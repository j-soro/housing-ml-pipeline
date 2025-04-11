from typing import Any, Protocol, TypeVar

from src.core.domain.entities.housing_record import HousingRecord


class ModelProtocol(Protocol):
    """Protocol defining what we expect from an ML model."""

    def predict(self, x: Any) -> Any:
        """Make predictions using the model."""
        ...


# Type variable bounded by our model protocol
ModelT = TypeVar("ModelT", bound=ModelProtocol, covariant=True)


class ModelPort(Protocol[ModelT]):
    """Protocol defining the interface for ML model operations."""

    async def load_model(self) -> ModelT:
        """Load the ML model.

        Returns:
            The loaded model object that implements prediction

        Raises:
            FileNotFoundError: If the model file is not found
            Exception: If there's an error loading the model
        """
        ...

    async def predict(self, record: HousingRecord) -> float:
        """Make a prediction using the model.

        Args:
            record: The housing record to make a prediction for

        Returns:
            float: The predicted house value

        Raises:
            ValueError: If the record cannot be processed by the model
            Exception: If there's an error during prediction
        """
        ...
