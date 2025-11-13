"""Modelo Report."""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

# Tabla asociativa para la relación muchos-a-muchos entre Report y TimeData
report_time_data = Table(
    "report_time_data",
    Base.metadata,
    Column("report_id", UUID(as_uuid=True), ForeignKey("reports.id"), primary_key=True),
    Column("time_data_id", UUID(as_uuid=True), ForeignKey("time_data.id"), primary_key=True),
)


class Report(Base):
    """Modelo de Report."""

    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False, index=True)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    business = relationship("Business", back_populates="reports")
    branch = relationship("Branch", back_populates="reports")
    machine = relationship("Machine", back_populates="reports")
    device = relationship("Device", back_populates="reports")
    time_data = relationship("TimeData", secondary=report_time_data, back_populates="reports")

    def __repr__(self):
        return f"<Report(id={self.id}, name={self.name})>"

