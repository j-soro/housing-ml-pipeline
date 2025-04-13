"""Unit tests for PostgresAdapter."""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.adapter.driven.storage.postgres_adapter import PostgresAdapter
from src.core.domain.entities.prediction import Prediction, PredictionStatus
from src.core.domain.exceptions import StorageError


@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session."""
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = None
    return session


@pytest.fixture
def mock_engine():
    """Create a mock SQLAlchemy engine."""
    return MagicMock()


@pytest.fixture
def mock_record_model():
    """Create a mock record model."""
    model = MagicMock()
    model.id = "test-id-1"
    model.longitude = -122.64
    model.latitude = 38.01
    model.housing_median_age = 36.0
    model.total_rooms = 1336.0
    model.total_bedrooms = 258.0
    model.population = 678.0
    model.households = 249.0
    model.median_income = 5.5789
    model.ocean_proximity = "NEAR OCEAN"
    model.created_at = datetime.now()
    model.updated_at = datetime.now()
    return model


@pytest.fixture
def mock_prediction_model():
    """Create a mock prediction model."""
    model = MagicMock()
    model.id = "test-pred-1"
    model.cleaned_record_id = "test-id-1"
    model.prediction_value = 320201.58554044
    model.created_at = datetime.now()
    model.run_id = "test-run-1"
    return model


@pytest.fixture
def adapter(mock_session, mock_engine):
    """Create a PostgresAdapter with mocked dependencies."""
    with patch(
        "src.adapter.driven.storage.postgres_adapter.create_engine", return_value=mock_engine
    ), patch("src.adapter.driven.storage.postgres_adapter.sessionmaker") as mock_sessionmaker:
        # Configure the sessionmaker to return our mock session
        mock_sessionmaker.return_value.return_value = mock_session
        return PostgresAdapter(connection_url="postgresql://fake:fake@localhost:5432/fake")


def test_save_housing_record_success(adapter, mock_housing_record, mock_session):
    """Test successful saving of a housing record."""
    # Call the method
    result = adapter.save_housing_record(mock_housing_record)

    # Verify the result
    assert result == mock_housing_record.id

    # Verify the session was used correctly
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.__exit__.assert_called_once()


def test_save_housing_record_error(adapter, mock_housing_record, mock_session):
    """Test error handling when saving a housing record."""
    # Configure the session to raise an exception
    mock_session.commit.side_effect = SQLAlchemyError("Database error")

    # Call the method and expect an exception
    with pytest.raises(StorageError) as excinfo:
        adapter.save_housing_record(mock_housing_record)

    # Verify the error message
    assert "Error saving housing record: Database error" in str(excinfo.value)

    # Verify the session was used correctly
    mock_session.add.assert_called_once()
    mock_session.__exit__.assert_called_once()


def test_get_housing_record_success(adapter, mock_record_model, mock_session):
    """Test successful retrieval of a housing record."""
    # Configure the session query
    mock_query = MagicMock()
    mock_query.filter_by.return_value = mock_query
    mock_query.first.return_value = mock_record_model
    mock_session.query.return_value = mock_query

    # Call the method
    result = adapter.get_housing_record("test-id-1")

    # Verify the result
    assert result is not None
    assert result.id == "test-id-1"
    assert result.longitude == -122.64
    assert result.latitude == 38.01
    assert result.housing_median_age == 36.0
    assert result.total_rooms == 1336.0
    assert result.total_bedrooms == 258.0
    assert result.population == 678.0
    assert result.households == 249.0
    assert result.median_income == 5.5789
    assert result.ocean_proximity == "NEAR OCEAN"

    # Verify the session was used correctly
    mock_session.query.assert_called_once()
    mock_session.__exit__.assert_called_once()


def test_get_housing_record_error(adapter, mock_session):
    """Test error handling when retrieving a housing record."""
    # Configure the session to raise an exception
    mock_session.query.side_effect = SQLAlchemyError("Database error")

    # Call the method and expect an exception
    with pytest.raises(StorageError) as excinfo:
        adapter.get_housing_record("test-id-1")

    # Verify the error message
    assert "Error getting housing record: Database error" in str(excinfo.value)

    # Verify the session was used correctly
    mock_session.__exit__.assert_called_once()


def test_save_prediction_success(adapter, mock_prediction_model, mock_session):
    """Test successful saving of a prediction."""
    # Configure the session query
    mock_query = MagicMock()
    mock_query.filter_by.return_value = mock_query
    mock_query.first.return_value = mock_prediction_model
    mock_session.query.return_value = mock_query

    # Create a prediction
    prediction = Prediction(
        id="test-pred-1",
        record_id="test-id-1",
        value=320201.58554044,
        created_at=datetime.now(),
        status=PredictionStatus.COMPLETED,
        run_id="test-run-1",
    )

    # Call the method
    result = adapter.save_prediction(prediction)

    # Verify the result
    assert result == prediction.id

    # Verify the session was used correctly
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.__exit__.assert_called_once()


def test_save_prediction_error(adapter, mock_session):
    """Test error handling when saving a prediction."""
    # Configure the session to raise an exception
    mock_session.commit.side_effect = SQLAlchemyError("Database error")

    # Create a prediction
    prediction = Prediction(
        id="test-pred-1",
        record_id="test-id-1",
        value=320201.58554044,
        created_at=datetime.now(),
        status=PredictionStatus.COMPLETED,
        run_id="test-run-1",
    )

    # Call the method and expect an exception
    with pytest.raises(StorageError) as excinfo:
        adapter.save_prediction(prediction)

    # Verify the error message
    assert "Error saving prediction: Database error" in str(excinfo.value)

    # Verify the session was used correctly
    mock_session.add.assert_called_once()
    mock_session.__exit__.assert_called_once()


def test_get_prediction_success(adapter, mock_prediction_model, mock_record_model, mock_session):
    """Test successful retrieval of a prediction."""
    # Configure the session query
    mock_query = MagicMock()
    mock_query.filter_by.return_value = mock_query
    mock_query.first.return_value = mock_prediction_model
    mock_session.query.return_value = mock_query

    # Configure the prediction model to return a record
    mock_prediction_model.cleaned_record = mock_record_model

    # Call the method
    result = adapter.get_prediction("test-run-1")

    # Verify the result
    assert result is not None
    assert result.id == "test-pred-1"
    assert result.record_id == "test-id-1"
    assert result.value == 320201.58554044
    assert result.run_id == "test-run-1"
    assert result.status == PredictionStatus.COMPLETED

    # Verify the session was used correctly
    mock_session.query.assert_called_once()
    mock_session.__exit__.assert_called_once()


def test_get_prediction_error(adapter, mock_session):
    """Test error handling when retrieving a prediction."""
    # Configure the session to raise an exception
    mock_session.query.side_effect = SQLAlchemyError("Database error")

    # Call the method and expect an exception
    with pytest.raises(StorageError) as excinfo:
        adapter.get_prediction("test-run-1")

    # Verify the error message
    assert "Error getting prediction by run_id: Database error" in str(excinfo.value)

    # Verify the session was used correctly
    mock_session.__exit__.assert_called_once()
