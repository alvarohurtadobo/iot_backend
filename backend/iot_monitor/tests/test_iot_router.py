"""Unit tests for the IoT router."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

from fastapi import status
from fastapi.testclient import TestClient

from app.db.models.device import Device
from app.db.models.device import Device
from app.db.models.time_data import TimeData
from app.iot_data.schemas import IoTDataRecord


class TestIoTDataIngestion:
    """Tests for the IoT data ingestion endpoint."""

    def test_post_iot_data_success(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data with valid data returns 201."""
        # Arrange
        record_id = uuid4()
        sensor_id = uuid4()
        device_id = uuid4()
        value = 25.5
        timestamp = datetime.utcnow()

        # Capture the TimeData object passed to add
        captured_time_data = None
        
        def capture_add(obj):
            nonlocal captured_time_data
            captured_time_data = obj
        
        mock_db_session.add.side_effect = capture_add
        mock_db_session.commit.return_value = None
        
        # Make refresh a no-op (the object already has all values)
        mock_db_session.refresh.return_value = None

        payload = {
            "id": str(record_id),
            "sensor_id": str(sensor_id),
            "device_id": str(device_id),
            "value": value,
            "unit": "°C",
            "type": "double",
            "timestamp": timestamp.isoformat(),
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        assert captured_time_data is not None
        assert captured_time_data.id == record_id
        assert captured_time_data.sensor_id == sensor_id
        assert captured_time_data.device_id == device_id
        
        data = response.json()
        assert data["sensor_id"] == str(sensor_id)
        assert data["device_id"] == str(device_id)
        assert data["value"] == value
        assert data["unit"] == "°C"
        assert data["type"] == "double"
        assert "id" in data
        assert UUID(data["id"]) is not None

    def test_post_iot_data_with_all_fields(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data with all required fields returns 201."""
        # Arrange
        record_id = uuid4()
        sensor_id = uuid4()
        device_id = uuid4()
        value = 30.0
        timestamp = datetime.utcnow()

        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        payload = {
            "id": str(record_id),
            "sensor_id": str(sensor_id),
            "device_id": str(device_id),
            "value": value,
            "unit": "kPa",
            "type": "double",
            "timestamp": timestamp.isoformat(),
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        
        data = response.json()
        assert data["sensor_id"] == str(sensor_id)
        assert data["device_id"] == str(device_id)
        assert data["value"] == value
        assert data["unit"] == "kPa"
        assert data["type"] == "double"
        assert "timestamp" in data

    def test_post_iot_data_missing_sensor_id(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data without sensor_id returns 422."""
        # Arrange
        payload = {
            "id": str(uuid4()),
            "device_id": str(uuid4()),
            "value": 25.5,
            "type": "double",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_db_session.add.called
        
        error_detail = response.json()
        assert "detail" in error_detail

    def test_post_iot_data_missing_value(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data without value returns 422."""
        # Arrange
        payload = {
            "id": str(uuid4()),
            "sensor_id": str(uuid4()),
            "device_id": str(uuid4()),
            "type": "double",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_db_session.add.called

    def test_post_iot_data_invalid_sensor_id_format(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data with invalid sensor_id returns 422."""
        # Arrange
        payload = {
            "id": str(uuid4()),
            "sensor_id": "not-a-valid-uuid",
            "device_id": str(uuid4()),
            "value": 25.5,
            "type": "double",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_db_session.add.called

    def test_post_iot_data_invalid_value_type(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data with non-numeric value returns 422."""
        # Arrange
        payload = {
            "id": str(uuid4()),
            "sensor_id": str(uuid4()),
            "device_id": str(uuid4()),
            "value": "not-a-number",
            "type": "double",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_db_session.add.called

    def test_post_iot_data_invalid_timestamp_format(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data with invalid timestamp returns 422."""
        # Arrange
        payload = {
            "id": str(uuid4()),
            "sensor_id": str(uuid4()),
            "device_id": str(uuid4()),
            "value": 25.5,
            "type": "double",
            "timestamp": "invalid-date-format",
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_db_session.add.called

    def test_post_iot_data_negative_value(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data accepts negative values."""
        # Arrange
        record_id = uuid4()
        sensor_id = uuid4()
        device_id = uuid4()
        value = -10.5
        timestamp = datetime.utcnow()

        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        payload = {
            "id": str(record_id),
            "sensor_id": str(sensor_id),
            "device_id": str(device_id),
            "value": value,
            "type": "double",
            "timestamp": timestamp.isoformat(),
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["value"] == value

    def test_post_iot_data_zero_value(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data accepts zero value."""
        # Arrange
        record_id = uuid4()
        sensor_id = uuid4()
        device_id = uuid4()
        value = 0.0
        timestamp = datetime.utcnow()

        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        payload = {
            "id": str(record_id),
            "sensor_id": str(sensor_id),
            "device_id": str(device_id),
            "value": value,
            "type": "double",
            "timestamp": timestamp.isoformat(),
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["value"] == value

    def test_post_iot_data_very_large_value(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/data accepts very large values."""
        # Arrange
        record_id = uuid4()
        sensor_id = uuid4()
        device_id = uuid4()
        value = 999999.999
        timestamp = datetime.utcnow()

        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        payload = {
            "id": str(record_id),
            "sensor_id": str(sensor_id),
            "device_id": str(device_id),
            "value": value,
            "type": "double",
            "timestamp": timestamp.isoformat(),
        }

        # Act
        response = client.post("/v1/iot/data", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["value"] == value


class TestIoTManyDataIngestion:
    """Tests for the IoT many data ingestion endpoint."""

    def test_post_many_iot_data_success(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/many with valid data returns 201."""
        # Arrange
        record_id_1 = uuid4()
        record_id_2 = uuid4()
        sensor_id_1 = uuid4()
        sensor_id_2 = uuid4()
        device_id_1 = uuid4()
        device_id_2 = uuid4()
        timestamp = datetime.utcnow()

        # Capture the TimeData objects passed to add_all
        captured_time_data_list = []
        
        def capture_add_all(objs):
            captured_time_data_list.extend(objs)
        
        mock_db_session.add_all.side_effect = capture_add_all
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        payload = [
            {
                "id": str(record_id_1),
                "sensor_id": str(sensor_id_1),
                "device_id": str(device_id_1),
                "value": 25.5,
                "unit": "°C",
                "type": "double",
                "timestamp": timestamp.isoformat(),
            },
            {
                "id": str(record_id_2),
                "sensor_id": str(sensor_id_2),
                "device_id": str(device_id_2),
                "value": 30.0,
                "unit": "kPa",
                "type": "double",
                "timestamp": timestamp.isoformat(),
            },
        ]

        # Act
        response = client.post("/v1/iot/many", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        mock_db_session.add_all.assert_called_once()
        mock_db_session.commit.assert_called_once()
        assert len(captured_time_data_list) == 2
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["sensor_id"] == str(sensor_id_1)
        assert data[0]["device_id"] == str(device_id_1)
        assert data[0]["value"] == 25.5
        assert data[0]["unit"] == "°C"
        assert data[1]["sensor_id"] == str(sensor_id_2)
        assert data[1]["device_id"] == str(device_id_2)
        assert data[1]["value"] == 30.0
        assert data[1]["unit"] == "kPa"

    def test_post_many_iot_data_empty_array(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/many with empty array returns 201 with empty list."""
        # Arrange
        payload = []

        mock_db_session.add_all.return_value = None
        mock_db_session.commit.return_value = None

        # Act
        response = client.post("/v1/iot/many", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        mock_db_session.add_all.assert_called_once()
        mock_db_session.commit.assert_called_once()
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_post_many_iot_data_invalid_item(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/many with invalid item returns 422."""
        # Arrange
        payload = [
            {
                "id": str(uuid4()),
                "sensor_id": str(uuid4()),
                "device_id": str(uuid4()),
                "value": 25.5,
                "type": "double",
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "id": str(uuid4()),
                "sensor_id": "invalid-uuid",
                "device_id": str(uuid4()),
                "value": 30.0,
                "type": "double",
                "timestamp": datetime.utcnow().isoformat(),
            },
        ]

        # Act
        response = client.post("/v1/iot/many", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_db_session.add_all.called

    def test_post_many_iot_data_missing_required_field(
        self, client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Test: POST /v1/iot/many with missing required field returns 422."""
        # Arrange
        payload = [
            {
                "id": str(uuid4()),
                "sensor_id": str(uuid4()),
                "device_id": str(uuid4()),
                "value": 25.5,
                "type": "double",
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "id": str(uuid4()),
                "sensor_id": str(uuid4()),
                # Missing device_id
                "value": 30.0,
                "type": "double",
                "timestamp": datetime.utcnow().isoformat(),
            },
        ]

        # Act
        response = client.post("/v1/iot/many", json=payload)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert not mock_db_session.add_all.called

