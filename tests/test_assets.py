"""Tests for Dagster assets in the housing prediction pipeline."""
# Standard library imports
from typing import Any, Dict
from unittest.mock import MagicMock

# Third-party imports
import pytest
from dagster import ConfigurableResource, materialize

# Local imports
from src.adapter.driven.etl.assets import (
    cleaned_data,
    prediction_result,
    prepared_data,
    raw_input,
    stored_cleaned_data,
    stored_prediction_result,
)
from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.exceptions import DataValidationError, PredictionError, StorageError
from tests.test_base import BaseDagsterTest

# Sample test data from documentation
SAMPLE_INPUT_1: Dict[str, Any] = {
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

SAMPLE_INPUT_2: Dict[str, Any] = {
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

SAMPLE_INPUT_3: Dict[str, Any] = {
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

# Expected outputs from documentation
EXPECTED_OUTPUT_1 = 320201.58554044
EXPECTED_OUTPUT_2 = 58815.45033765
EXPECTED_OUTPUT_3 = 192575.77355635


# Mock resources for testing
class MockPostgresResource(ConfigurableResource):
    """Mock PostgreSQL resource for testing."""

    connection_url: str

    def setup_for_execution(self, context) -> None:
        """Setup the resource for execution."""
        pass

    def teardown_after_execution(self, context) -> None:
        """Teardown the resource after execution."""
        pass

    def save_housing_record(self, record):
        # For testing purposes, we'll use a mapping to return the expected record_id
        # based on the longitude and latitude values
        if record.longitude == -122.64 and record.latitude == 38.01:
            return "sample-1"
        elif record.longitude == -115.73 and record.latitude == 33.35:
            return "sample-2"
        elif record.longitude == -117.96 and record.latitude == 33.89:
            return "sample-3"
        return record.id

    def get_housing_record(self, record_id):
        return None

    def save_prediction(self, prediction):
        # For testing purposes, we'll return the record_id from the prediction
        return prediction.record_id

    def get_prediction(self, run_id):
        return None


class MockModelResource(ConfigurableResource):
    """Mock model resource for testing."""

    model_path: str

    def setup_for_execution(self, context) -> None:
        """Setup the resource for execution."""
        pass

    def teardown_after_execution(self, context) -> None:
        """Teardown the resource after execution."""
        pass

    def predict(self, data):
        # Return different prediction values based on the input data
        # Use multiple fields to determine which sample we're dealing with

        # Check for sample 1 (NEAR OCEAN)
        if (
            data.get("ocean_proximity_NEAR OCEAN") == 1
            and data.get("longitude") == -122.64
            and data.get("latitude") == 38.01
        ):
            return [EXPECTED_OUTPUT_1]

        # Check for sample 2 (INLAND)
        elif (
            data.get("ocean_proximity_INLAND") == 1
            and data.get("longitude") == -115.73
            and data.get("latitude") == 33.35
        ):
            return [EXPECTED_OUTPUT_2]

        # Check for sample 3 (<1H OCEAN)
        elif (
            data.get("ocean_proximity_<1H OCEAN") == 1
            and data.get("longitude") == -117.96
            and data.get("latitude") == 33.89
        ):
            return [EXPECTED_OUTPUT_3]

        # If we can't determine which sample it is, log a warning and return a default value
        else:
            print(f"Warning: Could not determine sample from data: {data}")
            return [EXPECTED_OUTPUT_1]


class TestAssets(BaseDagsterTest):
    """Tests for Dagster assets."""

    @pytest.mark.parametrize("sample_input", ["sample_input_1", "sample_input_2", "sample_input_3"])
    def test_raw_input(self, request, sample_input):
        """Test the raw_input asset."""
        input_data = request.getfixturevalue(sample_input)
        context = self.create_test_context(config={"data": input_data})
        result = raw_input(context)
        assert result == input_data

    @pytest.mark.parametrize("sample_input", ["sample_input_1", "sample_input_2", "sample_input_3"])
    def test_cleaned_data(self, request, sample_input):
        """Test the cleaned_data asset."""
        input_data = request.getfixturevalue(sample_input)
        context = self.create_test_context()
        result = cleaned_data(context, input_data)
        assert isinstance(result, HousingRecord)
        assert result.id == input_data["record_id"]
        assert result.longitude == input_data["longitude"]
        assert result.latitude == input_data["latitude"]
        assert result.ocean_proximity == input_data["ocean_proximity"]

    def test_cleaned_data_without_record_id(self, sample_input_1):
        """Test the cleaned_data asset with input that doesn't have a record_id."""
        input_data = sample_input_1.copy()
        input_data.pop("record_id")
        context = self.create_test_context()
        result = cleaned_data(context, input_data)
        assert isinstance(result, HousingRecord)
        assert result.id is not None
        assert result.longitude == input_data["longitude"]
        assert result.latitude == input_data["latitude"]
        assert result.ocean_proximity == input_data["ocean_proximity"]

    def test_cleaned_data_invalid_ocean_proximity(self, sample_input_1):
        """Test data cleaning with invalid ocean proximity."""
        input_data = sample_input_1.copy()
        input_data["ocean_proximity"] = "INVALID"
        context = self.create_test_context()
        with pytest.raises(DataValidationError):
            cleaned_data(context, input_data)

    def test_cleaned_data_invalid_numeric(self, sample_input_1):
        """Test data cleaning with invalid numeric values."""
        input_data = sample_input_1.copy()
        input_data["longitude"] = "not a number"
        context = self.create_test_context()
        with pytest.raises(DataValidationError):
            cleaned_data(context, input_data)

    @pytest.mark.parametrize("sample_input", ["sample_input_1", "sample_input_2", "sample_input_3"])
    def test_stored_cleaned_data(self, request, sample_input, mock_storage_port):
        """Test successful storage of cleaned data."""
        input_data = request.getfixturevalue(sample_input)

        # Configure mock to return the record_id directly
        mock_storage_port.save_housing_record = MagicMock(return_value=input_data["record_id"])

        # Define resources
        resources = {
            "postgres": mock_storage_port,
        }

        # Define run config with input values
        run_config = {"ops": {"raw_input": {"config": {"data": input_data}}}}

        # Materialize the assets
        result = materialize(
            [
                raw_input,
                cleaned_data,
                stored_cleaned_data,
            ],
            resources=resources,
            run_config=run_config,
        )

        # Verify the results
        assert result.success
        assert result.output_for_node("stored_cleaned_data")["record_id"] == input_data["record_id"]
        mock_storage_port.save_housing_record.assert_called_once()

    def test_stored_cleaned_data_error(self, sample_input_1, mock_storage_port):
        """Test error handling in stored_cleaned_data."""
        context = self.create_test_context()

        # Configure mock to raise error
        mock_storage_port.save_housing_record = MagicMock(
            side_effect=StorageError("Database error")
        )

        # First clean the data
        cleaned = cleaned_data(context, sample_input_1)

        with pytest.raises(StorageError):
            stored_cleaned_data(context, cleaned, mock_storage_port)

    @pytest.mark.parametrize("sample_input", ["sample_input_1", "sample_input_2", "sample_input_3"])
    def test_prepared_data(self, request, sample_input):
        """Test successful data preparation."""
        input_data = request.getfixturevalue(sample_input)
        context = self.create_test_context()

        # First clean the data
        cleaned = cleaned_data(context, input_data)

        # Then prepare it
        result = prepared_data(context, cleaned)
        assert result["longitude"] == input_data["longitude"]
        assert result["latitude"] == input_data["latitude"]

        # Check one-hot encoding
        proximity = input_data["ocean_proximity"]
        assert result[f"ocean_proximity_{proximity}"] == 1

        # Check other proximity values are 0
        other_proximities = ["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]
        for other in other_proximities:
            if other != proximity:
                assert result[f"ocean_proximity_{other}"] == 0

    @pytest.mark.parametrize("sample_input", ["sample_input_1", "sample_input_2", "sample_input_3"])
    def test_prediction_result(self, request, sample_input, mock_model_port):
        """Test successful prediction result."""
        input_data = request.getfixturevalue(sample_input)

        # Configure mock to return prediction as a list
        mock_model_port.predict = MagicMock(return_value=[input_data["median_house_value"]])

        # Define resources
        resources = {
            "model": mock_model_port,
        }

        # Define run config with input values
        run_config = {"ops": {"raw_input": {"config": {"data": input_data}}}}

        # Materialize the assets
        result = materialize(
            [
                raw_input,
                cleaned_data,
                prepared_data,
                prediction_result,
            ],
            resources=resources,
            run_config=run_config,
        )

        # Verify the results
        assert result.success
        assert result.output_for_node("prediction_result") == [input_data["median_house_value"]]
        mock_model_port.predict.assert_called_once()

    def test_prediction_result_error(self, sample_input_1, mock_model_port):
        """Test error handling in prediction_result."""
        context = self.create_test_context()

        # Configure mock to raise error
        mock_model_port.predict = MagicMock(side_effect=PredictionError("Model error"))

        # First clean and prepare the data
        cleaned = cleaned_data(context, sample_input_1)
        prepared = prepared_data(context, cleaned)

        with pytest.raises(PredictionError):
            prediction_result(context, mock_model_port, prepared)

    @pytest.mark.parametrize("sample_input", ["sample_input_1", "sample_input_2", "sample_input_3"])
    def test_stored_prediction_result(
        self, request, sample_input, expected_outputs, mock_storage_port, mock_model_port
    ):
        """Test successful storage of prediction result."""
        input_data = request.getfixturevalue(sample_input)

        # Configure mocks
        expected_value = expected_outputs[input_data["record_id"]]
        mock_model_port.predict = MagicMock(return_value=[expected_value])
        mock_storage_port.save_prediction = MagicMock(return_value=input_data["record_id"])

        # Define resources
        resources = {
            "model": mock_model_port,
            "postgres": mock_storage_port,
        }

        # Define run config with input values
        run_config = {"ops": {"raw_input": {"config": {"data": input_data}}}}

        # Materialize the assets
        result = materialize(
            [
                raw_input,
                cleaned_data,
                prepared_data,
                prediction_result,
                stored_cleaned_data,
                stored_prediction_result,
            ],
            resources=resources,
            run_config=run_config,
        )

        # Verify the results
        assert result.success
        assert (
            result.output_for_node("stored_prediction_result")["record_id"]
            == input_data["record_id"]
        )
        assert result.output_for_node("stored_prediction_result")["prediction"] == expected_value
        assert "run_id" in result.output_for_node("stored_prediction_result")
        mock_storage_port.save_prediction.assert_called_once()

    @pytest.mark.parametrize("sample_input", ["sample_input_1", "sample_input_2", "sample_input_3"])
    def test_stored_prediction_result_error(
        self, request, sample_input, expected_outputs, mock_storage_port, mock_model_port
    ):
        """Test error handling when storing prediction result."""
        input_data = request.getfixturevalue(sample_input)

        # Configure mocks
        expected_value = expected_outputs[input_data["record_id"]]
        mock_model_port.predict = MagicMock(return_value=[expected_value])
        mock_storage_port.save_prediction = MagicMock(side_effect=StorageError("Test error"))

        # Define resources
        resources = {
            "model": mock_model_port,
            "postgres": mock_storage_port,
        }

        # Define run config with input values
        run_config = {"ops": {"raw_input": {"config": {"data": input_data}}}}

        # Materialize the assets and expect failure
        with pytest.raises(PredictionError) as exc_info:
            materialize(
                [
                    raw_input,
                    cleaned_data,
                    prepared_data,
                    prediction_result,
                    stored_cleaned_data,
                    stored_prediction_result,
                ],
                resources=resources,
                run_config=run_config,
            )

        assert "Test error" in str(exc_info.value)
        mock_storage_port.save_prediction.assert_called_once()

    @pytest.mark.parametrize("sample_input", ["sample_input_1", "sample_input_2", "sample_input_3"])
    def test_housing_prediction_job(
        self, request, sample_input, expected_outputs, mock_storage_port, mock_model_port
    ):
        """Test the complete housing prediction job."""
        input_data = request.getfixturevalue(sample_input)

        # Configure mocks
        expected_value = expected_outputs[input_data["record_id"]]
        mock_model_port.predict = MagicMock(return_value=[expected_value])
        mock_storage_port.save_housing_record = MagicMock(return_value=input_data["record_id"])
        mock_storage_port.save_prediction = MagicMock(return_value=input_data["record_id"])

        # Define resources
        resources = {
            "model": mock_model_port,
            "postgres": mock_storage_port,
        }

        # Define run config with input values
        run_config = {"ops": {"raw_input": {"config": {"data": input_data}}}}

        # Materialize the assets
        result = materialize(
            [
                raw_input,
                cleaned_data,
                prepared_data,
                prediction_result,
                stored_cleaned_data,
                stored_prediction_result,
            ],
            resources=resources,
            run_config=run_config,
        )

        # Verify the results
        assert result.success
        assert (
            result.output_for_node("stored_prediction_result")["record_id"]
            == input_data["record_id"]
        )
        assert result.output_for_node("stored_prediction_result")["prediction"] == expected_value
        assert "run_id" in result.output_for_node("stored_prediction_result")
