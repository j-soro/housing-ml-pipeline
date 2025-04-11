from datetime import datetime
from typing import Literal, Optional, Protocol, TypeVar

from src.core.domain.entities.housing_record import HousingRecord


class PipelineRunProtocol(Protocol):
    """Protocol defining what we expect from a pipeline run."""

    id: str
    status: Literal["pending", "running", "completed", "failed"]
    started_at: datetime
    completed_at: Optional[datetime]
    error: Optional[str]


# Type variable bounded by our protocol
RunT = TypeVar("RunT", bound=PipelineRunProtocol, covariant=True)


class ETLPort(Protocol[RunT]):
    """Protocol defining the interface for ETL pipeline operations."""

    async def start_prediction_pipeline(self, record: HousingRecord) -> RunT:
        """Start a prediction pipeline for a housing record.

        Args:
            record: The housing record to process

        Returns:
            Pipeline run information for tracking

        Raises:
            Exception: If there's an error starting the pipeline
        """
        ...

    async def get_pipeline_status(self, run_id: str) -> RunT:
        """Get the status of a pipeline run.

        Args:
            run_id: The ID of the pipeline run to check

        Returns:
            Current pipeline run status and metadata

        Raises:
            ValueError: If the run_id is invalid
            Exception: If there's an error checking the pipeline status
        """
        ...
