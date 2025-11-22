"""SQLAlchemy database configuration."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(settings.database_url, echo=True)

# Create SessionLocal for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative Base for future models
Base = declarative_base()


def get_db():
    """Function for dependency injection of database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
