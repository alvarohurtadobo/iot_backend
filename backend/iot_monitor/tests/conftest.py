"""Shared configuration for tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.iot_data.service import get_iot_data_service
from app.main import app


@pytest.fixture
def mock_iot_service() -> MagicMock:
    """Mock IoT service for unit tests."""
    service = MagicMock()
    return service


@pytest.fixture
def client(mock_iot_service: MagicMock) -> TestClient:
    """Test client with mocked service."""
    app.dependency_overrides[get_iot_data_service] = lambda: mock_iot_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

