import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    operator = "operator"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.operator, nullable=False)
    centre_id = Column(UUID(as_uuid=True), ForeignKey("centres.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    centre = relationship("Centre", back_populates="users")
    batches = relationship("Batch", back_populates="operator")
