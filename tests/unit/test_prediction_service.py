from unittest.mock import AsyncMock

import pytest

from src.core.service.prediction_service import PredictionService


@pytest.fixture
def prediction_service(mock_etl_port, mock_storage_port):
    """Create a PredictionService instance with mocked dependencies."""
    # Configure the mock_etl_port for async methods
    mock_etl_port.get_pipeline_status = AsyncMock()

    return PredictionService(etl=mock_etl_port, storage=mock_storage_port)


@pytest.mark.asyncio
async def test_get_prediction_result_pipeline_failed(
    mock_etl_port, mock_storage_port, prediction_service
):
    """Test get_prediction_result when pipeline fails."""
    # Setup
    run_id = "test-run-id"
    mock_etl_port.get_pipeline_status.return_value = "failed"

    # Execute
    result = await prediction_service.get_prediction_result(run_id)

    # Assert
    assert result == "failed"
    mock_etl_port.get_pipeline_status.assert_called_once_with(run_id)
    mock_storage_port.get_prediction.assert_not_called()


@pytest.mark.asyncio
async def test_get_prediction_result_prediction_not_found(
    mock_etl_port, mock_storage_port, prediction_service
):
    """Test get_prediction_result when prediction is not found in storage."""
    # Setup
    run_id = "test-run-id"
    mock_etl_port.get_pipeline_status.return_value = "completed"
    mock_storage_port.get_prediction.return_value = None

    # Execute
    result = await prediction_service.get_prediction_result(run_id)

    # Assert
    assert result == "failed"
    mock_etl_port.get_pipeline_status.assert_called_once_with(run_id)
    mock_storage_port.get_prediction.assert_called_once_with(run_id)


@pytest.mark.asyncio
async def test_get_prediction_result_pending_status(
    mock_etl_port, mock_storage_port, prediction_service
):
    """Test get_prediction_result when pipeline is still pending."""
    # Setup
    run_id = "test-run-id"
    mock_etl_port.get_pipeline_status.return_value = "pending"

    # Execute
    result = await prediction_service.get_prediction_result(run_id)

    # Assert
    assert result == "pending"
    mock_etl_port.get_pipeline_status.assert_called_once_with(run_id)
    mock_storage_port.get_prediction.assert_not_called()


@pytest.mark.asyncio
async def test_get_prediction_result_running_status(
    mock_etl_port, mock_storage_port, prediction_service
):
    """Test get_prediction_result when pipeline is still running."""
    # Setup
    run_id = "test-run-id"
    mock_etl_port.get_pipeline_status.return_value = "running"

    # Execute
    result = await prediction_service.get_prediction_result(run_id)

    # Assert
    assert result == "running"
    mock_etl_port.get_pipeline_status.assert_called_once_with(run_id)
    mock_storage_port.get_prediction.assert_not_called()


@pytest.mark.asyncio
async def test_get_prediction_result_exception_handling(
    mock_etl_port, mock_storage_port, prediction_service
):
    """Test get_prediction_result when an exception occurs."""
    # Setup
    run_id = "test-run-id"
    mock_etl_port.get_pipeline_status.side_effect = Exception("Test error")

    # Execute
    result = await prediction_service.get_prediction_result(run_id)

    # Assert
    assert result == "failed"
    mock_etl_port.get_pipeline_status.assert_called_once_with(run_id)
    mock_storage_port.get_prediction.assert_not_called()
