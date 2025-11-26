"""Endpoints for role management."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.roles import RoleCreate, RoleList, RoleRead, RoleUpdate
from app.services.roles import RoleService, get_role_service

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=RoleList)
def list_roles(service: RoleService = Depends(get_role_service)) -> RoleList:
    """List available roles."""
    return service.list()


@router.get("/{role_id}", response_model=RoleRead)
def get_role(role_id: UUID, service: RoleService = Depends(get_role_service)) -> RoleRead:
    """Get a role by identifier."""
    try:
        return service.get(role_id)
    except KeyError as exc:  # pragma: no cover - simple flow
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        ) from exc


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate, service: RoleService = Depends(get_role_service)
) -> RoleRead:
    """Create a new role."""
    return service.create(payload)


@router.put("/{role_id}", response_model=RoleRead)
def update_role(
    role_id: UUID, payload: RoleUpdate, service: RoleService = Depends(get_role_service)
) -> RoleRead:
    """Update an existing role."""
    try:
        return service.update(role_id, payload)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        ) from exc


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: UUID, service: RoleService = Depends(get_role_service)) -> None:
    """Delete a role."""
    try:
        service.delete(role_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        ) from exc
