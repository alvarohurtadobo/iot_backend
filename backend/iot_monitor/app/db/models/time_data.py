"""Modelo TimeData."""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class TimeData(Base):
    """Modelo de TimeData."""

    __tablename__ = "time_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    type = Column(String(50), nullable=False)  # Tipo de dato: "double", "int", etc.
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id"), nullable=False, index=True)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True)

    # Relaciones
    sensor = relationship("Sensor", back_populates="time_data")
    device = relationship("Device", back_populates="time_data")
    reports = relationship("Report", secondary="report_time_data", back_populates="time_data")

    # Índice compuesto para consultas frecuentes
    __table_args__ = (
        Index("idx_time_data_sensor_timestamp", "sensor_id", "timestamp"),
        Index("idx_time_data_device_timestamp", "device_id", "timestamp"),
    )

    def __repr__(self):
        return f"<TimeData(id={self.id}, sensor_id={self.sensor_id}, value={self.value}, timestamp={self.timestamp})>"

