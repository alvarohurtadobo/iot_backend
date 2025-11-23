"""Router dedicated to IoT data ingestion."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models.device import Device
from app.db.models.time_data import TimeData
from app.iot_data.schemas import DeviceRegisterIn, DeviceRegisterRecord, IoTDataIn, IoTDataRecord

router = APIRouter(prefix="/iot", tags=["iot"])


@router.post("/data", response_model=IoTDataRecord, status_code=status.HTTP_201_CREATED)
def ingest_iot_data(
    payload: IoTDataIn,
    db: Session = Depends(get_db),
) -> IoTDataRecord:
    """Receive and store a reading from an IoT device."""
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
    db: Session = Depends(get_db),
) -> List[IoTDataRecord]:
    """Receive and store multiple readings from IoT devices."""
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
    db: Session = Depends(get_db),
) -> DeviceRegisterRecord:
    """Register the state of an IoT device."""
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
