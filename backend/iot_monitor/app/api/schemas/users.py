"""Esquemas de datos para Usuarios."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Campos comunes del usuario."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role_id: Optional[UUID] = None


class UserCreate(UserBase):
    """Payload para crear un usuario."""

    id: UUID = Field(default_factory=uuid4)
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Payload para actualizar un usuario."""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role_id: Optional[UUID] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)

    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        """Evitar campos nulos en actualizaciones parciales."""
        data = super().model_dump(*args, **kwargs)
        return {key: value for key, value in data.items() if value is not None}


class UserRead(UserBase):
    """Respuesta estándar de un usuario."""

    id: UUID
    password_hash: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class UserList(BaseModel):
    """Listado de usuarios."""

    items: list[UserRead]
    total: int
