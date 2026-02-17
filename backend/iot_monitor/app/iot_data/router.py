"""Router dedicated to IoT data ingestion and device registration."""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.db.base import get_db
from app.db.models.device import Device
from app.db.models.time_data import TimeData
from app.iot_data.schemas import (
    DeviceRegisterIn,
    DeviceRegisterRecord,
    IoTDataIn,
    IoTDataRecord,
    IoTHealthResponse,
    MQTTHealth,
)
from app.mqtt.client import get_mqtt_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/iot", tags=["iot"])


@router.post("/data", response_model=IoTDataRecord, status_code=status.HTTP_201_CREATED)
def ingest_iot_data(
    payload: IoTDataIn,
    db: Session = Depends(get_db),
) -> IoTDataRecord:
    """Receive and store a reading from an IoT device to the database."""
    try:
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
        
        logger.info(
            f"IoT data ingested successfully: id={time_data.id}, "
            f"sensor_id={payload.sensor_id}, device_id={payload.device_id}, "
            f"value={payload.value}, timestamp={payload.timestamp}"
        )
        
        return IoTDataRecord(
            id=time_data.id,
            timestamp=time_data.timestamp,
            value=time_data.value,
            unit=time_data.unit,
            type=time_data.type,
            sensor_id=time_data.sensor_id,
            device_id=time_data.device_id,
        )
    except IntegrityError as e:
        db.rollback()
        logger.error(
            f"Integrity error storing IoT data: sensor_id={payload.sensor_id}, "
            f"device_id={payload.device_id}, error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Data already exists or violates an integrity constraint",
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error storing IoT data: sensor_id={payload.sensor_id}, "
            f"device_id={payload.device_id}, error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error storing IoT data in the database",
        ) from e
    except Exception as e:
        db.rollback()
        logger.exception(
            f"Unexpected error storing IoT data: sensor_id={payload.sensor_id}, "
            f"device_id={payload.device_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error processing IoT data",
        ) from e


@router.post("/many", response_model=List[IoTDataRecord], status_code=status.HTTP_201_CREATED)
def ingest_many_iot_data(
    payload: List[IoTDataIn],
    db: Session = Depends(get_db),
) -> List[IoTDataRecord]:
    """Receive and store multiple readings from IoT devices."""
    try:
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
        
        logger.info(
            f"Bulk IoT data ingested successfully: count={len(time_data_list)}, "
            f"device_ids={set(item.device_id for item in payload)}"
        )
        
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
    except IntegrityError as e:
        db.rollback()
        logger.error(
            f"Integrity error storing bulk IoT data: count={len(payload)}, "
            f"error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="One or more records already exist or violate integrity constraints",
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error storing bulk IoT data: count={len(payload)}, "
            f"error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error storing IoT data in the database",
        ) from e
    except Exception as e:
        db.rollback()
        logger.exception(
            f"Unexpected error storing bulk IoT data: count={len(payload)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error processing IoT data",
        ) from e


@router.post("/register", response_model=DeviceRegisterRecord, status_code=status.HTTP_200_OK)
def register_device_state(
    payload: DeviceRegisterIn,
    db: Session = Depends(get_db),
) -> DeviceRegisterRecord:
    """Register the state of an IoT device."""
    try:
        # Get the device
        device = db.query(Device).filter(Device.id == payload.device_id).first()
        
        if not device:
            logger.warning(
                f"Device not found for registration: device_id={payload.device_id}, "
                f"state={payload.state.value}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with id {payload.device_id} not found",
            )
        
        # Update device state (DeviceState enum automatically converts to string)
        device.state = payload.state.value
        device.updated_at = payload.timestamp
        db.commit()
        db.refresh(device)
        
        logger.info(
            f"Device state registered: device_id={payload.device_id}, "
            f"state={payload.state.value}, timestamp={payload.timestamp}"
        )
        
        return DeviceRegisterRecord(
            device_id=payload.device_id,
            timestamp=payload.timestamp,
            state=payload.state,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error registering device state: device_id={payload.device_id}, "
            f"error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering device state",
        ) from e
    except Exception as e:
        db.rollback()
        logger.exception(
            f"Unexpected error registering device state: device_id={payload.device_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error processing device registration",
        ) from e


@router.post("/update", response_model=DeviceRegisterRecord, status_code=status.HTTP_200_OK)
def update_device_state(
    payload: DeviceRegisterIn,
    db: Session = Depends(get_db),
) -> DeviceRegisterRecord:
    """Update the state of an IoT device."""
    try:
        # Get the device
        device = db.query(Device).filter(Device.id == payload.device_id).first()
        
        if not device:
            logger.warning(
                f"Device not found for update: device_id={payload.device_id}, "
                f"state={payload.state.value}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with id {payload.device_id} not found",
            )
        
        old_state = device.state
        # Update device state (DeviceState enum automatically converts to string)
        device.state = payload.state.value
        device.updated_at = payload.timestamp
        db.commit()
        db.refresh(device)
        
        logger.info(
            f"Device state updated: device_id={payload.device_id}, "
            f"old_state={old_state}, new_state={payload.state.value}, "
            f"timestamp={payload.timestamp}"
        )
        
        return DeviceRegisterRecord(
            device_id=payload.device_id,
            timestamp=payload.timestamp,
            state=payload.state,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error updating device state: device_id={payload.device_id}, "
            f"error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating device state",
        ) from e
    except Exception as e:
        db.rollback()
        logger.exception(
            f"Unexpected error updating device state: device_id={payload.device_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error processing device update",
        ) from e


@router.get("/health", response_model=IoTHealthResponse, status_code=status.HTTP_200_OK)
def iot_health_check(
    db: Session = Depends(get_db),
) -> IoTHealthResponse:
    """Check the health status of the IoT gateway service."""
    # Check MQTT status
    mqtt_client = get_mqtt_client()
    mqtt_status = "connected" if mqtt_client._running else "disconnected"
    
    # Check database connection
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
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
