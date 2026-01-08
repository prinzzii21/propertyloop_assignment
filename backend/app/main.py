"""
FastAPI backend for Financial Data RAG Chat.
"""

import os
import uuid
from typing import Dict, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .schemas import ChatRequest, ChatResponse, HealthResponse, Source
from .data import DataLoader
from .rag import RAGPipeline


# Load environment variables
load_dotenv()

# Configuration
HOLDINGS_PATH = os.getenv("HOLDINGS_CSV", "dataset/holdings.csv")
TRADES_PATH = os.getenv("TRADES_CSV", "dataset/trades.csv")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "10"))

# Global state
rag_pipeline: RAGPipeline = None
session_histories: Dict[str, List[Dict]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    global rag_pipeline
    
    print("=" * 50)
    print("Starting Financial Data RAG API")
    print("=" * 50)
    
    # Initialize data loader
    data_loader = DataLoader(HOLDINGS_PATH, TRADES_PATH)
    
    # Validate and load data
    success, msg = data_loader.load_data()
    if not success:
        print(f"ERROR: {msg}")
        print("Please ensure CSV files exist at the specified paths:")
        print(f"  - {HOLDINGS_PATH}")
        print(f"  - {TRADES_PATH}")
        raise RuntimeError(msg)
    
    print(f"✓ {msg}")
    
    # Initialize RAG pipeline
    rag_pipeline = RAGPipeline(
        data_loader=data_loader,
        embedding_model=EMBEDDING_MODEL,
        llm_model=LLM_MODEL,
        hf_token=HF_TOKEN
    )
    
    success, msg = rag_pipeline.initialize()
    if not success:
        print(f"ERROR: {msg}")
        raise RuntimeError(msg)
    
    print(f"✓ {msg}")
    print("=" * 50)
    print("API ready at http://localhost:8000")
    print("=" * 50)
    
    yield
    
    # Cleanup
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Financial Data RAG API",
    description="Chat API grounded in holdings.csv and trades.csv",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for RAG-based Q&A.
    
    Accepts questions about holdings and trades data.
    Supports aggregation queries (totals, averages, top-N, etc.)
    """
    global rag_pipeline, session_histories
    
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get chat history for session
    if session_id not in session_histories:
        session_histories[session_id] = []
    
    chat_history = session_histories[session_id]
    
    # Add user message to history
    chat_history.append({"role": "user", "content": request.message})
    
    try:
        # Query RAG pipeline
        answer, sources = rag_pipeline.query(
            question=request.message,
            top_k=request.top_k,
            chat_history=chat_history
        )
        
        # Add assistant response to history
        chat_history.append({"role": "assistant", "content": answer})
        
        # Trim history if too long
        if len(chat_history) > MAX_HISTORY * 2:
            session_histories[session_id] = chat_history[-(MAX_HISTORY * 2):]
        
        return ChatResponse(
            session_id=session_id,
            answer=answer,
            sources=[Source(**s) for s in sources]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Financial Data RAG API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /chat"
        }
    }
