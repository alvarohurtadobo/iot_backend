"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.api_v1 import api_router
from app.core.config import settings
from app.mqtt.client import get_mqtt_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application lifecycle (startup/shutdown)."""
    # Startup: Start MQTT client
    logger.info("Starting application...")
    logger.info(f"Service: {settings.project_name}, Version: {settings.version}")
    mqtt_client = get_mqtt_client()
    try:
        await mqtt_client.start()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Error starting MQTT client: {e}")
        logger.exception("Full traceback for MQTT startup error")
        # Continue even if MQTT fails so the API keeps working

    yield

    # Shutdown: Stop MQTT client
    logger.info("Stopping application...")
    try:
        await mqtt_client.stop()
        logger.info("Application stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping MQTT client: {e}")
        logger.exception("Full traceback for MQTT shutdown error")


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    lifespan=lifespan,
)
app.include_router(api_router, prefix="/v1")


@app.get("/")
def read_root() -> dict[str, str]:
    """Welcome message for the API."""
    return {"message": "Welcome to iotMonitor"}


@app.get("/health")
def read_health() -> dict[str, str]:
    """Basic health check endpoint."""
    try:
        mqtt_client = get_mqtt_client()
        mqtt_status = "connected" if mqtt_client._running else "disconnected"
        
        health_status = {
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
        
        logger.debug(f"Health check: status={health_status['status']}, mqtt={mqtt_status}")
        return health_status
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        logger.exception("Full traceback for health check error")
        return {
            "status": "error",
            "service": settings.project_name,
            "version": settings.version,
            "error": "Health check failed",
        }
