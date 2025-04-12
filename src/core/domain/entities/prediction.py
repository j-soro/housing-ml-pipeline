"""Domain entities for predictions."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from src.core.domain.entities.housing_record import HousingRecord


class PredictionStatus(str, Enum):
    """Status of a prediction request."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


class Prediction(BaseModel):
    """Prediction model."""

    record_id: str = Field(description="ID of the housing record this prediction is for")
    value: float = Field(description="Predicted house price value")
    created_at: datetime = Field(description="When the prediction was created")
    status: PredictionStatus = Field(
        default=PredictionStatus.PENDING, description="Current status of the prediction"
    )
    record: Optional[HousingRecord] = Field(
        None, description="The housing record this prediction is for"
    )
    error: Optional[str] = Field(None, description="Error message if prediction failed")
    run_id: Optional[str] = Field(None, description="Dagster run ID that generated this prediction")

    @classmethod
    def create(
        cls,
        prediction_id: str,
        status: PredictionStatus = PredictionStatus.PENDING,
        value: Optional[float] = None,
        record: Optional[HousingRecord] = None,
        error: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> "Prediction":
        """Create a new Prediction instance."""
        return cls(
            record_id=prediction_id,
            status=status,
            value=value,
            record=record,
            created_at=datetime.utcnow(),
            error=error,
            run_id=run_id,
        )
