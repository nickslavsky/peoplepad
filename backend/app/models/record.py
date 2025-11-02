from sqlalchemy import Index, Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Record(Base):
    __tablename__ = "records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    all_mpnet_base_v2_embedding = Column(Vector(768), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_records_all_mpnet_base_v2_embedding', 'all_mpnet_base_v2_embedding', postgresql_using='hnsw',
              postgresql_ops={'all_mpnet_base_v2_embedding': 'vector_cos_ops'}),
    )
    # Add relationship to fetch tags
    tags = relationship(
        "Tag",
        secondary="record_tags",
        back_populates="records",
        lazy="joined"  # Eagerly load tags to avoid N+1 queries
    )