from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.database import get_db
from app.utils.security import get_current_user
from app.models.tag import Tag
from app.schemas.tag import TagResponse

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/", response_model=List[TagResponse])
async def get_tags(db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user)):
    tags = db.query(Tag).filter(Tag.user_id == user_id).all()
    return tags