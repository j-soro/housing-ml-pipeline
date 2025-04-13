"""Domain entities for predictions."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

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

    id: str = Field(default_factory=lambda: str(uuid4()), description="ID of the prediction")
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

    @field_validator("value")
    @classmethod
    def validate_value(cls, v):
        """Validate prediction value is positive."""
        if v < 0:
            raise ValueError("Prediction value must be positive")
        return v

    @field_validator("record_id")
    @classmethod
    def validate_record_id(cls, v):
        """Validate record_id is not empty."""
        if not v:
            raise ValueError("Record ID cannot be empty")
        return v
