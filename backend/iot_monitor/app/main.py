"""Punto de entrada de la aplicación FastAPI."""

from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title=settings.project_name, version=settings.version)


@app.get("/")
def read_root() -> dict[str, str]:
    """Mensaje de bienvenida para la API."""
    return {"message": "Bienvenido a iotMonitor"}


@app.get("/health")
def read_health() -> dict[str, str]:
    """Endpoint de health check básico."""
    return {
        "status": "ok",
        "service": settings.project_name,
        "version": settings.version,
    }
