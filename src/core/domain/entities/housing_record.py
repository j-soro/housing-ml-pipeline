"""Domain entity for housing records."""
from __future__ import annotations

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

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
    ocean_proximity: str = Field(description="Proximity to the ocean")

    model_config = ConfigDict(validate_assignment=True, extra="forbid")
