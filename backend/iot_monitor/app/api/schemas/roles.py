"""Data schemas for Roles."""

from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """Shared fields in Role representations."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class RoleCreate(RoleBase):
    """Payload to create a new role."""

    id: UUID = Field(default_factory=uuid4)


class RoleUpdate(BaseModel):
    """Payload to update an existing role."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)

    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        """Avoid returning empty fields to the service."""
        data = super().model_dump(*args, **kwargs)
        return {key: value for key, value in data.items() if value is not None}


class RoleRead(RoleBase):
    """Standard Role response."""

    id: UUID


class RoleList(BaseModel):
    """Simple paginated list of roles."""

    items: list[RoleRead]
    total: int
