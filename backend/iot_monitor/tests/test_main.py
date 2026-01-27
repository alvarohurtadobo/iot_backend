from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.mqtt import client as mqtt_client_module


def _reset_mqtt_client() -> None:
    mqtt_client_module._mqtt_client = None


def test_root_returns_welcome_message() -> None:
    _reset_mqtt_client()
    settings.mqtt_enabled = False
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to iotMonitor"}


def test_health_returns_ok_with_mqtt_disabled() -> None:
    _reset_mqtt_client()
    settings.mqtt_enabled = False
    with TestClient(app) as client:
        response = client.get("/health")

    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "ok"
    assert payload["service"] == settings.project_name
    assert payload["version"] == settings.version
    assert payload["mqtt"]["enabled"] is False
    assert payload["mqtt"]["status"] == "disconnected"
