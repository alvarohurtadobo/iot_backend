"""Data schemas for Users."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Common user fields."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role_id: Optional[UUID] = None


class UserCreate(UserBase):
    """Payload to create a user."""

    id: UUID = Field(default_factory=uuid4)
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Payload to update a user."""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role_id: Optional[UUID] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)

    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        """Avoid null fields in partial updates."""
        data = super().model_dump(*args, **kwargs)
        return {key: value for key, value in data.items() if value is not None}


class UserRead(UserBase):
    """Standard user response."""

    id: UUID
    password_hash: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class UserPublic(UserBase):
    """Public user response (without sensitive information)."""

    id: UUID
    created_at: datetime
    updated_at: datetime


class UserList(BaseModel):
    """User list."""

    items: list[UserRead]
    total: int
