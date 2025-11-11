"""Tests unitarios para el router de IoT."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

import pytest
from fastapi import status

from app.iot_data.schemas import IoTDataRecord


class TestIoTDataIngestion:
    """Tests para el endpoint de ingestión de datos IoT."""

    def test_post_iot_data_success(
        self, client: pytest.fixture, mock_iot_service: pytest.fixture
    ) -> None:
        """Test: POST /v1/iot/data con datos válidos retorna 201."""
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
        assert mock_iot_service.store.called_once()
        
        data = response.json()
        assert data["sensor_id"] == str(sensor_id)
        assert data["value"] == value
        assert "id" in data
        assert UUID(data["id"]) is not None

    def test_post_iot_data_with_default_timestamp(
        self, client: pytest.fixture, mock_iot_service: pytest.fixture
    ) -> None:
        """Test: POST /v1/iot/data sin timestamp usa timestamp por defecto."""
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
        assert mock_iot_service.store.called_once()
        
        data = response.json()
        assert data["sensor_id"] == str(sensor_id)
        assert data["value"] == value
        assert "timestamp" in data

    def test_post_iot_data_missing_sensor_id(
        self, client: pytest.fixture, mock_iot_service: pytest.fixture
    ) -> None:
        """Test: POST /v1/iot/data sin sensor_id retorna 422."""
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
        self, client: pytest.fixture, mock_iot_service: pytest.fixture
    ) -> None:
        """Test: POST /v1/iot/data sin value retorna 422."""
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
        self, client: pytest.fixture, mock_iot_service: pytest.fixture
    ) -> None:
        """Test: POST /v1/iot/data con sensor_id inválido retorna 422."""
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
        self, client: pytest.fixture, mock_iot_service: pytest.fixture
    ) -> None:
        """Test: POST /v1/iot/data con value no numérico retorna 422."""
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
        self, client: pytest.fixture, mock_iot_service: pytest.fixture
    ) -> None:
        """Test: POST /v1/iot/data con timestamp inválido retorna 422."""
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
        self, client: pytest.fixture, mock_iot_service: pytest.fixture
    ) -> None:
        """Test: POST /v1/iot/data acepta valores negativos."""
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
        self, client: pytest.fixture, mock_iot_service: pytest.fixture
    ) -> None:
        """Test: POST /v1/iot/data acepta valor cero."""
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
        self, client: pytest.fixture, mock_iot_service: pytest.fixture
    ) -> None:
        """Test: POST /v1/iot/data acepta valores muy grandes."""
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

