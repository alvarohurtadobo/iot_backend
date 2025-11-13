"""Modelo Sensor."""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Sensor(Base):
    """Modelo de Sensor."""

    __tablename__ = "sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type_id = Column(UUID(as_uuid=True), ForeignKey("sensor_types.id"), nullable=False, index=True)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False, index=True)

    # Relaciones
    sensor_type = relationship("SensorType", back_populates="sensors")
    device = relationship("Device", back_populates="sensors")
    machine = relationship("Machine", back_populates="sensors")
    time_data = relationship("TimeData", back_populates="sensor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sensor(id={self.id}, name={self.name})>"

