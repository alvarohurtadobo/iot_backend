"""Endpoints for user management."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.api.schemas.users import UserCreate, UserList, UserPublic, UserRead, UserUpdate
from app.db.models.user import User
from app.services.users import UserService, get_user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserList)
def list_users(service: UserService = Depends(get_user_service)) -> UserList:
    """List active users."""
    try:
        result = service.list()
        logger.info(f"Listed users: total={result.total}")
        return result
    except Exception as e:
        logger.exception("Error listing users")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar usuarios",
        ) from e


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> UserRead:
    """Get a user by identifier."""
    try:
        user = service.get(user_id)
        logger.info(f"User retrieved: user_id={user_id}")
        return user
    except KeyError as exc:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc
    except Exception as e:
        logger.exception(f"Error retrieving user: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener usuario",
        ) from e


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate, service: UserService = Depends(get_user_service)
) -> UserRead:
    """Create a new user."""
    try:
        user = service.create(payload)
        logger.info(
            f"User created: user_id={user.id}, email={payload.email}, "
            f"role_id={payload.role_id}"
        )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating user: email={payload.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear usuario",
        ) from e


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID, payload: UserUpdate, service: UserService = Depends(get_user_service)
) -> UserRead:
    """Update user information."""
    try:
        return service.update(user_id, payload)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> None:
    """Logically delete a user."""
    try:
        service.delete(user_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc


@router.get("/me", response_model=UserPublic)
def get_current_user_info(current_user: User = Depends(get_current_user)) -> UserPublic:
    """Get information about the current authenticated user."""
    return UserPublic(
        id=current_user.id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        role_id=current_user.role_id,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
