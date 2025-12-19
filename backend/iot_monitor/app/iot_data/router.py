"""Router dedicated to IoT data ingestion and device registration."""

from __future__ import annotations

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.dependencies.auth import get_current_user
from app.core.config import settings
from app.db.base import get_db
from app.db.models.device import Device
from app.db.models.time_data import TimeData
from app.db.models.user import User
from app.iot_data.schemas import (
    DeviceRegisterIn,
    DeviceRegisterRecord,
    IoTDataIn,
    IoTDataRecord,
    IoTHealthResponse,
    MQTTHealth,
)
from app.mqtt.client import get_mqtt_client

router = APIRouter(prefix="/iot", tags=["iot"])


@router.post("/data", response_model=IoTDataRecord, status_code=status.HTTP_201_CREATED)
def ingest_iot_data(
    payload: IoTDataIn,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> IoTDataRecord:
    """Receive and store a reading from an IoT device to the database.
    
    Requires authentication via Bearer token.
    """
    time_data = TimeData(
        id=payload.id,
        timestamp=payload.timestamp,
        value=payload.value,
        unit=payload.unit,
        type=payload.type,
        sensor_id=payload.sensor_id,
        device_id=payload.device_id,
    )
    db.add(time_data)
    db.commit()
    db.refresh(time_data)
    
    return IoTDataRecord(
        id=time_data.id,
        timestamp=time_data.timestamp,
        value=time_data.value,
        unit=time_data.unit,
        type=time_data.type,
        sensor_id=time_data.sensor_id,
        device_id=time_data.device_id,
    )


@router.post("/many", response_model=List[IoTDataRecord], status_code=status.HTTP_201_CREATED)
def ingest_many_iot_data(
    payload: List[IoTDataIn],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[IoTDataRecord]:
    """Receive and store multiple readings from IoT devices.
    
    Requires authentication via Bearer token.
    """
    time_data_list = [
        TimeData(
            id=item.id,
            timestamp=item.timestamp,
            value=item.value,
            unit=item.unit,
            type=item.type,
            sensor_id=item.sensor_id,
            device_id=item.device_id,
        )
        for item in payload
    ]
    
    db.add_all(time_data_list)
    db.commit()
    
    # Refresh all objects to get any database-generated values
    for time_data in time_data_list:
        db.refresh(time_data)
    
    return [
        IoTDataRecord(
            id=time_data.id,
            timestamp=time_data.timestamp,
            value=time_data.value,
            unit=time_data.unit,
            type=time_data.type,
            sensor_id=time_data.sensor_id,
            device_id=time_data.device_id,
        )
        for time_data in time_data_list
    ]


@router.post("/register", response_model=DeviceRegisterRecord, status_code=status.HTTP_200_OK)
def register_device_state(
    payload: DeviceRegisterIn,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DeviceRegisterRecord:
    """Register the state of an IoT device.
    
    Requires authentication via Bearer token.
    """
    # Get the device
    device = db.query(Device).filter(Device.id == payload.device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {payload.device_id} not found",
        )
    
    # Update device state (DeviceState enum automatically converts to string)
    device.state = payload.state.value
    device.updated_at = payload.timestamp
    db.commit()
    db.refresh(device)
    
    return DeviceRegisterRecord(
        device_id=payload.device_id,
        timestamp=payload.timestamp,
        state=payload.state,
    )


@router.post("/update", response_model=DeviceRegisterRecord, status_code=status.HTTP_200_OK)
def update_device_state(
    payload: DeviceRegisterIn,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DeviceRegisterRecord:
    """Update the state of an IoT device.
    
    Requires authentication via Bearer token.
    """
    # Get the device
    device = db.query(Device).filter(Device.id == payload.device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {payload.device_id} not found",
        )
    
    # Update device state (DeviceState enum automatically converts to string)
    device.state = payload.state.value
    device.updated_at = payload.timestamp
    db.commit()
    db.refresh(device)
    
    return DeviceRegisterRecord(
        device_id=payload.device_id,
        timestamp=payload.timestamp,
        state=payload.state,
    )


@router.get("/health", response_model=IoTHealthResponse, status_code=status.HTTP_200_OK)
def iot_health_check(
    db: Annotated[Session, Depends(get_db)],
) -> IoTHealthResponse:
    """Check the health status of the IoT gateway service.
    
    Public endpoint - does not require authentication.
    """
    # Check MQTT status
    mqtt_client = get_mqtt_client()
    mqtt_status = "connected" if mqtt_client._running else "disconnected"
    
    # Check database connection
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"
    
    # Determine overall status
    overall_status = "ok"
    if db_status != "connected":
        overall_status = "degraded"
    if settings.mqtt_enabled and mqtt_status != "connected":
        overall_status = "degraded"
    
    return IoTHealthResponse(
        status=overall_status,
        service=settings.project_name,
        version=settings.version,
        mqtt=MQTTHealth(
            enabled=settings.mqtt_enabled,
            status=mqtt_status,
            broker=f"{settings.mqtt_broker_host}:{settings.mqtt_broker_port}",
            topic=settings.mqtt_topic,
        ),
        database=db_status,
    )
