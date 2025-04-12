"""FastAPI request and response models."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from src.core.domain.entities.housing_record import HousingRecord, OceanProximity
from src.core.domain.entities.prediction import PredictionStatus


class PredictionRequest(BaseModel):
    """Request model for house price prediction."""

    longitude: float = Field(description="Longitude of the house location")
    latitude: float = Field(description="Latitude of the house location")
    housing_median_age: float = Field(description="Median age of houses in the block")
    total_rooms: float = Field(description="Total number of rooms in the block")
    total_bedrooms: float = Field(description="Total number of bedrooms in the block")
    population: float = Field(description="Total population in the block")
    households: float = Field(description="Total number of households in the block")
    median_income: float = Field(description="Median income of households in the block")
    ocean_proximity: OceanProximity = Field(description="Proximity to the ocean")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "longitude": -122.64,
                "latitude": 38.01,
                "housing_median_age": 36.0,
                "total_rooms": 1336.0,
                "total_bedrooms": 258.0,
                "population": 678.0,
                "households": 249.0,
                "median_income": 5.5789,
                "ocean_proximity": "NEAR OCEAN",
            }
        }
    )

    def to_housing_record(self) -> HousingRecord:
        """Convert request to housing record.

        Returns:
            HousingRecord: The housing record
        """
        return HousingRecord(
            longitude=self.longitude,
            latitude=self.latitude,
            housing_median_age=self.housing_median_age,
            total_rooms=self.total_rooms,
            total_bedrooms=self.total_bedrooms,
            population=self.population,
            households=self.households,
            median_income=self.median_income,
            ocean_proximity=self.ocean_proximity,
        )


# Base response model with common fields
class BasePredictionResponse(BaseModel):
    """Base response model for prediction requests."""

    run_id: str = Field(description="Dagster run ID for the prediction")
    status: PredictionStatus = Field(description="Status of the prediction")
    prediction: Optional[float] = Field(
        default=None, description="The prediction value if available"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "pending",
            }
        }
    )


# Response model for initial submission
class PredictionSubmissionResponse(BasePredictionResponse):
    """Response model for prediction request submission."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "pending",
            }
        }
    )


# Response model for pending/running status
class PredictionPendingResponse(BasePredictionResponse):
    """Response model for pending/running prediction requests."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "pending",
            }
        }
    )


# Response model for completed status
class PredictionCompletedResponse(BasePredictionResponse):
    """Response model for completed prediction requests."""

    completed_at: datetime = Field(description="When the prediction was completed")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "prediction_value": 320201.58,
                "completed_at": "2024-04-10T12:00:05Z",
            }
        }
    )


# Response model for failed status
class PredictionFailedResponse(BasePredictionResponse):
    """Response model for failed prediction requests."""

    completed_at: datetime = Field(description="When the prediction failed")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "failed",
                "error": "Error processing prediction",
                "completed_at": "2024-04-10T12:00:05Z",
            }
        }
    )


# Response model for not found status
class PredictionNotFoundResponse(BaseModel):
    """Response model for not found prediction requests."""

    detail: str = Field(description="Error message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"detail": "Prediction run not found: 123e4567-e89b-12d3-a456-426614174000"}
        }
    )


# Union type for all possible response types
PredictionResponse = Union[
    PredictionSubmissionResponse,
    PredictionPendingResponse,
    PredictionCompletedResponse,
    PredictionFailedResponse,
    PredictionNotFoundResponse,
]


# Error response model
class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(description="Error message")

    model_config = ConfigDict(json_schema_extra={"example": {"detail": "Invalid input data"}})
