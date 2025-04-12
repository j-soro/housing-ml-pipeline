"""Prediction service implementation."""
import logging
from typing import Union

from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.entities.prediction import Prediction
from src.core.port.etl_port import ETLPort
from src.core.port.service_port import PredictionServicePort
from src.core.port.storage_port import StoragePort

# Set up logger
logger = logging.getLogger(__name__)


class PredictionService(PredictionServicePort):
    """Service for handling prediction requests."""

    def __init__(self, etl: ETLPort, storage: StoragePort):
        """Initialize the prediction service.

        Args:
            etl: The ETL port for running the prediction pipeline
            storage: The storage port for saving and retrieving records
        """
        self.etl = etl
        self.storage = storage
        logger.info("PredictionService initialized")

    async def submit_prediction_request(self, record: HousingRecord) -> str:
        """Submit a prediction request and trigger ETL pipeline.

        Args:
            record: Housing record to process

        Returns:
            str: Dagster run ID for tracking
        """
        try:
            # Start the ETL pipeline
            run_id = await self.etl.start_prediction_pipeline(record)

            # Store the record (without run_id)
            self.storage.save_housing_record(record)

            logger.info(f"Submitted prediction request with run_id: {run_id}")
            return run_id

        except Exception as e:
            logger.error(f"Error submitting prediction request: {str(e)}")
            raise

    async def get_prediction_result(self, run_id: str) -> Union[Prediction, str]:
        """Get the result of a prediction request.

        Args:
            run_id: Dagster run ID of the request to check

        Returns:
            Union[Prediction, str]: The prediction result or status string if not completed
        """
        try:
            # Get pipeline status
            status = await self.etl.get_pipeline_status(run_id)

            if status == "failed":
                logger.error("Pipeline failed")
                return "failed"

            # Pipeline completed, get prediction from storage
            if status == "completed":
                stored_prediction = self.storage.get_prediction(run_id)
                if not stored_prediction:
                    logger.error("Prediction not found in storage")
                    return "failed"

                return stored_prediction

            # For pending/running states, just return the status
            return status

        except Exception as e:
            logger.error(f"Error getting prediction result: {str(e)}")
            return "failed"
