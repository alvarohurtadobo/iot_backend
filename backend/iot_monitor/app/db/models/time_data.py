"""TimeData model."""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base, UUID


class TimeData(Base):
    """Time-series data model: sensor readings with timestamp, value and unit."""

    __tablename__ = "time_data"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    type = Column(String(50), nullable=False)  # Value type: "double", "int", etc. (avoid using as variable name)
    sensor_id = Column(UUID(), ForeignKey("sensors.id"), nullable=False, index=True)
    device_id = Column(UUID(), ForeignKey("devices.id"), nullable=False, index=True)

    # Relationships
    sensor = relationship("Sensor", back_populates="time_data")
    device = relationship("Device", back_populates="time_data")
    reports = relationship("Report", secondary="report_time_data", back_populates="time_data")

    # Composite index for frequent queries
    __table_args__ = (
        Index("idx_time_data_sensor_timestamp", "sensor_id", "timestamp"),
        Index("idx_time_data_device_timestamp", "device_id", "timestamp"),
    )

    def __repr__(self):
        return f"<TimeData(id={self.id}, sensor_id={self.sensor_id}, value={self.value}, timestamp={self.timestamp})>"

