"""Unit tests for SklearnModelAdapter."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.adapter.driven.model.sklearn_adapter import SklearnModel, SklearnModelAdapter
from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.exceptions import PredictionError


@pytest.fixture
def mock_model():
    """Create a mock scikit-learn model."""
    model = MagicMock()
    model.predict.return_value = np.array([320201.58554044])
    return model


@pytest.fixture
def mock_sklearn_model():
    """Create a mock scikit-learn model."""
    model = MagicMock()
    # Configure the predict method to return a numpy array
    model.predict = MagicMock(return_value=np.array([320201.58554044]))
    return model


@pytest.fixture
def mock_housing_record():
    """Create a housing record."""
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
def mock_joblib():
    """Create a mock joblib."""
    with patch("src.adapter.driven.model.sklearn_adapter.joblib") as mock:
        yield mock


@pytest.fixture
def adapter(mock_path):
    """Create a SklearnModelAdapter with a mock model path."""
    with patch("src.adapter.driven.model.sklearn_adapter.Path", return_value=mock_path):
        return SklearnModelAdapter("mock_model_path.joblib")


@pytest.fixture
def mock_sklearn_model_wrapper(mock_sklearn_model):
    """Create a mock SklearnModel."""
    return SklearnModel(mock_sklearn_model)


def test_sklearn_model_predict(mock_sklearn_model):
    """Test that SklearnModel.predict calls the underlying model's predict method."""
    # Create a SklearnModel with the mock model
    sklearn_model = SklearnModel(mock_sklearn_model)

    # Create a test input
    test_input = np.array([[1, 2, 3]])

    # Call predict
    result = sklearn_model.predict(test_input)

    # Verify the model's predict method was called with the input
    mock_sklearn_model.predict.assert_called_once_with(test_input)

    # Verify the result is the same as what the mock returns
    assert np.array_equal(result, np.array([320201.58554044]))


@pytest.mark.asyncio
async def test_load_model_success(adapter, mock_joblib, mock_sklearn_model, mock_path):
    """Test successful loading of a model."""
    # Configure the mock
    mock_joblib.load.return_value = mock_sklearn_model

    # Call the method
    result = await adapter.load_model()

    # Verify joblib.load was called with the correct path
    mock_joblib.load.assert_called_once_with(mock_path)

    # Verify the result is a SklearnModel
    assert isinstance(result, SklearnModel)

    # Verify the model was stored in the adapter
    assert adapter._model is result


@pytest.mark.asyncio
async def test_load_model_file_not_found(adapter, mock_path):
    """Test error handling when model file doesn't exist."""
    # Configure the mock Path to return False for exists()
    mock_path.exists.return_value = False

    # Call the method and expect an exception
    with pytest.raises(FileNotFoundError) as excinfo:
        await adapter.load_model()

    # Verify the error message
    assert "Model file not found" in str(excinfo.value)


@pytest.mark.asyncio
async def test_load_model_error(adapter, mock_joblib, mock_path):
    """Test error handling when there's an error loading the model."""
    # Configure the mock to raise an exception
    mock_joblib.load.side_effect = Exception("Load error")

    # Call the method and expect an exception
    with pytest.raises(PredictionError) as excinfo:
        await adapter.load_model()

    # Verify the error message
    assert "Error loading model" in str(excinfo.value)


@pytest.mark.asyncio
async def test_predict_success(adapter, mock_sklearn_model_wrapper, mock_housing_record):
    """Test successful prediction."""
    # Set the model in the adapter
    adapter._model = mock_sklearn_model_wrapper

    # Call the method
    result = await adapter.predict(mock_housing_record)

    # Verify the result
    assert result == 320201.58554044

    # Verify the model's predict method was called
    mock_sklearn_model_wrapper.model.predict.assert_called_once()


@pytest.mark.asyncio
async def test_predict_auto_load(
    adapter, mock_joblib, mock_sklearn_model, mock_housing_record, mock_path
):
    """Test that predict automatically loads the model if not loaded."""
    # Configure the mock
    mock_joblib.load.return_value = mock_sklearn_model

    # Call the method
    result = await adapter.predict(mock_housing_record)

    # Verify the model was loaded
    mock_joblib.load.assert_called_once()

    # Verify the result
    assert result == 320201.58554044


@pytest.mark.asyncio
async def test_predict_error(adapter, mock_sklearn_model_wrapper, mock_housing_record):
    """Test error handling during prediction."""
    # Set the model in the adapter
    adapter._model = mock_sklearn_model_wrapper

    # Configure the model to raise an exception
    mock_sklearn_model_wrapper.model.predict = MagicMock(side_effect=Exception("Prediction error"))

    # Call the method and expect an exception
    with pytest.raises(PredictionError) as excinfo:
        await adapter.predict(mock_housing_record)

    # Verify the error message
    assert "Error making prediction" in str(excinfo.value)


def test_record_to_features(mock_housing_record):
    """Test conversion of housing record to feature array."""
    # Call the method
    features = SklearnModelAdapter._record_to_features(mock_housing_record)

    # Verify the result is a numpy array
    assert isinstance(features, np.ndarray)

    # Verify the shape (8 numeric features + 5 one-hot encoded ocean proximity)
    assert features.shape == (13,)

    # Verify some specific values
    assert features[0] == -122.64  # longitude
    assert features[1] == 38.01  # latitude
    assert features[8] == 0  # first ocean proximity bit
    assert features[12] == 1  # last ocean proximity bit (NEAR OCEAN)
