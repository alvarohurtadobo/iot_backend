"""Modelo Business."""

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Business(Base):
    """Modelo de Business."""

    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    picture_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    branches = relationship("Branch", back_populates="business", cascade="all, delete-orphan")
    machines = relationship("Machine", back_populates="business", cascade="all, delete-orphan")
    users = relationship("User", back_populates="business")
    reports = relationship("Report", back_populates="business")

    def __repr__(self):
        return f"<Business(id={self.id}, name={self.name})>"

