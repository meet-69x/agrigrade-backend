import uuid
from datetime import datetime
from pydantic import BaseModel


class CentreCreate(BaseModel):
    name: str
    location: str | None = None


class CentreResponse(BaseModel):
    id: uuid.UUID
    name: str
    location: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
