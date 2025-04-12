"""Service port definitions."""
from typing import Protocol

from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.entities.prediction import Prediction


class PredictionServicePort(Protocol):
    """Interface for the prediction service."""

    async def submit_prediction_request(self, record: HousingRecord) -> str:
        """Submit a prediction request and trigger ETL pipeline.

        Args:
            record: Housing record to process

        Returns:
            str: Dagster run ID for tracking
        """
        ...

    async def get_prediction_result(self, run_id: str) -> Prediction:
        """Get the result of a prediction request.

        Args:
            run_id: Dagster run ID of the request to check

        Returns:
            Prediction: The prediction result
        """
        ...

    async def trigger_etl_pipeline(self, record_id: str) -> None:
        """Trigger the ETL pipeline for a record.

        Args:
            record_id: ID of the record to process
        """
        ...
