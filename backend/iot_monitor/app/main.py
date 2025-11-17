"""Punto de entrada de la aplicación FastAPI."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.api_v1 import api_router
from app.core.config import settings
from app.mqtt.client import get_mqtt_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación (startup/shutdown)."""
    # Startup: Iniciar cliente MQTT
    logger.info("Iniciando aplicación...")
    mqtt_client = get_mqtt_client()
    try:
        await mqtt_client.start()
    except Exception as e:
        logger.error(f"Error al iniciar cliente MQTT: {e}")
        # Continuar aunque falle MQTT para que la API siga funcionando

    yield

    # Shutdown: Detener cliente MQTT
    logger.info("Deteniendo aplicación...")
    try:
        await mqtt_client.stop()
    except Exception as e:
        logger.error(f"Error al detener cliente MQTT: {e}")


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    lifespan=lifespan,
)
app.include_router(api_router, prefix="/v1")


@app.get("/")
def read_root() -> dict[str, str]:
    """Mensaje de bienvenida para la API."""
    return {"message": "Bienvenido a iotMonitor"}


@app.get("/health")
def read_health() -> dict[str, str]:
    """Endpoint de health check básico."""
    mqtt_client = get_mqtt_client()
    mqtt_status = "connected" if mqtt_client._running else "disconnected"
    
    return {
        "status": "ok",
        "service": settings.project_name,
        "version": settings.version,
        "mqtt": {
            "enabled": settings.mqtt_enabled,
            "status": mqtt_status,
            "broker": f"{settings.mqtt_broker_host}:{settings.mqtt_broker_port}",
            "topic": settings.mqtt_topic,
        },
    }
