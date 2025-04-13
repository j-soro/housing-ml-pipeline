"""Dagster resource for PostgreSQL storage."""

from typing import Optional

from dagster import ConfigurableResource

from src.adapter.driven.storage.postgres_adapter import PostgresAdapter
from src.core.domain.entities.prediction import Prediction
from src.core.port.storage_port import (
    HousingRecord,
)


class PostgresResource(ConfigurableResource):
    """PostgreSQL resource for Dagster."""

    connection_url: str
    _adapter: Optional[PostgresAdapter] = None

    def setup_for_execution(self, context) -> None:
        """Setup the resource for execution."""
        self._adapter = PostgresAdapter(self.connection_url)
        self._adapter.setup()

    def teardown_after_execution(self, context) -> None:
        """Teardown the resource after execution."""
        # No cleanup needed, as we want to keep the adapter for API access
        pass

    def get_adapter(self) -> PostgresAdapter:
        """Get the PostgreSQL adapter."""
        if not self._adapter:
            self._adapter = PostgresAdapter(self.connection_url)
            self._adapter.setup()
        return self._adapter

    def save_housing_record(self, record: HousingRecord) -> str:
        """Save a housing record to storage."""
        return self.get_adapter().save_housing_record(record)

    def get_housing_record(self, record_id: str) -> Optional[HousingRecord]:
        """Get a housing record from storage."""
        return self.get_adapter().get_housing_record(record_id)

    def save_prediction(self, prediction: Prediction) -> str:
        """Save a prediction to storage."""
        return self.get_adapter().save_prediction(prediction)

    def get_prediction(self, prediction_id: str) -> Optional[Prediction]:
        """Get a prediction from storage."""
        return self.get_adapter().get_prediction(prediction_id)
