"""Mock generator utilities for ports."""
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


def create_mock_from_protocol(protocol_class: Any, **kwargs: Any) -> Any:
    """Create a mock object that implements the given protocol.

    Args:
        protocol_class: The protocol class to mock
        **kwargs: Additional attributes to set on the mock

    Returns:
        A mock object that implements the protocol
    """
    # Create a mock that implements the protocol
    mock = MagicMock()

    # Set any additional attributes
    for key, value in kwargs.items():
        setattr(mock, key, value)

    return mock


@pytest.fixture
def mock_model_port():
    """Fixture that creates a mock model port."""
    from src.core.port.model_port import ModelPort

    mock = create_mock_from_protocol(ModelPort)
    mock.predict = AsyncMock(return_value=0.0)
    mock.load_model = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_storage_port():
    """Fixture that creates a mock storage port."""
    from src.core.port.storage_port import StoragePort

    mock = create_mock_from_protocol(StoragePort)
    mock.save_housing_record = MagicMock(return_value="test-id")
    mock.get_housing_record = MagicMock(return_value=None)
    mock.save_prediction = MagicMock(return_value="test-id")
    mock.get_prediction = MagicMock(return_value=None)
    return mock


@pytest.fixture
def mock_input_port():
    """Fixture that creates a mock input port."""
    from src.core.port.input_port import InputPort

    return create_mock_from_protocol(InputPort)


@pytest.fixture
def mock_etl_port():
    """Fixture that creates a mock ETL port."""
    from src.core.port.etl_port import ETLPort

    return create_mock_from_protocol(ETLPort)


@pytest.fixture
def mock_service_port():
    """Fixture that creates a mock service port."""
    from src.core.port.service_port import ServicePort

    return create_mock_from_protocol(ServicePort)
