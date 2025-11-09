"""Servicios en memoria para roles."""

from __future__ import annotations

from threading import RLock
from typing import Dict
from uuid import UUID

from app.api.schemas.roles import RoleCreate, RoleList, RoleRead, RoleUpdate


class RoleService:
    """Servicio simple para gestionar roles en memoria."""

    def __init__(self) -> None:
        self._storage: Dict[UUID, RoleRead] = {}
        self._lock = RLock()

    def list(self) -> RoleList:
        """Retornar todos los roles."""
        with self._lock:
            items = list(self._storage.values())
        return RoleList(items=items, total=len(items))

    def get(self, role_id: UUID) -> RoleRead:
        """Obtener un role por su identificador."""
        with self._lock:
            role = self._storage.get(role_id)
        if role is None:
            raise KeyError(str(role_id))
        return role

    def create(self, payload: RoleCreate) -> RoleRead:
        """Registrar un nuevo role."""
        data = RoleRead(**payload.model_dump())
        with self._lock:
            self._storage[data.id] = data
        return data

    def update(self, role_id: UUID, payload: RoleUpdate) -> RoleRead:
        """Actualizar un role existente."""
        with self._lock:
            stored = self._storage.get(role_id)
            if stored is None:
                raise KeyError(str(role_id))
            updated_data = stored.model_copy(update=payload.model_dump())
            self._storage[role_id] = updated_data
            return updated_data

    def delete(self, role_id: UUID) -> None:
        """Eliminar un role."""
        with self._lock:
            if role_id not in self._storage:
                raise KeyError(str(role_id))
            del self._storage[role_id]


def get_role_service() -> RoleService:
    """Obtener instancia singleton de RoleService."""

    if not hasattr(get_role_service, "_instance"):
        get_role_service._instance = RoleService()  # type: ignore[attr-defined]
    return get_role_service._instance  # type: ignore[attr-defined]
