"""Unit tests for core domain entities and service."""
from datetime import datetime
from typing import cast

import pytest

from src.core.domain.entities.housing_record import HousingRecord, OceanProximity
from src.core.domain.entities.prediction import Prediction, PredictionStatus


def test_housing_record_creation():
    """Test that HousingRecord correctly creates from valid data."""
    record = HousingRecord(
        longitude=-122.64,
        latitude=38.01,
        housing_median_age=36.0,
        total_rooms=1336.0,
        total_bedrooms=258.0,
        population=678.0,
        households=249.0,
        median_income=5.5789,
        ocean_proximity=cast(OceanProximity, "NEAR OCEAN"),
    )

    assert record.id is not None
    assert record.longitude == -122.64
    assert record.latitude == 38.01
    assert record.ocean_proximity == "NEAR OCEAN"
    assert isinstance(record.ocean_proximity, str)


def test_housing_record_validation():
    """Test that HousingRecord validates input data."""
    # Test invalid ocean_proximity
    with pytest.raises(ValueError):
        HousingRecord(
            longitude=-122.64,
            latitude=38.01,
            housing_median_age=36.0,
            total_rooms=1336.0,
            total_bedrooms=258.0,
            population=678.0,
            households=249.0,
            median_income=5.5789,
            ocean_proximity=cast(OceanProximity, "INVALID"),  # This should fail validation
        )

    # Test invalid longitude
    with pytest.raises(ValueError):
        HousingRecord(
            longitude=200,  # Invalid longitude
            latitude=38.01,
            housing_median_age=36.0,
            total_rooms=1336.0,
            total_bedrooms=258.0,
            population=678.0,
            households=249.0,
            median_income=5.5789,
            ocean_proximity=cast(OceanProximity, "NEAR OCEAN"),
        )

    # Test invalid latitude
    with pytest.raises(ValueError):
        HousingRecord(
            longitude=-122.64,
            latitude=100,  # Invalid latitude
            housing_median_age=36.0,
            total_rooms=1336.0,
            total_bedrooms=258.0,
            population=678.0,
            households=249.0,
            median_income=5.5789,
            ocean_proximity=cast(OceanProximity, "NEAR OCEAN"),
        )

    # Test negative housing_median_age
    with pytest.raises(ValueError):
        HousingRecord(
            longitude=-122.64,
            latitude=38.01,
            housing_median_age=-10,  # Invalid age
            total_rooms=1336.0,
            total_bedrooms=258.0,
            population=678.0,
            households=249.0,
            median_income=5.5789,
            ocean_proximity=cast(OceanProximity, "NEAR OCEAN"),
        )


def test_prediction_creation():
    """Test that Prediction correctly creates from valid data."""
    prediction = Prediction(
        record_id="test-record", value=320201.58554044, run_id="test-run", created_at=datetime.now()
    )

    assert prediction.id is not None
    assert prediction.record_id == "test-record"
    assert prediction.value == 320201.58554044
    assert prediction.run_id == "test-run"
    assert prediction.created_at is not None
    assert isinstance(prediction.created_at, datetime)
    assert prediction.status == PredictionStatus.PENDING


def test_prediction_validation():
    """Test that Prediction validates input data."""
    # Test negative value
    with pytest.raises(ValueError):
        Prediction(
            record_id="test-record",
            value=-100,  # Invalid negative value
            run_id="test-run",
            created_at=datetime.now(),
        )

    # Test empty record_id
    with pytest.raises(ValueError):
        Prediction(
            record_id="",  # Invalid empty record_id
            value=320201.58554044,
            run_id="test-run",
            created_at=datetime.now(),
        )
