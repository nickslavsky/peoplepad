from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)

    # Add relationship to records
    records = relationship(
        "Record",
        secondary="record_tags",
        back_populates="tags"
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='tags_user_id_name_key'),
    )

class RecordTag(Base):
    __tablename__ = "record_tags"

    record_id = Column(UUID(as_uuid=True), ForeignKey("records.id"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True)