from sqlalchemy.orm import Session
from app.models.record import Record
from app.services.embedding import get_embedding
import logging
from typing import List

logger = logging.getLogger(__name__)


async def compute_embedding(record_id: str, notes: str, db: Session):
    try:
        # Combine text for embedding
        embedding = await get_embedding(notes)
        # Update record with embedding
        db_record = db.query(Record).filter(Record.id == record_id).first()
        if db_record:
            db_record.all_mpnet_base_v2_embedding = embedding
            db.commit()
            logger.info(f"Embedding updated for record {record_id}")
        else:
            logger.error(f"Record {record_id} not found for embedding update")
    except Exception as e:
        logger.error(f"Failed to compute embedding for record {record_id}: {str(e)}")