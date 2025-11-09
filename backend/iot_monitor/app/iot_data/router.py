"""Router dedicado a ingestión de datos IoT."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.iot_data.schemas import IoTDataIn, IoTDataRecord
from app.iot_data.service import IoTDataService, get_iot_data_service

router = APIRouter(prefix="/iot", tags=["iot"])


@router.post("/data", response_model=IoTDataRecord, status_code=status.HTTP_201_CREATED)
def ingest_iot_data(
    payload: IoTDataIn,
    service: IoTDataService = Depends(get_iot_data_service),
) -> IoTDataRecord:
    """Recibir y almacenar una lectura proveniente de un dispositivo IoT."""

    return service.store(payload)
