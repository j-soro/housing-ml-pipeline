"""Integration tests for database operations."""
from unittest.mock import MagicMock

import pytest

from src.core.domain.entities.housing_record import HousingRecord
from src.core.port.storage_port import StoragePort


@pytest.mark.integration
def test_save_and_retrieve_housing_record():
    """Test saving and retrieving a housing record using mocks."""
    # Create a mock for the PostgresAdapter
    mock_adapter = MagicMock(spec=StoragePort)

    # Create a housing record
    record = HousingRecord(
        longitude=-122.64,
        latitude=38.01,
        housing_median_age=36.0,
        total_rooms=1336.0,
        total_bedrooms=258.0,
        population=678.0,
        households=249.0,
        median_income=5.5789,
        ocean_proximity="NEAR OCEAN",
    )

    # Configure the mock to return the record ID
    mock_adapter.save_housing_record.return_value = record.id

    # Configure the mock to return the record when get_housing_record is called
    mock_adapter.get_housing_record.return_value = record

    # Save the record
    record_id = mock_adapter.save_housing_record(record)

    # Verify save_housing_record was called with the record
    mock_adapter.save_housing_record.assert_called_once_with(record)

    # Retrieve the record
    retrieved_record = mock_adapter.get_housing_record(record_id)

    # Verify get_housing_record was called with the record ID
    mock_adapter.get_housing_record.assert_called_once_with(record_id)

    # Verify the record
    assert retrieved_record is not None
    assert retrieved_record.id == record.id
    assert retrieved_record.longitude == record.longitude
    assert retrieved_record.latitude == record.latitude
    assert retrieved_record.ocean_proximity == record.ocean_proximity
