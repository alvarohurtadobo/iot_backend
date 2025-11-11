"""Configuración compartida para tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.iot_data.service import IoTDataService
from app.main import app


@pytest.fixture
def mock_iot_service() -> MagicMock:
    """Mock del servicio IoT para tests unitarios."""
    service = MagicMock(spec=IoTDataService)
    return service


@pytest.fixture
def client(mock_iot_service: MagicMock) -> TestClient:
    """Cliente de prueba con servicio mockeado."""
    app.dependency_overrides[IoTDataService] = lambda: mock_iot_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

