"""Domain entity for housing records."""
from __future__ import annotations

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Valid categories for ocean_proximity
OceanProximity = Literal["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]


class HousingRecord(BaseModel):
    """Housing record model."""

    id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique identifier for the housing record"
    )
    longitude: float = Field(description="Longitude coordinate of the house location")
    latitude: float = Field(description="Latitude coordinate of the house location")
    housing_median_age: float = Field(description="Median age of houses in the block")
    total_rooms: float = Field(description="Total number of rooms in the block")
    total_bedrooms: float = Field(description="Total number of bedrooms in the block")
    population: float = Field(description="Total population in the block")
    households: float = Field(description="Total number of households in the block")
    median_income: float = Field(description="Median income of households in the block")
    ocean_proximity: OceanProximity = Field(description="Proximity to the ocean")

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v):
        """Validate longitude is within reasonable range."""
        if v < -180 or v > 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v):
        """Validate latitude is within reasonable range."""
        if v < -90 or v > 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("housing_median_age")
    @classmethod
    def validate_housing_median_age(cls, v):
        """Validate housing median age is positive."""
        if v < 0:
            raise ValueError("Housing median age must be positive")
        return v

    @field_validator("total_rooms", "total_bedrooms", "population", "households")
    @classmethod
    def validate_positive_numbers(cls, v):
        """Validate numeric fields are positive."""
        if v < 0:
            raise ValueError("Value must be positive")
        return v

    @field_validator("median_income")
    @classmethod
    def validate_median_income(cls, v):
        """Validate median income is positive."""
        if v < 0:
            raise ValueError("Median income must be positive")
        return v
