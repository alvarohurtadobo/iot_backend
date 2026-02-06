"""Login audit model for tracking authentication attempts."""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base, UUID


class LoginAudit(Base):
    """Login audit model for tracking authentication attempts."""

    __tablename__ = "login_audits"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id"), nullable=True)
    email = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    success = Column(Boolean, default=False, nullable=False)
    failure_reason = Column(String(255), nullable=True)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<LoginAudit(id={self.id}, email={self.email}, success={self.success})>"
