from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy import cast
from pgvector.sqlalchemy import Vector
from app.database import get_db
from app.models.record import Record
from app.models.tag import Tag, RecordTag
from app.schemas.search import SearchRequest, SearchResponse
from app.services.embedding import get_embedding
from app.utils.security import get_current_user
from uuid import UUID
from typing import List

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/", response_model=List[SearchResponse])
async def search_records(
    request: SearchRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    query_embedding = await get_embedding(request.query)
    if not query_embedding:
        raise HTTPException(status_code=500, detail="Failed to compute query embedding")

    query = (
        db.query(
            Record,
            Record.embedding.l2_distance(query_embedding).label("distance")
        )
        .join(RecordTag, Record.id == RecordTag.record_id, isouter=True)
        .join(Tag, RecordTag.tag_id == Tag.id, isouter=True)
        .filter(Record.user_id == str(user_id))
    )

    if request.start_date:
        query = query.filter(Record.created_at >= request.start_date)

    if request.end_date:
        query = query.filter(Record.created_at <= request.end_date)

    if request.tags:
        query = query.filter(Tag.name.ilike_any([f"{tag}%" for tag in request.tags]))

    query = query.order_by("distance").limit(10)

    result = query.all()
    records = [
        SearchResponse(
            id=r.Record.id,
            name=r.Record.name,
            notes=r.Record.notes,
            tags=[tag.name for tag in r.Record.tags],
            created_at=r.Record.created_at,
            updated_at=r.Record.updated_at,
            distance=r.distance
        )
        for r in result
    ]
    return records

# Example Request (POST /search):
# {
#   "query": "AI conference",
#   "start_date": "2025-01-01T00:00:00Z",
#   "end_date": "2025-12-31T23:59:59Z",
#   "tags": ["conference", "AI"]
# }
#
# Example Response:
# [
#   {
#     "id": "123e4567-e89b-12d3-a456-426614174000",
#     "name": "John Doe",
#     "notes": "Met at conference, works in AI",
#     "created_at": "2025-09-25T14:17:00Z",
#     "updated_at": "2025-09-25T14:17:00Z",
#     "distance": 0.123
#   }
# ]