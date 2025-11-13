"""Modelo SensorType."""

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class SensorType(Base):
    """Modelo de SensorType."""

    __tablename__ = "sensor_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False, unique=True, index=True)
    type = Column(String(50), nullable=False)  # Tipo de dato: "double", "int", etc.

    # Relaciones
    sensors = relationship("Sensor", back_populates="sensor_type")

    def __repr__(self):
        return f"<SensorType(id={self.id}, name={self.name}, code={self.code})>"

