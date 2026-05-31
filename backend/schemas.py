from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: Optional[dict] = None


class Reference(BaseModel):
    title: str
    court: Optional[str] = None
    date: Optional[str] = None
    snippet: str
    full:str
    score: float
    source_url: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    reasoning_path: List[str]
    references: List[Reference]