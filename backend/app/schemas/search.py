from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class SearchRequest(BaseModel):
    query: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: List[str] = []

class SearchResponse(BaseModel):
    id: UUID
    name: str
    notes: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    distance: float

    class Config:
        from_attributes = True