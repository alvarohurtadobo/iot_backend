"""Endpoints para gestión de usuarios."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.users import UserCreate, UserList, UserRead, UserUpdate
from app.services.users import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserList)
def list_users(service: UserService = Depends(get_user_service)) -> UserList:
    """Listar usuarios activos."""
    return service.list()


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> UserRead:
    """Obtener un usuario por identificador."""
    try:
        return service.get(user_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        ) from exc


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate, service: UserService = Depends(get_user_service)
) -> UserRead:
    """Crear un nuevo usuario."""
    return service.create(payload)


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID, payload: UserUpdate, service: UserService = Depends(get_user_service)
) -> UserRead:
    """Actualizar información de un usuario."""
    try:
        return service.update(user_id, payload)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        ) from exc


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> None:
    """Eliminar lógicamente un usuario."""
    try:
        service.delete(user_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        ) from exc
