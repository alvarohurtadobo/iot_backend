"""Authentication router."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.auth import LoginRequest, Token
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.base import get_db
from app.db.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
) -> Token:
    """Authenticate user and return access token."""
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is deleted
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )
    
    return Token(access_token=access_token, token_type="bearer")

