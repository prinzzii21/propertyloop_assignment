"""
RAG (Retrieval-Augmented Generation) pipeline module.
Handles embeddings, vector store, and LLM generation.
"""

import os
import re
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
import faiss

from .data import Document, DataLoader


class RAGPipeline:
    """RAG pipeline for document retrieval and answer generation."""
    
    def __init__(
        self,
        data_loader: DataLoader,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_model: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        hf_token: Optional[str] = None
    ):
        self.data_loader = data_loader
        self.embedding_model_name = embedding_model
        self.llm_model_name = llm_model
        self.hf_token = hf_token
        
        self.embedder: SentenceTransformer = None
        self.llm = None
        self.index: faiss.IndexFlatL2 = None
        self.documents: List[Document] = []
        
    def initialize(self) -> Tuple[bool, str]:
        """Initialize the RAG pipeline components."""
        try:
            # Load embedding model
            print(f"Loading embedding model: {self.embedding_model_name}")
            self.embedder = SentenceTransformer(self.embedding_model_name)
            
            # Load LLM
            print(f"Loading LLM: {self.llm_model_name}")
            from transformers import pipeline
            
            self.llm = pipeline(
                "text-generation",
                model=self.llm_model_name,
                token=self.hf_token,
                device_map="auto",
                torch_dtype="auto",
                max_new_tokens=512,
            )
            
            # Create documents and build index
            self.documents = self.data_loader.create_documents()
            self._build_index()
            
            return True, f"RAG pipeline initialized with {len(self.documents)} documents"
            
        except Exception as e:
            return False, f"Error initializing RAG pipeline: {str(e)}"
    
    def _build_index(self):
        """Build FAISS index from documents."""
        if not self.documents:
            return
            
        # Create embeddings
        texts = [doc.content for doc in self.documents]
        embeddings = self.embedder.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype(np.float32))
        
        print(f"Built FAISS index with {self.index.ntotal} vectors")
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """Retrieve top-k relevant documents for a query."""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Encode query
        query_embedding = self.embedder.encode([query])
        
        # Search
        distances, indices = self.index.search(
            query_embedding.astype(np.float32), 
            min(top_k, self.index.ntotal)
        )
        
        # Return documents
        return [self.documents[i] for i in indices[0] if i < len(self.documents)]
    
    def _is_aggregation_query(self, query: str) -> bool:
        """Check if query requires pandas aggregation."""
        agg_keywords = [
            "total", "sum", "average", "avg", "mean", "count", "how many",
            "top", "bottom", "highest", "lowest", "max", "min", "group",
            "net", "aggregate", "calculate", "compute"
        ]
        query_lower = query.lower()
        return any(kw in query_lower for kw in agg_keywords)
    
    def _handle_aggregation(self, query: str) -> Tuple[Optional[str], List[Dict]]:
        """Handle aggregation queries using pandas."""
        query_lower = query.lower()
        sources = []
        
        holdings_df = self.data_loader.holdings_df
        trades_df = self.data_loader.trades_df
        
        try:
            # Top holdings by value
            if "top" in query_lower and "holding" in query_lower:
                if "value" in holdings_df.columns:
                    n = 5  # default
                    match = re.search(r'top\s+(\d+)', query_lower)
                    if match:
                        n = int(match.group(1))
                    result = holdings_df.nlargest(n, "value")[["symbol" if "symbol" in holdings_df.columns else holdings_df.columns[0], "value"]]
                    sources = [{"file": "holdings.csv", "row_index": int(i)} for i in result.index]
                    return f"Top {n} holdings by value:\n{result.to_string(index=False)}", sources
            
            # Total PnL
            if "total" in query_lower and "pnl" in query_lower:
                pnl_col = None
                for col in trades_df.columns:
                    if "pnl" in col.lower() or "profit" in col.lower():
                        pnl_col = col
                        break
                if pnl_col:
                    total = trades_df[pnl_col].sum()
                    sources = [{"file": "trades.csv", "row_index": int(i)} for i in trades_df.index[:10]]
                    return f"Total PnL: {total:,.2f} (computed from {len(trades_df)} trades)", sources
            
            # Net position
            if "net" in query_lower and "position" in query_lower:
                symbol_match = re.search(r'(?:in|for)\s+([A-Z]{1,5})', query.upper())
                if symbol_match and "symbol" in trades_df.columns:
                    symbol = symbol_match.group(1)
                    filtered = trades_df[trades_df["symbol"].str.upper() == symbol]
                    if not filtered.empty and "quantity" in filtered.columns:
                        net = filtered["quantity"].sum()
                        sources = [{"file": "trades.csv", "row_index": int(i)} for i in filtered.index]
                        return f"Net position in {symbol}: {net:,.0f} shares", sources
            
            # Count trades
            if "how many" in query_lower and "trade" in query_lower:
                count = len(trades_df)
                return f"Total number of trades: {count}", [{"file": "trades.csv", "row_index": 0}]
            
            # Average price
            if ("average" in query_lower or "avg" in query_lower) and "price" in query_lower:
                price_col = None
                for col in trades_df.columns:
                    if "price" in col.lower():
                        price_col = col
                        break
                if price_col:
                    avg = trades_df[price_col].mean()
                    return f"Average trade price: ${avg:,.2f}", [{"file": "trades.csv", "row_index": 0}]
            
        except Exception as e:
            print(f"Aggregation error: {e}")
        
        return None, []
    
    def generate_answer(
        self, 
        query: str, 
        context_docs: List[Document],
        chat_history: List[Dict] = None
    ) -> str:
        """Generate an answer using the LLM."""
        
        # Build context from retrieved documents
        context = "\n".join([doc.content for doc in context_docs])
        
        # Build chat history context
        history_text = ""
        if chat_history:
            for msg in chat_history[-6:]:  # Last 3 turns
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"{role.upper()}: {content}\n"
        
        # Create prompt
        prompt = f"""<s>[INST] <<SYS>>
You are a helpful financial data assistant. Answer questions ONLY based on the provided data context.
Rules:
1. Only use information from the CONTEXT below
2. If the answer is not in the context, say "I don't know based on the data"
3. Never invent or guess numbers
4. Be concise and specific
5. Reference specific rows when possible
<</SYS>>

CONTEXT:
{context}

{f"CHAT HISTORY:{chr(10)}{history_text}" if history_text else ""}

USER QUESTION: {query}
[/INST]"""

        # Generate response
        try:
            result = self.llm(prompt, do_sample=True, temperature=0.3)
            answer = result[0]["generated_text"]
            
            # Extract just the assistant's response
            if "[/INST]" in answer:
                answer = answer.split("[/INST]")[-1].strip()
            
            return answer
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def query(
        self, 
        question: str, 
        top_k: int = 5,
        chat_history: List[Dict] = None
    ) -> Tuple[str, List[Dict]]:
        """Main query method - handles both retrieval and aggregation."""
        
        # Check for aggregation queries first
        if self._is_aggregation_query(question):
            agg_result, agg_sources = self._handle_aggregation(question)
            if agg_result:
                return agg_result, agg_sources
        
        # Standard RAG retrieval
        retrieved_docs = self.retrieve(question, top_k)
        
        if not retrieved_docs:
            return "I don't have any relevant data to answer this question.", []
        
        # Generate answer
        answer = self.generate_answer(question, retrieved_docs, chat_history)
        
        # Extract sources
        sources = [
            {"file": doc.metadata["file"], "row_index": doc.metadata["row_index"]}
            for doc in retrieved_docs
        ]
        
        return answer, sources
