"""Branch model."""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base, UUID


class Branch(Base):
    """Branch model."""

    __tablename__ = "branches"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    business_id = Column(UUID(), ForeignKey("businesses.id"), nullable=False, index=True)
    representative_id = Column(UUID(), ForeignKey("users.id"), nullable=True)
    address = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    business = relationship("Business", back_populates="branches")
    representative = relationship("User", back_populates="branches_as_representative", foreign_keys=[representative_id])
    users = relationship("User", back_populates="branch", foreign_keys="User.branch_id")
    machines = relationship("Machine", back_populates="branch", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="branch")

    def __repr__(self):
        return f"<Branch(id={self.id}, name={self.name})>"

