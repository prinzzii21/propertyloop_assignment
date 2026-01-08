from pydantic import BaseModel, Field
from typing import Optional, List


class Source(BaseModel):
    """Represents a source document from the CSV files."""
    file: str
    row_index: int


class ChatRequest(BaseModel):
    """Request model for the /chat endpoint."""
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class ChatResponse(BaseModel):
    """Response model for the /chat endpoint."""
    session_id: str
    answer: str
    sources: List[Source]


class HealthResponse(BaseModel):
    """Response model for the /health endpoint."""
    status: str
