"""In-memory services for users."""

from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock
from typing import Dict
from uuid import UUID

from app.api.schemas.users import UserCreate, UserList, UserRead, UserUpdate
from app.core.security import get_password_hash


class UserService:
    """Temporary in-memory user management."""

    def __init__(self) -> None:
        self._storage: Dict[UUID, UserRead] = {}
        self._lock = RLock()

    def list(self) -> UserList:
        """Return active users."""
        with self._lock:
            items = [user for user in self._storage.values() if user.deleted_at is None]
        return UserList(items=items, total=len(items))

    def get(self, user_id: UUID) -> UserRead:
        """Get a user by id, if active."""
        with self._lock:
            user = self._storage.get(user_id)
        if user is None or user.deleted_at is not None:
            raise KeyError(str(user_id))
        return user

    def create(self, payload: UserCreate) -> UserRead:
        """Register a new user."""
        now = datetime.now(timezone.utc)
        user = UserRead(
            id=payload.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            role_id=payload.role_id,
            password_hash=get_password_hash(payload.password),
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )
        with self._lock:
            self._storage[user.id] = user
        return user

    def update(self, user_id: UUID, payload: UserUpdate) -> UserRead:
        """Update data for an existing user."""
        with self._lock:
            stored = self._storage.get(user_id)
            if stored is None or stored.deleted_at is not None:
                raise KeyError(str(user_id))

            update_data = payload.model_dump()
            if "password" in update_data:
                update_data["password_hash"] = get_password_hash(update_data.pop("password"))
            update_data["updated_at"] = datetime.now(timezone.utc)

            updated_user = stored.model_copy(update=update_data)
            self._storage[user_id] = updated_user
            return updated_user

    def delete(self, user_id: UUID) -> None:
        """Mark a user as deleted."""
        with self._lock:
            stored = self._storage.get(user_id)
            if stored is None or stored.deleted_at is not None:
                raise KeyError(str(user_id))
            self._storage[user_id] = stored.model_copy(
                update={"deleted_at": datetime.now(timezone.utc)}
            )


def get_user_service() -> UserService:
    """Get singleton instance of UserService."""

    if not hasattr(get_user_service, "_instance"):
        get_user_service._instance = UserService()  # type: ignore[attr-defined]
    return get_user_service._instance  # type: ignore[attr-defined]
