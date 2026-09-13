import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Onion(Base):
    __tablename__ = "onions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=False)

    bbox = Column(JSON, nullable=True)  # {x, y, width, height} in pixels
    size_mm = Column(Float, nullable=True)
    shape_score = Column(Float, nullable=True)  # 0-1 roundness/eccentricity
    color_uniformity = Column(Float, nullable=True)  # 0-1

    predicted_grade = Column(String, nullable=True)  # A / B / C
    defect_tags = Column(JSON, default=list)  # ["sprouting", "rot", ...]
    confidence = Column(Float, nullable=True)  # 0-1

    final_grade = Column(String, nullable=True)  # after any human override
    overridden_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    override_reason = Column(String, nullable=True)
    overridden_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("Batch", back_populates="onions")
