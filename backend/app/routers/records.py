from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.record import Record
from app.models.tag import Tag, RecordTag
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse
from app.tasks.embeddings import compute_embedding
from uuid import UUID
from app.utils.security import get_current_user
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/records",
                   tags=["records"],
                   dependencies=[Depends(get_current_user)])

@router.post("/", response_model=RecordResponse)
async def create_record(
    record: RecordCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    db_record = Record(user_id=user_id, name=record.name, notes=record.notes)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    # Handle tags
    for tag_name in record.tags:
        tag = db.query(Tag).filter(Tag.user_id == user_id, Tag.name == tag_name).first()
        if not tag:
            tag = Tag(user_id=user_id, name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        db.add(RecordTag(record_id=db_record.id, tag_id=tag.id))
    db.commit()

    # Launch async embedding task
    background_tasks.add_task(compute_embedding, db_record.id, record.notes, db)

    return db_record

@router.get("/{id}", response_model=RecordResponse)
async def get_record(id: UUID, db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user)):
    record = db.query(Record).filter(Record.id == id, Record.user_id == user_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.put("/{id}", response_model=RecordResponse)
async def update_record(
    id: UUID,
    record: RecordUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    db_record = db.query(Record).filter(Record.id == id, Record.user_id == user_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")

    db_record.name = record.name
    db_record.notes = record.notes

    # Update tags
    db.query(RecordTag).filter(RecordTag.record_id == id).delete()
    for tag_name in record.tags:
        tag = db.query(Tag).filter(Tag.user_id == user_id, Tag.name == tag_name).first()
        if not tag:
            tag = Tag(user_id=user_id, name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        db.add(RecordTag(record_id=db_record.id, tag_id=tag.id))

    db.commit()
    db.refresh(db_record)

    # Launch async embedding task
    background_tasks.add_task(compute_embedding, db_record.id, record.notes, db)

    return db_record

@router.delete("/{id}")
async def delete_record(id: UUID, db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user)):
    record = db.query(Record).filter(Record.id == id, Record.user_id == user_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Record deleted"}

# Example Request (POST /records):
# {
#   "name": "John Doe",
#   "notes": "Met at conference, works in AI",
#   "tags": ["conference", "AI"]
# }
#
# Example Response:
# {
#   "id": "123e4567-e89b-12d3-a456-426614174000",
#   "user_id": "456e7890-e12b-34d5-a678-426614174000",
#   "name": "John Doe",
#   "notes": "Met at conference, works in AI",
#   "tags": ["conference", "AI"],
#   "created_at": "2025-09-25T14:17:00Z",
#   "updated_at": "2025-09-25T14:17:00Z"
# }