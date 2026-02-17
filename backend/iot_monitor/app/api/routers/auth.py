"""Authentication router."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.schemas.auth import LoginRequest, RefreshTokenRequest, Token
from app.core.config import settings
from app.core.rate_limit import check_rate_limit
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from app.db.base import get_db
from app.db.models.login_audit import LoginAudit
from app.db.models.revoked_token import RevokedToken
from app.db.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


def _is_account_locked(user: User) -> bool:
    """Check if user account is locked."""
    if user.locked_until is None:
        return False
    return datetime.now(timezone.utc) < user.locked_until


def _lock_account(user: User, db: Session) -> None:
    """Lock user account for configured duration."""
    lock_until = datetime.now(timezone.utc) + timedelta(
        minutes=settings.account_lockout_minutes
    )
    user.locked_until = lock_until
    user.failed_login_attempts = str(settings.max_login_attempts)
    db.commit()


def _increment_failed_attempts(user: User, db: Session) -> None:
    """Increment failed login attempts and lock if threshold reached."""
    try:
        attempts = int(user.failed_login_attempts or "0")
    except ValueError:
        attempts = 0
    
    attempts += 1
    user.failed_login_attempts = str(attempts)
    
    if attempts >= settings.max_login_attempts:
        _lock_account(user, db)
    else:
        db.commit()


def _reset_failed_attempts(user: User, db: Session) -> None:
    """Reset failed login attempts on successful login."""
    user.failed_login_attempts = "0"
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()


def _log_login_attempt(
    db: Session,
    user_id: uuid.UUID | None,
    email: str,
    ip_address: str | None,
    user_agent: str | None,
    success: bool,
    failure_reason: str | None = None,
) -> None:
    """Log login attempt for audit purposes."""
    audit = LoginAudit(
        user_id=user_id,
        email=email,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        failure_reason=failure_reason,
    )
    db.add(audit)
    db.commit()


def _get_client_info(request: Request) -> tuple[str | None, str | None]:
    """Extract client IP and user agent from request."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> Token:
    """Authenticate user to return access and refresh tokens."""
    # Rate limiting
    check_rate_limit(request, key=f"login:{login_data.email}")
    
    ip_address, user_agent = _get_client_info(request)
    
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    # Log attempt even if user doesn't exist (security best practice)
    if not user:
        logger.warning(
            f"Login attempt failed - user not found: email={login_data.email}, "
            f"ip={ip_address}"
        )
        _log_login_attempt(
            db=db,
            user_id=None,
            email=login_data.email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="User not found",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is deleted
    if user.deleted_at is not None:
        logger.warning(
            f"Login attempt failed - account disabled: user_id={user.id}, "
            f"email={login_data.email}, ip={ip_address}"
        )
        _log_login_attempt(
            db=db,
            user_id=user.id,
            email=login_data.email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="Account disabled",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is locked
    if _is_account_locked(user):
        logger.warning(
            f"Login attempt failed - account locked: user_id={user.id}, "
            f"email={login_data.email}, ip={ip_address}, "
            f"locked_until={user.locked_until}"
        )
        _log_login_attempt(
            db=db,
            user_id=user.id,
            email=login_data.email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="Account locked",
        )
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked. Try again after {settings.account_lockout_minutes} minutes.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password):
        _increment_failed_attempts(user, db)
        logger.warning(
            f"Login attempt failed - incorrect password: user_id={user.id}, "
            f"email={login_data.email}, ip={ip_address}, "
            f"failed_attempts={user.failed_login_attempts}"
        )
        _log_login_attempt(
            db=db,
            user_id=user.id,
            email=login_data.email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="Incorrect password",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Successful login
    _reset_failed_attempts(user, db)
    _log_login_attempt(
        db=db,
        user_id=user.id,
        email=login_data.email,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True,
    )
    
    logger.info(
        f"Login successful: user_id={user.id}, email={login_data.email}, "
        f"ip={ip_address}"
    )
    
    # Generate JWT IDs for token revocation
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "jti": access_jti,
            "type": "access",
        },
        expires_delta=access_token_expires,
    )
    
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "jti": refresh_jti,
        },
        expires_delta=refresh_token_expires,
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> Token:
    """Refresh access token using refresh token."""
    try:
        payload = decode_refresh_token(refresh_data.refresh_token)
    except ValueError as exc:
        logger.warning(f"Token refresh failed - invalid token: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    
    # Check if token is revoked
    jti = payload.get("jti")
    if jti:
        revoked = (
            db.query(RevokedToken)
            .filter(RevokedToken.jti == jti)
            .first()
        )
        if revoked:
            logger.warning(f"Token refresh failed - revoked token: jti={jti}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Get user
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.deleted_at is not None:
        logger.warning(
            f"Token refresh failed - user not found or disabled: user_id={user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate new tokens
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "jti": access_jti,
            "type": "access",
        },
        expires_delta=access_token_expires,
    )
    
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "jti": refresh_jti,
        },
        expires_delta=refresh_token_expires,
    )
    
    # Revoke old refresh token
    if jti:
        try:
            expires_at = datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc)
            revoked_token = RevokedToken(
                jti=jti,
                token=refresh_data.refresh_token,
                expires_at=expires_at,
            )
            db.add(revoked_token)
            db.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error revoking old token: jti={jti}, error={str(e)}")
            db.rollback()
    
    logger.info(f"Token refreshed successfully: user_id={user.id}, email={user.email}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Revoke refresh token (logout)."""
    try:
        payload = decode_refresh_token(refresh_data.refresh_token)
    except ValueError:
        # Token already invalid, consider it logged out
        logger.debug("Logout attempted with invalid token (already logged out)")
        return {"message": "Sesión cerrada exitosamente"}
    
    jti = payload.get("jti")
    user_id = payload.get("sub")
    
    if jti:
        try:
            # Check if already revoked
            existing = (
                db.query(RevokedToken)
                .filter(RevokedToken.jti == jti)
                .first()
            )
            if not existing:
                expires_at = datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc)
                revoked_token = RevokedToken(
                    jti=jti,
                    token=refresh_data.refresh_token,
                    expires_at=expires_at,
                )
                db.add(revoked_token)
                db.commit()
                logger.info(f"User logged out successfully: user_id={user_id}, jti={jti}")
            else:
                logger.debug(f"Token already revoked: jti={jti}")
        except SQLAlchemyError as e:
            logger.error(f"Error during logout: jti={jti}, error={str(e)}")
            db.rollback()
    
    return {"message": "Sesión cerrada exitosamente"}

