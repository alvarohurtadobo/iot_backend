"""Schemas Pydantic para mensajes MQTT de TimeData."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TimeDataMQTTMessage(BaseModel):
    """Schema para mensajes MQTT de TimeData."""

    sensor_id: UUID = Field(..., description="ID del sensor que envía los datos")
    device_id: UUID = Field(..., description="ID del dispositivo asociado")
    value: float = Field(..., description="Valor numérico reportado por el sensor")
    unit: str | None = Field(None, description="Unidad de medida (ej: °C, kPa)")
    type: str = Field(..., description="Tipo de dato: 'double', 'int', etc.")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp cuando se generó la lectura",
    )

    class Config:
        """Configuración del modelo."""

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

