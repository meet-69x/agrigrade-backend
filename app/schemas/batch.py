import uuid
from datetime import datetime
from pydantic import BaseModel

from app.schemas.onion import OnionResponse


class BatchCreate(BaseModel):
    label: str | None = None
    centre_id: uuid.UUID


class BatchSummary(BaseModel):
    id: uuid.UUID
    label: str | None = None
    centre_id: uuid.UUID
    status: str
    onion_count: int
    avg_size_mm: float | None = None
    overall_grade: str | None = None
    percent_defective: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class BatchDetail(BatchSummary):
    image_path: str | None = None
    onions: list[OnionResponse] = []

    class Config:
        from_attributes = True
