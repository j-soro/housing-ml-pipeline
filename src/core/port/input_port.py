from __future__ import annotations

from typing import Optional, Protocol

from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.entities.prediction import PredictionStatus


class PredictionRequestProtocol(Protocol):
    """Protocol defining what we expect from a prediction request."""

    longitude: float
    latitude: float
    housing_median_age: float
    total_rooms: float
    total_bedrooms: float
    population: float
    households: float
    median_income: float
    ocean_proximity: str

    def to_housing_record(self) -> HousingRecord:
        """Convert to housing record."""
        ...


class PredictionResponseProtocol(Protocol):
    """Protocol defining what we expect from a prediction response."""

    run_id: str
    status: PredictionStatus
    prediction: Optional[float]


class PredictionStatusProtocol(Protocol):
    """Protocol defining what we expect from a prediction status."""

    run_id: str
    status: str
    error: Optional[str]


class InputPort(Protocol):
    """Protocol defining the interface for external input operations."""

    async def submit_prediction_request(
        self, request: PredictionRequestProtocol
    ) -> PredictionResponseProtocol:
        """Submit a request for house price prediction.

        Args:
            request: Validated prediction request data

        Returns:
            Response containing request tracking information

        Raises:
            ValueError: If the request data is invalid
            Exception: If there's an error processing the request
        """
        ...

    async def get_prediction_result(self, run_id: str) -> PredictionResponseProtocol:
        """Get the result of a prediction request.

        Args:
            run_id: The Dagster run ID of the prediction request to check

        Returns:
            Current status and result of the prediction request

        Raises:
            ValueError: If the run_id is invalid
            Exception: If there's an error retrieving the result
        """
        ...
