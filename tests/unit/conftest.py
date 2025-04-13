"""Shared test fixtures."""
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from src.core.domain.entities.housing_record import HousingRecord


@pytest.fixture
def mock_housing_record():
    """Create a housing record with test data."""
    return HousingRecord(
        longitude=-122.64,
        latitude=38.01,
        housing_median_age=36.0,
        total_rooms=1336.0,
        total_bedrooms=258.0,
        population=678.0,
        households=249.0,
        median_income=5.5789,
        ocean_proximity="NEAR OCEAN",
    )


@pytest.fixture
def mock_path():
    """Create a mock Path object."""
    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True
    return mock_path


@pytest.fixture
def mock_sklearn_model():
    """Create a mock scikit-learn model."""
    model = MagicMock()
    model.predict.return_value = np.array([320201.58554044])
    return model


@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session."""
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = None
    return session


@pytest.fixture
def mock_dagster_client():
    """Create a mock DagsterGraphQLClient."""
    client = MagicMock()
    client.submit_job_execution.return_value = "test-run-id"
    return client


@pytest.fixture
def mock_settings():
    """Create a mock settings object."""
    settings = MagicMock()
    settings.database_url = "postgresql://fake:fake@localhost:5432/fake"
    settings.MODEL_PATH = "/path/to/model.joblib"
    return settings
