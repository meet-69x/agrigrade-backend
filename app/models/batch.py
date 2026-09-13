import uuid
from datetime import datetime
import enum

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class BatchStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Batch(Base):
    __tablename__ = "batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    centre_id = Column(UUID(as_uuid=True), ForeignKey("centres.id"), nullable=False)
    operator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    label = Column(String, nullable=True)  # e.g. user-given batch name/ID
    image_path = Column(String, nullable=True)
    status = Column(Enum(BatchStatus), default=BatchStatus.pending, nullable=False)

    onion_count = Column(Integer, default=0)
    avg_size_mm = Column(Float, nullable=True)
    overall_grade = Column(String, nullable=True)
    percent_defective = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    centre = relationship("Centre", back_populates="batches")
    operator = relationship("User", back_populates="batches")
    onions = relationship("Onion", back_populates="batch", cascade="all, delete-orphan")
