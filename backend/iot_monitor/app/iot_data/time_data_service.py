"""Servicio para almacenar TimeData en la base de datos."""

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.time_data import TimeData
from app.mqtt.schemas import TimeDataMQTTMessage

logger = logging.getLogger(__name__)


def store_time_data(db: Session, message: TimeDataMQTTMessage) -> TimeData:
    """Almacena un registro de TimeData en la base de datos.

    Args:
        db: Sesión de base de datos SQLAlchemy
        message: Mensaje MQTT con los datos de TimeData

    Returns:
        Instancia de TimeData creada

    Raises:
        Exception: Si hay un error al almacenar los datos
    """
    try:
        time_data = TimeData(
            sensor_id=message.sensor_id,
            device_id=message.device_id,
            value=message.value,
            unit=message.unit,
            type=message.type,
            timestamp=message.timestamp,
        )
        db.add(time_data)
        db.commit()
        db.refresh(time_data)
        logger.info(
            f"TimeData almacenado: sensor_id={message.sensor_id}, "
            f"device_id={message.device_id}, value={message.value}"
        )
        return time_data
    except Exception as e:
        db.rollback()
        logger.error(f"Error al almacenar TimeData: {e}")
        raise


def get_time_data_by_sensor(
    db: Session, sensor_id: UUID, limit: int = 100
) -> list[TimeData]:
    """Obtiene registros de TimeData por sensor_id.

    Args:
        db: Sesión de base de datos SQLAlchemy
        sensor_id: ID del sensor
        limit: Número máximo de registros a retornar

    Returns:
        Lista de registros TimeData
    """
    return (
        db.query(TimeData)
        .filter(TimeData.sensor_id == sensor_id)
        .order_by(TimeData.timestamp.desc())
        .limit(limit)
        .all()
    )


def get_time_data_by_device(
    db: Session, device_id: UUID, limit: int = 100
) -> list[TimeData]:
    """Obtiene registros de TimeData por device_id.

    Args:
        db: Sesión de base de datos SQLAlchemy
        device_id: ID del dispositivo
        limit: Número máximo de registros a retornar

    Returns:
        Lista de registros TimeData
    """
    return (
        db.query(TimeData)
        .filter(TimeData.device_id == device_id)
        .order_by(TimeData.timestamp.desc())
        .limit(limit)
        .all()
    )

