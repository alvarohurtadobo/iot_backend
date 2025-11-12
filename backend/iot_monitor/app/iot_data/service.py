"""In-memory service for storing IoT data."""

from __future__ import annotations

from threading import RLock
from typing import List
from uuid import UUID

from app.iot_data.schemas import IoTDataIn, IoTDataRecord


class IoTDataService:
    """Simple service for storing IoT readings."""

    def __init__(self) -> None:
        self._storage: List[IoTDataRecord] = []
        self._lock = RLock()

    def store(self, payload: IoTDataIn) -> IoTDataRecord:
        """Store a new reading and return its representation."""
        record = IoTDataRecord(**payload.model_dump())
        with self._lock:
            self._storage.append(record)
        return record

    def list_by_sensor(self, sensor_id: UUID) -> list[IoTDataRecord]:
        """List readings belonging to a sensor."""
        with self._lock:
            return [item for item in self._storage if item.sensor_id == sensor_id]


def get_iot_data_service() -> IoTDataService:
    """Singleton instance of the IoT data service."""

    if not hasattr(get_iot_data_service, "_instance"):
        get_iot_data_service._instance = IoTDataService()  # type: ignore[attr-defined]
    return get_iot_data_service._instance  # type: ignore[attr-defined]
