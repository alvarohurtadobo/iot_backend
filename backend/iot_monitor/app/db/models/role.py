"""Role model."""

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Role(Base):
    """Role model."""

    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Relationships
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"

