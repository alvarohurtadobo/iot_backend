"""Machine model."""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Machine(Base):
    """Machine model."""

    __tablename__ = "machines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True)
    year = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    business = relationship("Business", back_populates="machines")
    branch = relationship("Branch", back_populates="machines")
    devices = relationship("Device", back_populates="machine", cascade="all, delete-orphan")
    sensors = relationship("Sensor", back_populates="machine", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="machine")

    def __repr__(self):
        return f"<Machine(id={self.id}, name={self.name}, code={self.code})>"

