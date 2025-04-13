"""Dagster resource for ML model."""
from typing import Any, Dict, List, Optional

import dagster as dg
import joblib
import numpy as np

from src.core.domain.exceptions import PredictionError


class ModelResource(dg.ConfigurableResource):
    """Resource for loading and using the ML model."""

    model_path: str
    _model: Optional[Any] = None

    def setup_for_execution(self, context) -> None:
        """Setup the resource for execution."""
        self._model = joblib.load(self.model_path)

    def teardown_after_execution(self, context) -> None:
        """Teardown the resource after execution."""
        self._model = None

    def predict(self, data: Dict[str, Any]) -> List[float]:
        """Make predictions using the loaded model.

        Args:
            data: The prepared data as a dictionary

        Returns:
            A list containing the predictions

        Raises:
            PredictionError: If there's an error during prediction
        """
        if self._model is None:
            self._model = joblib.load(self.model_path)

        try:
            # The model expects exactly 13 features:
            # - 8 numeric features: longitude, latitude, housing_median_age, total_rooms,
            #   total_bedrooms, population, households, median_income
            # - 5 one-hot encoded features for ocean_proximity
            expected_features = [
                "longitude",
                "latitude",
                "housing_median_age",
                "total_rooms",
                "total_bedrooms",
                "population",
                "households",
                "median_income",
                "ocean_proximity_<1H OCEAN",
                "ocean_proximity_INLAND",
                "ocean_proximity_ISLAND",
                "ocean_proximity_NEAR BAY",
                "ocean_proximity_NEAR OCEAN",
            ]

            # Create a list of values in the correct order
            feature_values = [data[feature] for feature in expected_features]

            # Convert to numpy array for prediction
            features = np.array(feature_values).reshape(1, -1)

            # Make prediction
            prediction = self._model.predict(features)[0]
            return [float(prediction)]
        except Exception as e:
            raise PredictionError(f"Error making prediction: {str(e)}") from e
