import uuid
from datetime import datetime
from pydantic import BaseModel


class BBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class OnionResponse(BaseModel):
    id: uuid.UUID
    batch_id: uuid.UUID
    bbox: dict | None = None
    size_mm: float | None = None
    shape_score: float | None = None
    color_uniformity: float | None = None
    predicted_grade: str | None = None
    defect_tags: list[str] = []
    confidence: float | None = None
    final_grade: str | None = None
    override_reason: str | None = None

    class Config:
        from_attributes = True


class OverrideRequest(BaseModel):
    final_grade: str
    override_reason: str
