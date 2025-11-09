"""Servicio en memoria para almacenar datos IoT."""

from __future__ import annotations

from threading import RLock
from typing import List
from uuid import UUID

from app.iot_data.schemas import IoTDataIn, IoTDataRecord


class IoTDataService:
    """Servicio simple para almacenar lecturas IoT."""

    def __init__(self) -> None:
        self._storage: List[IoTDataRecord] = []
        self._lock = RLock()

    def store(self, payload: IoTDataIn) -> IoTDataRecord:
        """Guardar una nueva lectura y retornar su representación."""
        record = IoTDataRecord(**payload.model_dump())
        with self._lock:
            self._storage.append(record)
        return record

    def list_by_sensor(self, sensor_id: UUID) -> list[IoTDataRecord]:
        """Listar lecturas pertenecientes a un sensor."""
        with self._lock:
            return [item for item in self._storage if item.sensor_id == sensor_id]


def get_iot_data_service() -> IoTDataService:
    """Instancia singleton del servicio IoT data."""

    if not hasattr(get_iot_data_service, "_instance"):
        get_iot_data_service._instance = IoTDataService()  # type: ignore[attr-defined]
    return get_iot_data_service._instance  # type: ignore[attr-defined]
