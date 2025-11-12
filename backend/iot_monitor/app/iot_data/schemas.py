"""Pydantic schemas for IoT data ingestion."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class IoTDataIn(BaseModel):
    """Payload received from IoT devices."""

    sensor_id: UUID = Field(..., description="Identifier of the sensor sending the data")
    value: float = Field(..., description="Numeric value reported by the sensor")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Time when the reading was generated",
    )


class IoTDataRecord(IoTDataIn):
    """Internal/response representation of stored data."""

    id: UUID = Field(default_factory=uuid4, description="Unique identifier of the reading")
