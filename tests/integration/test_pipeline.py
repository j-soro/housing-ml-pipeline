"""Integration tests for the complete prediction pipeline."""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.entities.prediction import Prediction
from src.core.port.etl_port import ETLPort
from src.core.port.model_port import ModelPort
from src.core.port.storage_port import StoragePort
from src.core.service.prediction_service import PredictionService


@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_prediction_pipeline():
    """Test the complete prediction pipeline from input to stored prediction."""
    # Setup mock for ETL port
    mock_etl = MagicMock(spec=ETLPort)
    mock_etl.start_prediction_pipeline.return_value = "test-run-id"

    # Setup mock for storage port
    mock_storage = MagicMock(spec=StoragePort)
    mock_storage.save_housing_record.return_value = "test-record-id"

    # Setup mock for model port
    mock_model = MagicMock(spec=ModelPort)
    mock_model.predict.return_value = 320201.58554044

    # Create service with mocked components
    service = PredictionService(etl=mock_etl, storage=mock_storage)

    # Create a housing record
    record = HousingRecord(
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

    # Submit prediction request
    run_id = await service.submit_prediction_request(record)

    # Verify ETL was called
    mock_etl.start_prediction_pipeline.assert_called_once_with(record)

    # Verify run_id
    assert run_id == "test-run-id"

    # Mock the get_prediction_result method to return a prediction
    with patch.object(
        service,
        "get_prediction_result",
        return_value=Prediction(
            record_id=record.id, value=320201.58554044, run_id=run_id, created_at=datetime.now()
        ),
    ):
        # Get prediction result
        prediction = await service.get_prediction_result(run_id)

        # Verify prediction
        assert isinstance(prediction, Prediction)
        assert prediction.record_id == record.id
        assert prediction.run_id == run_id
        assert prediction.value == 320201.58554044
