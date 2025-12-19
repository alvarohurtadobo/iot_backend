"""Service for storing TimeData in the database."""

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.time_data import TimeData
from app.mqtt.schemas import TimeDataMQTTMessage

logger = logging.getLogger(__name__)


def store_time_data(db: Session, message: TimeDataMQTTMessage) -> TimeData:
    """Store a TimeData record in the database.

    Args:
        db: SQLAlchemy database session
        message: MQTT message with TimeData

    Returns:
        Created TimeData instance

    Raises:
        Exception: If there is an error storing the data
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
            f"TimeData stored: sensor_id={message.sensor_id}, "
            f"device_id={message.device_id}, value={message.value}"
        )
        return time_data
    except Exception as e:
        db.rollback()
        logger.error(
            f"Error storing TimeData: sensor_id={message.sensor_id}, "
            f"device_id={message.device_id}, value={message.value}, "
            f"error={str(e)}"
        )
        logger.exception("Full traceback for TimeData storage error")
        raise


def get_time_data_by_sensor(
    db: Session, sensor_id: UUID, limit: int = 100
) -> list[TimeData]:
    """Get TimeData records by sensor_id.

    Args:
        db: SQLAlchemy database session
        sensor_id: Sensor ID
        limit: Maximum number of records to return

    Returns:
        List of TimeData records
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
    """Get TimeData records by device_id.

    Args:
        db: SQLAlchemy database session
        device_id: Device ID
        limit: Maximum number of records to return

    Returns:
        List of TimeData records
    """
    return (
        db.query(TimeData)
        .filter(TimeData.device_id == device_id)
        .order_by(TimeData.timestamp.desc())
        .limit(limit)
        .all()
    )

