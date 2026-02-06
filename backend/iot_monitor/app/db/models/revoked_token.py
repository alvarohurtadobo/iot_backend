"""Revoked token model for token blacklisting."""

from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.sql import func
import uuid

from app.db.base import Base, UUID


class RevokedToken(Base):
    """Revoked token model for tracking invalidated tokens."""

    __tablename__ = "revoked_tokens"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    jti = Column(String(255), nullable=False, unique=True, index=True)  # JWT ID
    token = Column(String(500), nullable=False)  # Full token for verification
    revoked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        Index("idx_revoked_token_jti", "jti"),
    )

    def __repr__(self):
        return f"<RevokedToken(id={self.id}, jti={self.jti[:10]}...)>"
