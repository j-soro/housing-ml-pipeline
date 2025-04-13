"""Scikit-learn implementation of the ModelPort."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np

from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.exceptions import PredictionError
from src.core.port.model_port import ModelPort, ModelProtocol


class SklearnModel(ModelProtocol):
    """Wrapper for scikit-learn model to match our protocol."""

    def __init__(self, model: Any):
        self.model = model

    def predict(self, x: np.ndarray) -> np.ndarray:
        """Make predictions using the wrapped model."""
        return self.model.predict(x)


class SklearnModelAdapter(ModelPort[SklearnModel]):
    """Adapter for scikit-learn models."""

    def __init__(self, model_path: str):
        """Initialize the adapter with path to saved model.

        Args:
            model_path: Path to the saved scikit-learn model file
        """
        self.model_path = Path(model_path)
        self._model: SklearnModel | None = None

    async def load_model(self) -> SklearnModel:
        """Load the scikit-learn model from disk.

        Returns:
            Loaded model wrapped in our protocol

        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If there's an error loading the model
        """
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {self.model_path}")

        try:
            model = joblib.load(self.model_path)
            self._model = SklearnModel(model)
            return self._model
        except Exception as e:
            raise PredictionError(f"Error loading model: {str(e)}") from e

    async def predict(self, record: HousingRecord) -> float:
        """Make a prediction for a housing record.

        Args:
            record: The housing record to make prediction for

        Returns:
            float: The predicted house value

        Raises:
            ValueError: If model isn't loaded or record can't be processed
            PredictionError: If there's an error during prediction
        """
        if self._model is None:
            self._model = await self.load_model()

        try:
            # Convert record to feature array
            features = self._record_to_features(record)

            # Make prediction
            prediction = self._model.predict(features.reshape(1, -1))[0]

            return float(prediction)

        except Exception as e:
            raise PredictionError(f"Error making prediction: {str(e)}") from e

    @staticmethod
    def _record_to_features(record: HousingRecord) -> np.ndarray:
        """Convert a housing record to feature array for prediction.

        Args:
            record: Housing record to convert

        Returns:
            numpy array of features in correct order for model
        """
        # Convert ocean_proximity to one-hot encoding
        ocean_proximity_map = {
            "<1H OCEAN": [1, 0, 0, 0, 0],
            "INLAND": [0, 1, 0, 0, 0],
            "ISLAND": [0, 0, 1, 0, 0],
            "NEAR BAY": [0, 0, 0, 1, 0],
            "NEAR OCEAN": [0, 0, 0, 0, 1],
            "OUT OF REACH": [0, 0, 0, 0, 0],  # Default case
        }

        ocean_prox_encoded = (
            ocean_proximity_map[record.ocean_proximity]
            if record.ocean_proximity
            else ocean_proximity_map["OUT OF REACH"]
        )

        # Create feature array in correct order
        features = np.array(
            [
                record.longitude,
                record.latitude,
                record.housing_median_age,
                record.total_rooms,
                record.total_bedrooms,
                record.population,
                record.households,
                record.median_income,
                *ocean_prox_encoded,  # Unpack one-hot encoded ocean proximity
            ]
        )

        return features
