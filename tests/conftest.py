"""Global test fixtures and configuration."""
# Standard library imports
from typing import Any, Dict

# Third-party imports
import pytest

# Local imports
from tests.mocks import (
    mock_etl_port,
    mock_input_port,
    mock_model_port,
    mock_service_port,
    mock_storage_port,
)

# Re-export the mock fixtures
__all__ = [
    "mock_model_port",
    "mock_storage_port",
    "mock_input_port",
    "mock_etl_port",
    "mock_service_port",
    "sample_input_1",
    "sample_input_2",
    "sample_input_3",
]


@pytest.fixture
def sample_input_1() -> Dict[str, Any]:
    """Sample input data 1."""
    return {
        "record_id": "sample-1",
        "longitude": -122.64,
        "latitude": 38.01,
        "housing_median_age": 36.0,
        "total_rooms": 1336.0,
        "total_bedrooms": 258.0,
        "population": 678.0,
        "households": 249.0,
        "median_income": 5.5789,
        "ocean_proximity": "NEAR OCEAN",
        "median_house_value": 320201.58554044,  # Expected output
    }


@pytest.fixture
def sample_input_2() -> Dict[str, Any]:
    """Sample input data 2."""
    return {
        "record_id": "sample-2",
        "longitude": -115.73,
        "latitude": 33.35,
        "housing_median_age": 23.0,
        "total_rooms": 1586.0,
        "total_bedrooms": 448.0,
        "population": 338.0,
        "households": 182.0,
        "median_income": 1.2132,
        "ocean_proximity": "INLAND",
        "median_house_value": 58815.45033765,  # Expected output
    }


@pytest.fixture
def sample_input_3() -> Dict[str, Any]:
    """Sample input data 3."""
    return {
        "record_id": "sample-3",
        "longitude": -117.96,
        "latitude": 33.89,
        "housing_median_age": 24.0,
        "total_rooms": 1332.0,
        "total_bedrooms": 252.0,
        "population": 625.0,
        "households": 230.0,
        "median_income": 4.4375,
        "ocean_proximity": "<1H OCEAN",
        "median_house_value": 192575.77355635,  # Expected output
    }


@pytest.fixture
def expected_outputs() -> Dict[str, float]:
    """Expected output values."""
    return {
        "sample-1": 320201.58554044,
        "sample-2": 58815.45033765,
        "sample-3": 192575.77355635,
    }
