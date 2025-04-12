"""Service port definitions."""
from typing import Protocol, Union

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

    async def get_prediction_result(self, run_id: str) -> Union[Prediction, str]:
        """Get the result of a prediction request.

        Args:
            run_id: Pipeline run ID of the request to check

        Returns:
            Union[Prediction, str]: Either the prediction result or the pipeline status
        """
        ...
