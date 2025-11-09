"""Esquemas Pydantic para ingestión de datos IoT."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class IoTDataIn(BaseModel):
    """Payload recibido desde dispositivos IoT."""

    sensor_id: UUID = Field(..., description="Identificador del sensor que envía el dato")
    value: float = Field(..., description="Valor numérico reportado por el sensor")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Momento en que se generó la lectura",
    )


class IoTDataRecord(IoTDataIn):
    """Representación interna/en respuesta de un dato almacenado."""

    id: UUID = Field(default_factory=uuid4, description="Identificador único de la lectura")
