"""Unit tests for the IoT router."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

from fastapi import status
from fastapi.testclient import TestClient

from app.iot_data.schemas import IoTDataRecord


class TestIoTDataIngestion:
    """Tests for the IoT data ingestion endpoint."""

    def test_post_iot_data_success(
        self, client: TestClient, mock_iot_service: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data with valid data returns 201."""
        # Arrange
        sensor_id = uuid4()
        value = 25.5
        timestamp = datetime.utcnow().isoformat()

        expected_record = IoTDataRecord(
            id=uuid4(),
            sensor_id=sensor_id,
            value=value,
            timestamp=datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
        )

        mock_iot_service.store.return_value = expected_record

        payload = {
            "sensor_id": str(sensor_id),
            "value": value,
            "timestamp": timestamp,
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        mock_iot_service.store.assert_called_once()
        
        data = response.json()
        assert data["sensor_id"] == str(sensor_id)
        assert data["value"] == value
        assert "id" in data
        assert UUID(data["id"]) is not None

    def test_post_iot_data_with_default_timestamp(
        self, client: TestClient, mock_iot_service: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data without timestamp uses default timestamp."""
        # Arrange
        sensor_id = uuid4()
        value = 30.0

        expected_record = IoTDataRecord(
            id=uuid4(),
            sensor_id=sensor_id,
            value=value,
            timestamp=datetime.utcnow(),
        )

        mock_iot_service.store.return_value = expected_record

        payload = {
            "sensor_id": str(sensor_id),
            "value": value,
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        mock_iot_service.store.assert_called_once()
        
        data = response.json()
        assert data["sensor_id"] == str(sensor_id)
        assert data["value"] == value
        assert "timestamp" in data

    def test_post_iot_data_missing_sensor_id(
        self, client: TestClient, mock_iot_service: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data without sensor_id returns 422."""
        # Arrange
        payload = {
            "value": 25.5,
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_iot_service.store.called
        
        error_detail = response.json()
        assert "detail" in error_detail

    def test_post_iot_data_missing_value(
        self, client: TestClient, mock_iot_service: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data without value returns 422."""
        # Arrange
        payload = {
            "sensor_id": str(uuid4()),
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_iot_service.store.called

    def test_post_iot_data_invalid_sensor_id_format(
        self, client: TestClient, mock_iot_service: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data with invalid sensor_id returns 422."""
        # Arrange
        payload = {
            "sensor_id": "not-a-valid-uuid",
            "value": 25.5,
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_iot_service.store.called

    def test_post_iot_data_invalid_value_type(
        self, client: TestClient, mock_iot_service: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data with non-numeric value returns 422."""
        # Arrange
        payload = {
            "sensor_id": str(uuid4()),
            "value": "not-a-number",
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_iot_service.store.called

    def test_post_iot_data_invalid_timestamp_format(
        self, client: TestClient, mock_iot_service: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data with invalid timestamp returns 422."""
        # Arrange
        payload = {
            "sensor_id": str(uuid4()),
            "value": 25.5,
            "timestamp": "invalid-date-format",
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_iot_service.store.called

    def test_post_iot_data_negative_value(
        self, client: TestClient, mock_iot_service: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data accepts negative values."""
        # Arrange
        sensor_id = uuid4()
        value = -10.5

        expected_record = IoTDataRecord(
            id=uuid4(),
            sensor_id=sensor_id,
            value=value,
            timestamp=datetime.utcnow(),
        )

        mock_iot_service.store.return_value = expected_record

        payload = {
            "sensor_id": str(sensor_id),
            "value": value,
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["value"] == value

    def test_post_iot_data_zero_value(
        self, client: TestClient, mock_iot_service: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data accepts zero value."""
        # Arrange
        sensor_id = uuid4()
        value = 0.0

        expected_record = IoTDataRecord(
            id=uuid4(),
            sensor_id=sensor_id,
            value=value,
            timestamp=datetime.utcnow(),
        )

        mock_iot_service.store.return_value = expected_record

        payload = {
            "sensor_id": str(sensor_id),
            "value": value,
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["value"] == value

    def test_post_iot_data_very_large_value(
        self, client: TestClient, mock_iot_service: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data accepts very large values."""
        # Arrange
        sensor_id = uuid4()
        value = 999999.999

        expected_record = IoTDataRecord(
            id=uuid4(),
            sensor_id=sensor_id,
            value=value,
            timestamp=datetime.utcnow(),
        )

        mock_iot_service.store.return_value = expected_record

        payload = {
            "sensor_id": str(sensor_id),
            "value": value,
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["value"] == value

