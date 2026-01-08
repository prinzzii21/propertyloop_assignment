"""
Data loading and preprocessing module.
Handles loading CSV files and converting rows to documents.
"""

import os
import pandas as pd
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Document:
    """Represents a document created from a CSV row."""
    content: str
    metadata: Dict[str, any]


class DataLoader:
    """Loads and manages CSV data for the RAG pipeline."""
    
    def __init__(self, holdings_path: str, trades_path: str):
        self.holdings_path = holdings_path
        self.trades_path = trades_path
        self.holdings_df: pd.DataFrame = None
        self.trades_df: pd.DataFrame = None
        self.documents: List[Document] = []
        
    def validate_files(self) -> Tuple[bool, str]:
        """Validate that both CSV files exist."""
        if not os.path.exists(self.holdings_path):
            return False, f"Holdings file not found: {self.holdings_path}"
        if not os.path.exists(self.trades_path):
            return False, f"Trades file not found: {self.trades_path}"
        return True, "Files validated successfully"
    
    def load_data(self) -> Tuple[bool, str]:
        """Load CSV files into DataFrames."""
        valid, msg = self.validate_files()
        if not valid:
            return False, msg
        
        try:
            self.holdings_df = pd.read_csv(self.holdings_path)
            self.trades_df = pd.read_csv(self.trades_path)
            return True, f"Loaded {len(self.holdings_df)} holdings, {len(self.trades_df)} trades"
        except Exception as e:
            return False, f"Error loading CSV files: {str(e)}"
    
    def _row_to_document(self, row: pd.Series, file_name: str, row_index: int) -> Document:
        """Convert a DataFrame row to a Document."""
        # Create content string with all column=value pairs
        pairs = [f"{col}={row[col]}" for col in row.index if pd.notna(row[col])]
        content = f"FILE: {file_name} | ROW: {row_index} | " + " | ".join(pairs)
        
        metadata = {
            "file": file_name,
            "row_index": row_index,
        }
        
        return Document(content=content, metadata=metadata)
    
    def create_documents(self) -> List[Document]:
        """Convert all CSV rows to documents."""
        self.documents = []
        
        # Process holdings
        if self.holdings_df is not None:
            for idx, row in self.holdings_df.iterrows():
                doc = self._row_to_document(row, "holdings.csv", idx)
                self.documents.append(doc)
        
        # Process trades
        if self.trades_df is not None:
            for idx, row in self.trades_df.iterrows():
                doc = self._row_to_document(row, "trades.csv", idx)
                self.documents.append(doc)
        
        return self.documents
    
    def get_dataframe(self, file_name: str) -> pd.DataFrame:
        """Get the DataFrame for a specific file."""
        if "holdings" in file_name.lower():
            return self.holdings_df
        elif "trades" in file_name.lower():
            return self.trades_df
        return None
