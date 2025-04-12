from datetime import datetime
from typing import Literal, Optional, Protocol

from src.core.domain.entities.housing_record import HousingRecord


class PipelineRunProtocol(Protocol):
    """Protocol defining what we expect from a pipeline run."""

    id: str
    status: Literal["pending", "running", "completed", "failed"]
    started_at: datetime
    completed_at: Optional[datetime]
    error: Optional[str]


class ETLPort(Protocol):
    """Protocol defining the interface for ETL pipeline operations."""

    async def start_prediction_pipeline(self, record: HousingRecord) -> str:
        """Start a prediction pipeline for a housing record.

        Args:
            record: The housing record to process

        Returns:
            str: The run ID for tracking the pipeline

        Raises:
            Exception: If there's an error starting the pipeline
        """
        ...

    async def get_pipeline_status(self, run_id: str) -> str:
        """Get the status of a pipeline run.

        Args:
            run_id: The ID of the pipeline run to check

        Returns:
            str: "pending", "running", "completed", or "failed"

        Raises:
            ValueError: If the run_id is invalid
            Exception: If there's an error checking the pipeline status
        """
        ...
