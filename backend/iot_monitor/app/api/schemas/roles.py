"""Esquemas de datos para Roles."""

from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """Campos compartidos en las representaciones de Role."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class RoleCreate(RoleBase):
    """Payload para crear un nuevo role."""

    id: UUID = Field(default_factory=uuid4)


class RoleUpdate(BaseModel):
    """Payload para actualizar un role existente."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)

    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        """Evitar retornar campos vacíos al servicio."""
        data = super().model_dump(*args, **kwargs)
        return {key: value for key, value in data.items() if value is not None}


class RoleRead(RoleBase):
    """Respuesta estándar de Role."""

    id: UUID


class RoleList(BaseModel):
    """Listado paginado simple de roles."""

    items: list[RoleRead]
    total: int
