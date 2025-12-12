from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
from src.models.organization import PyObjectId


class AdminUserModel(BaseModel):
    """Database model for admin users stored in master database."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: str
    password_hash: str
    organization_id: PyObjectId
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class LoginRequest(BaseModel):
    """Request schema for admin login."""

    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    """Response schema for successful authentication."""

    access_token: str
    token_type: str = "bearer"
    admin_id: str
    organization_id: str
    email: str
    expires_in: int  # in seconds


class AdminResponse(BaseModel):
    """Response schema for admin user operations."""

    admin_id: str
    email: str
    organization_id: str
    created_at: str

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
