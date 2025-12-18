"""Device model."""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Device(Base):
    """Device model."""

    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    type_id = Column(UUID(as_uuid=True), ForeignKey("device_types.id"), nullable=False, index=True)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False, index=True)
    location = Column(String(500), nullable=True)
    state = Column(String(20), nullable=True, comment="Current state of the device (created, active, disabled, error)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    device_type = relationship("DeviceType", back_populates="devices")
    machine = relationship("Machine", back_populates="devices")
    sensors = relationship("Sensor", back_populates="device", cascade="all, delete-orphan")
    time_data = relationship("TimeData", back_populates="device", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="device")

    def __repr__(self):
        return f"<Device(id={self.id}, name={self.name}, code={self.code})>"

