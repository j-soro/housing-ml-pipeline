from datetime import datetime
from typing import Protocol, TypeVar

from src.core.domain.entities.housing_record import HousingRecord


class StorageRecordProtocol(Protocol):
    """Protocol defining what we expect from a stored housing record."""

    id: str
    record: HousingRecord
    created_at: datetime


class StoragePredictionProtocol(Protocol):
    """Protocol defining what we expect from a stored prediction."""

    id: str
    record_id: str
    prediction_value: float
    created_at: datetime


# Type variables bounded by our protocols
RecordT = TypeVar("RecordT", bound=StorageRecordProtocol)
PredictionT = TypeVar("PredictionT", bound=StoragePredictionProtocol)


class StoragePort(Protocol[RecordT, PredictionT]):
    """Protocol for storage operations."""

    def save_housing_record(self, record: RecordT) -> str:
        """Save a housing record to storage.

        Args:
            record: The housing record to save

        Returns:
            The ID of the saved record

        Raises:
            StorageError: If the record cannot be saved
        """
        ...

    def get_housing_record(self, record_id: str) -> RecordT:
        """Get a housing record from storage.

        Args:
            record_id: ID of the record to retrieve

        Returns:
            The retrieved housing record

        Raises:
            StorageError: If the record cannot be retrieved
        """
        ...

    def save_prediction(self, prediction: PredictionT) -> str:
        """Save a prediction to storage.

        Args:
            prediction: The prediction to save

        Returns:
            The ID of the saved prediction

        Raises:
            StorageError: If the prediction cannot be saved
        """
        ...

    def get_prediction(self, prediction_id: str) -> PredictionT:
        """Get a prediction from storage.

        Args:
            prediction_id: ID of the prediction to retrieve

        Returns:
            The retrieved prediction

        Raises:
            StorageError: If the prediction cannot be retrieved
        """
        ...
