"""Role model."""

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base, UUID


class Role(Base):
    """Role model."""

    __tablename__ = "roles"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Relationships
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"

