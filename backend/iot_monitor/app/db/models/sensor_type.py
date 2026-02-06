"""SensorType model."""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base, UUID


class SensorType(Base):
    """SensorType model."""

    __tablename__ = "sensor_types"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False, unique=True, index=True)
    type = Column(String(50), nullable=False)  # Data type: "double", "int", etc.

    # Relationships
    sensors = relationship("Sensor", back_populates="sensor_type")

    def __repr__(self):
        return f"<SensorType(id={self.id}, name={self.name}, code={self.code})>"

