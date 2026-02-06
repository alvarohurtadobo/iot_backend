"""SQLAlchemy database configuration."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import TypeDecorator, CHAR
import uuid

from app.core.config import settings

# Tipo UUID compatible con SQLite y PostgreSQL (se guarda como string en SQLite)
class UUID(TypeDecorator):
    impl = CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value) if value else None

# Parámetros del engine según el dialecto
_connect_args = {}
if settings.database_url.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    echo=True,
    connect_args=_connect_args,
)

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


def create_tables_if_sqlite() -> None:
    """Crea las tablas desde los modelos cuando se usa SQLite (útil para desarrollo local)."""
    if settings.database_url.startswith("sqlite"):
        import app.db.models  # noqa: F401 - registra todos los modelos en Base.metadata
        Base.metadata.create_all(bind=engine)
