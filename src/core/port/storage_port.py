from typing import Optional, Protocol

from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.entities.prediction import Prediction


class StoragePort(Protocol):
    """Protocol for storage operations."""

    def save_housing_record(self, record: HousingRecord) -> str:
        """Save a housing record to storage.

        Args:
            record: The housing record to save

        Returns:
            The ID of the saved record

        Raises:
            StorageError: If the record cannot be saved
        """
        ...

    def get_housing_record(self, record_id: str) -> Optional[HousingRecord]:
        """Get a housing record from storage.

        Args:
            record_id: ID of the record to retrieve

        Returns:
            The retrieved housing record or None if not found

        Raises:
            StorageError: If the record cannot be retrieved
        """
        ...

    def save_prediction(self, prediction: Prediction) -> str:
        """Save a prediction to storage.

        Args:
            prediction: The prediction to save

        Returns:
            The ID of the saved prediction

        Raises:
            StorageError: If the prediction cannot be saved
        """
        ...

    def get_prediction(self, run_id: str) -> Optional[Prediction]:
        """Get a prediction from storage by pipeline run execution id.

        Args:
            run_id: ID of the prediction pipeline run to retrieve

        Returns:
            The retrieved prediction or None if not found

        Raises:
            StorageError: If the prediction cannot be retrieved
        """
        ...
