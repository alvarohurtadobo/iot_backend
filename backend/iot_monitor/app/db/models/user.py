"""User model."""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    profile_picture = Column(String(500), nullable=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)  # Password hash
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    role = relationship("Role", back_populates="users")
    business = relationship("Business", back_populates="users")
    branch = relationship("Branch", back_populates="users", foreign_keys=[branch_id])
    branches_as_representative = relationship("Branch", back_populates="representative", foreign_keys="Branch.representative_id")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

