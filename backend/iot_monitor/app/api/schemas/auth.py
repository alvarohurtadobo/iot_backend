"""Schemas for authentication."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class TokenData(BaseModel):
    """Token data schema."""

    user_id: str | None = None
    email: str | None = None

