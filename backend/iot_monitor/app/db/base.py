"""Configuración de la base de datos SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Crear engine de SQLAlchemy
engine = create_engine(settings.database_url, echo=True)

# Crear SessionLocal para sesiones de DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear Base declarativa para futuros modelos
Base = declarative_base()


def get_db():
    """Función para dependency injection de sesiones de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
