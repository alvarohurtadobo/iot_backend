"""Pydantic schemas for MQTT TimeData messages."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TimeDataMQTTMessage(BaseModel):
    """Schema for MQTT TimeData messages."""

    sensor_id: UUID = Field(..., description="ID of the sensor sending the data")
    device_id: UUID = Field(..., description="ID of the associated device")
    value: float = Field(..., description="Numeric value reported by the sensor")
    unit: str | None = Field(None, description="Unit of measurement (e.g., °C, kPa)")
    type: str = Field(..., description="Data type: 'double', 'int', etc.")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the reading was generated",
    )

    class Config:
        """Model configuration."""

        json_schema_extra = {
            "example": {
                "sensor_id": "123e4567-e89b-12d3-a456-426614174000",
                "device_id": "123e4567-e89b-12d3-a456-426614174001",
                "value": 25.5,
                "unit": "°C",
                "type": "double",
                "timestamp": "2024-01-01T12:00:00Z",
            }
        }

