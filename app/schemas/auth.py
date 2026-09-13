import uuid
from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    centre_id: uuid.UUID | None = None
    role: str = "operator"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: str
    centre_id: uuid.UUID | None = None

    class Config:
        from_attributes = True
