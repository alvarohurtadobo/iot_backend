"""Endpoints for role management."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.roles import RoleCreate, RoleList, RoleRead, RoleUpdate
from app.services.roles import RoleService, get_role_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=RoleList)
def list_roles(service: RoleService = Depends(get_role_service)) -> RoleList:
    """List available roles."""
    try:
        result = service.list()
        logger.info(f"Listed roles: total={result.total}")
        return result
    except Exception as e:
        logger.exception("Error listing roles")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing roles",
        ) from e


@router.get("/{role_id}", response_model=RoleRead)
def get_role(role_id: UUID, service: RoleService = Depends(get_role_service)) -> RoleRead:
    """Get a role by identifier."""
    try:
        role = service.get(role_id)
        logger.info(f"Role retrieved: role_id={role_id}, name={role.name}")
        return role
    except KeyError as exc:  # pragma: no cover - simple flow
        logger.warning(f"Role not found: role_id={role_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        ) from exc
    except Exception as e:
        logger.exception(f"Error retrieving role: role_id={role_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving role",
        ) from e


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate, service: RoleService = Depends(get_role_service)
) -> RoleRead:
    """Create a new role."""
    try:
        role = service.create(payload)
        logger.info(f"Role created: role_id={role.id}, name={payload.name}")
        return role
    except Exception as e:
        logger.exception(f"Error creating role: name={payload.name}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating role",
        ) from e


@router.put("/{role_id}", response_model=RoleRead)
def update_role(
    role_id: UUID, payload: RoleUpdate, service: RoleService = Depends(get_role_service)
) -> RoleRead:
    """Update an existing role."""
    try:
        role = service.update(role_id, payload)
        logger.info(f"Role updated: role_id={role_id}, name={role.name}")
        return role
    except KeyError as exc:
        logger.warning(f"Role not found for update: role_id={role_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        ) from exc
    except Exception as e:
        logger.exception(f"Error updating role: role_id={role_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating role",
        ) from e


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: UUID, service: RoleService = Depends(get_role_service)) -> None:
    """Delete a role."""
    try:
        service.delete(role_id)
        logger.info(f"Role deleted: role_id={role_id}")
    except KeyError as exc:
        logger.warning(f"Role not found for deletion: role_id={role_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        ) from exc
    except Exception as e:
        logger.exception(f"Error deleting role: role_id={role_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting role",
        ) from e
