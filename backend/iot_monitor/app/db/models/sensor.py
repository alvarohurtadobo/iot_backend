"""Sensor model."""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base, UUID


class Sensor(Base):
    """Sensor model."""

    __tablename__ = "sensors"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type_id = Column(UUID(), ForeignKey("sensor_types.id"), nullable=False, index=True)
    device_id = Column(UUID(), ForeignKey("devices.id"), nullable=False, index=True)
    machine_id = Column(UUID(), ForeignKey("machines.id"), nullable=False, index=True)

    # Relationships
    sensor_type = relationship("SensorType", back_populates="sensors")
    device = relationship("Device", back_populates="sensors")
    machine = relationship("Machine", back_populates="sensors")
    time_data = relationship("TimeData", back_populates="sensor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sensor(id={self.id}, name={self.name})>"

