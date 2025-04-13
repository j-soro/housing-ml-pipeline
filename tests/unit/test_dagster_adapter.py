"""Unit tests for DagsterETLAdapter."""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from dagster import DagsterRunStatus
from dagster_graphql import DagsterGraphQLClientError

from src.adapter.driven.etl.dagster_adapter import DagsterETLAdapter, DagsterPipelineRun
from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.exceptions import PipelineError


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
def mock_dagster_client():
    """Create a mock DagsterGraphQLClient."""
    client = MagicMock()
    # Configure the submit_job_execution method to return a string
    client.submit_job_execution = MagicMock(return_value="test-run-id")
    return client


@pytest.fixture
def mock_settings():
    """Create a mock settings."""
    settings = MagicMock()
    settings.database_url = "postgresql://fake:fake@localhost:5432/fake"
    settings.MODEL_PATH = "/path/to/model.joblib"
    return settings


@pytest.fixture
def adapter(mock_dagster_client, mock_settings):
    """Create a DagsterETLAdapter with mocked dependencies."""
    with patch(
        "src.adapter.driven.etl.dagster_adapter.DagsterGraphQLClient",
        return_value=mock_dagster_client,
    ), patch(
        "src.adapter.driven.etl.dagster_adapter.get_settings", return_value=mock_settings
    ), patch("src.adapter.driven.etl.dagster_adapter.urlparse") as mock_urlparse:
        # Configure urlparse to return a mock result
        mock_parsed_url = MagicMock()
        mock_parsed_url.netloc = "dagster-webserver:3000"
        mock_urlparse.return_value = mock_parsed_url

        # Create the adapter
        adapter = DagsterETLAdapter()

        # Verify the client was initialized correctly
        assert adapter.client is mock_dagster_client
        assert adapter.settings is mock_settings

        return adapter


def test_dagster_pipeline_run_creation():
    """Test creation of DagsterPipelineRun."""
    # Create a run with all parameters
    run = DagsterPipelineRun(
        run_id="test-run",
        status="completed",
        start_time=datetime.now(),
        end_time=datetime.now(),
        error_message="Test error",
    )

    # Verify the attributes
    assert run.id == "test-run"
    assert run.status == "completed"
    assert isinstance(run.started_at, datetime)
    assert isinstance(run.completed_at, datetime)
    assert run.error == "Test error"

    # Create a run with minimal parameters
    run = DagsterPipelineRun(run_id="test-run", status="pending", start_time=datetime.now())

    # Verify the attributes
    assert run.id == "test-run"
    assert run.status == "pending"
    assert isinstance(run.started_at, datetime)
    assert run.completed_at is None
    assert run.error is None


@pytest.mark.asyncio
async def test_start_prediction_pipeline_success(adapter, mock_housing_record, mock_dagster_client):
    """Test successful starting of a prediction pipeline."""
    # Call the method
    run_id = await adapter.start_prediction_pipeline(mock_housing_record)

    # Verify the result
    assert run_id == "test-run-id"

    # Verify the client was called correctly
    mock_dagster_client.submit_job_execution.assert_called_once()

    # Get the call arguments
    call_args = mock_dagster_client.submit_job_execution.call_args[0]
    call_kwargs = mock_dagster_client.submit_job_execution.call_args[1]

    # Verify the job name
    assert call_args[0] == "housing_prediction_job"

    # Verify the run config
    run_config = call_kwargs["run_config"]
    assert "ops" in run_config
    assert "raw_input" in run_config["ops"]
    assert "config" in run_config["ops"]["raw_input"]
    assert "data" in run_config["ops"]["raw_input"]["config"]

    # Verify the resources config
    assert "resources" in run_config
    assert "postgres" in run_config["resources"]
    assert "model" in run_config["resources"]
    assert (
        run_config["resources"]["postgres"]["config"]["connection_url"]
        == "postgresql://fake:fake@localhost:5432/fake"
    )
    assert run_config["resources"]["model"]["config"]["model_path"] == "/path/to/model.joblib"


@pytest.mark.asyncio
async def test_start_prediction_pipeline_dagster_error(
    adapter, mock_housing_record, mock_dagster_client
):
    """Test error handling when Dagster client raises an error."""
    # Configure the mock client to raise an exception
    mock_dagster_client.submit_job_execution.side_effect = DagsterGraphQLClientError(
        "Dagster error"
    )

    # Call the method and expect an exception
    with pytest.raises(DagsterGraphQLClientError) as excinfo:
        await adapter.start_prediction_pipeline(mock_housing_record)

    # Verify the error message
    assert "Dagster error" in str(excinfo.value)


@pytest.mark.asyncio
async def test_start_prediction_pipeline_unexpected_error(
    adapter, mock_housing_record, mock_dagster_client
):
    """Test error handling when an unexpected error occurs."""
    # Configure the mock client to raise an exception
    mock_dagster_client.submit_job_execution.side_effect = Exception("Unexpected error")

    # Call the method and expect an exception
    with pytest.raises(Exception) as excinfo:
        await adapter.start_prediction_pipeline(mock_housing_record)

    # Verify the error message
    assert "Unexpected error" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_pipeline_status_success(adapter, mock_dagster_client):
    """Test successful retrieval of pipeline status."""
    # Test all possible status mappings
    status_mappings = [
        (DagsterRunStatus.SUCCESS, "completed"),
        (DagsterRunStatus.FAILURE, "failed"),
        (DagsterRunStatus.CANCELED, "failed"),
        (DagsterRunStatus.STARTED, "running"),
        (DagsterRunStatus.STARTING, "pending"),
        (DagsterRunStatus.MANAGED, "pending"),
        (DagsterRunStatus.QUEUED, "pending"),
        (DagsterRunStatus.NOT_STARTED, "pending"),
        (DagsterRunStatus.CANCELING, "pending"),
    ]

    for dagster_status, expected_status in status_mappings:
        # Configure the mock client
        mock_dagster_client.get_run_status.return_value = dagster_status

        # Call the method
        status = await adapter.get_pipeline_status("test-run-id")

        # Verify the result
        assert status == expected_status

        # Verify the client was called correctly
        mock_dagster_client.get_run_status.assert_called_with("test-run-id")


@pytest.mark.asyncio
async def test_get_pipeline_status_dagster_error(adapter, mock_dagster_client):
    """Test error handling when Dagster client raises an error."""
    # Configure the mock client to raise an exception
    mock_dagster_client.get_run_status.side_effect = DagsterGraphQLClientError("Dagster error")

    # Call the method and expect an exception
    with pytest.raises(PipelineError) as excinfo:
        await adapter.get_pipeline_status("test-run-id")

    # Verify the error message
    assert "Dagster client error" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_pipeline_status_unexpected_error(adapter, mock_dagster_client):
    """Test error handling when an unexpected error occurs."""
    # Configure the mock client to raise an exception
    mock_dagster_client.get_run_status.side_effect = Exception("Unexpected error")

    # Call the method and expect an exception
    with pytest.raises(PipelineError) as excinfo:
        await adapter.get_pipeline_status("test-run-id")

    # Verify the error message
    assert "Error checking pipeline status" in str(excinfo.value)
