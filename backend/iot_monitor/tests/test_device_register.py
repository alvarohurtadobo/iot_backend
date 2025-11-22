"""Unit tests for the device register endpoint."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from app.db.models.device import Device


class TestDeviceRegister:
    """Tests for the device state registration endpoint."""

    def test_post_device_register_success(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/register with valid data returns 200."""
        # Arrange
        device_id = uuid4()
        state = 100.0
        timestamp = datetime.utcnow()

        mock_device = Device(
            id=device_id,
            name="Test Device",
            code="TEST001",
            type_id=uuid4(),
            machine_id=uuid4(),
        )
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_device
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        payload = {
            "device_id": str(device_id),
            "timestamp": timestamp.isoformat(),
            "state": state,
        }

        # Act
        response = client.post("/v1/iot/register", json=payload)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_db_session.commit.assert_called_once()
        
        data = response.json()
        assert data["device_id"] == str(device_id)
        assert data["state"] == state
        assert "timestamp" in data

    def test_post_device_register_device_not_found(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/register with non-existent device returns 404."""
        # Arrange
        device_id = uuid4()
        timestamp = datetime.utcnow()

        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        payload = {
            "device_id": str(device_id),
            "timestamp": timestamp.isoformat(),
            "state": 100.0,
        }

        # Act
        response = client.post("/v1/iot/register", json=payload)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert not mock_db_session.commit.called

    def test_post_device_register_missing_device_id(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/register without device_id returns 422."""
        # Arrange
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "state": 100.0,
        }

        # Act
        response = client.post("/v1/iot/register", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_db_session.commit.called

    def test_post_device_register_missing_state(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/register without state returns 422."""
        # Arrange
        payload = {
            "device_id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Act
        response = client.post("/v1/iot/register", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_db_session.commit.called

    def test_post_device_register_invalid_device_id_format(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/register with invalid device_id returns 422."""
        # Arrange
        payload = {
            "device_id": "invalid-uuid",
            "timestamp": datetime.utcnow().isoformat(),
            "state": 100.0,
        }

        # Act
        response = client.post("/v1/iot/register", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_db_session.commit.called

    def test_post_device_register_negative_state(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/register accepts negative state values."""
        # Arrange
        device_id = uuid4()
        state = -50.0
        timestamp = datetime.utcnow()

        mock_device = Device(
            id=device_id,
            name="Test Device",
            code="TEST001",
            type_id=uuid4(),
            machine_id=uuid4(),
        )
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_device
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        payload = {
            "device_id": str(device_id),
            "timestamp": timestamp.isoformat(),
            "state": state,
        }

        # Act
        response = client.post("/v1/iot/register", json=payload)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["state"] == state

