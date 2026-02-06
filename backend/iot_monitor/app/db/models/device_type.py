"""DeviceType model."""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base, UUID


class DeviceType(Base):
    """DeviceType model."""

    __tablename__ = "device_types"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False, unique=True, index=True)

    # Relationships
    devices = relationship("Device", back_populates="device_type")

    def __repr__(self):
        return f"<DeviceType(id={self.id}, name={self.name}, code={self.code})>"

