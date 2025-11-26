"""Endpoints for user management."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.api.schemas.users import UserCreate, UserList, UserPublic, UserRead, UserUpdate
from app.db.models.user import User
from app.services.users import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserList)
def list_users(service: UserService = Depends(get_user_service)) -> UserList:
    """List active users."""
    return service.list()


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> UserRead:
    """Get a user by identifier."""
    try:
        return service.get(user_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate, service: UserService = Depends(get_user_service)
) -> UserRead:
    """Create a new user."""
    return service.create(payload)


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
