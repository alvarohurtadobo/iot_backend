"""Rate limiting utilities."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, Request, status

from app.core.config import settings

# Simple in-memory rate limiter (consider Redis for production)
_rate_limit_store: dict[str, list[datetime]] = defaultdict(list)


def check_rate_limit(request: Request, key: str | None = None) -> None:
    """
    Check if request exceeds rate limit.
    Raises HTTPException if rate limit exceeded.
    """
    if key is None:
        # Use IP address as default key
        client_host = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_host}"
    
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=1)
    
    # Clean old entries
    _rate_limit_store[key] = [
        timestamp for timestamp in _rate_limit_store[key]
        if timestamp > window_start
    ]
    
    # Check limit
    if len(_rate_limit_store[key]) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": "60"},
        )
    
    # Record this request
    _rate_limit_store[key].append(now)


def clear_rate_limit(key: str) -> None:
    """Clear rate limit for a specific key."""
    if key in _rate_limit_store:
        del _rate_limit_store[key]
