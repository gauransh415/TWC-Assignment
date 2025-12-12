from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class OrganizationModel(BaseModel):
    """Database model for organizations stored in master database."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    organization_name: str
    collection_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class CreateOrganizationRequest(BaseModel):
    """Request schema for creating an organization."""

    organization_name: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=8)


class GetOrganizationRequest(BaseModel):
    """Request schema for getting an organization."""

    organization_name: str


class UpdateOrganizationRequest(BaseModel):
    """Request schema for updating an organization."""

    organization_name: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(
        None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    password: Optional[str] = Field(None, min_length=8)


class DeleteOrganizationRequest(BaseModel):
    """Request schema for deleting an organization."""

    organization_name: str


class OrganizationResponse(BaseModel):
    """Response schema for organization operations."""

    organization_id: str
    organization_name: str
    collection_name: str
    created_at: str
    admin_email: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
