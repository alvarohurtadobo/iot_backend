"""Shared configuration for tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.main import app


@pytest.fixture
def mock_db_session() -> MagicMock:
    """Mock database session for unit tests."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def client(mock_db_session: MagicMock) -> TestClient:
    """Test client with mocked database session."""
    app.dependency_overrides[get_db] = lambda: mock_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

