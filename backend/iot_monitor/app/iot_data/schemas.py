"""Pydantic schemas for IoT data ingestion."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DeviceState(str, Enum):
    """Device state enumeration."""

    CREATED = "created"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"


class IoTDataIn(BaseModel):
    """Payload received from IoT devices."""

    id: UUID = Field(default_factory=uuid4, description="Unique identifier of the reading")
    timestamp: datetime = Field(
        ...,
        description="Time when the reading was generated",
    )
    value: float = Field(..., description="Numeric value reported by the sensor")
    unit: str | None = Field(None, description="Unit of measurement (e.g., °C, kPa)")
    type: str = Field(..., description="Data type: 'double', 'int', etc.")
    sensor_id: UUID = Field(..., description="Identifier of the sensor sending the data")
    device_id: UUID = Field(..., description="Identifier of the device associated with the sensor")


class IoTDataRecord(IoTDataIn):
    """Internal/response representation of stored data."""

    pass


class DeviceRegisterIn(BaseModel):
    """Payload for device state registration."""

    device_id: UUID = Field(..., description="Identifier of the device")
    timestamp: datetime = Field(
        ...,
        description="Time when the state was registered",
    )
    state: DeviceState = Field(..., description="State of the device (created, active, disabled, error)")


class DeviceRegisterRecord(DeviceRegisterIn):
    """Response representation of device state registration."""

    pass
