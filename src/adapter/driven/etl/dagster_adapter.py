"""Dagster adapter implementation."""
import logging
import os
from datetime import datetime
from typing import Literal, Optional
from urllib.parse import urlparse

from dagster import DagsterRunStatus
from dagster_graphql import DagsterGraphQLClient, DagsterGraphQLClientError

from src.config.settings import get_settings
from src.core.domain.entities.housing_record import HousingRecord
from src.core.domain.exceptions import PipelineError
from src.core.port.etl_port import ETLPort, PipelineRunProtocol

# Set up logger
logger = logging.getLogger(__name__)


class DagsterPipelineRun(PipelineRunProtocol):
    """Implementation of PipelineRunProtocol for Dagster."""

    def __init__(
        self,
        run_id: str,
        status: Literal["pending", "running", "completed", "failed"],
        start_time: datetime,
        end_time: Optional[datetime] = None,
        error_message: Optional[str] = None,
    ):
        self.id = run_id
        self.status = status
        self.started_at = start_time
        self.completed_at = end_time
        self.error = error_message


class DagsterETLAdapter(ETLPort):
    """Implementation of ETLPort using Dagster's GraphQL Python client."""

    def __init__(self) -> None:
        """Initialize the adapter with Dagster client."""

        # Use the provided URL or get it from environment variables
        self.dagster_url = os.getenv("DAGSTER_WEBSERVER_URL", "http://dagster-webserver:3000")
        logger.info(f"Initializing DagsterETLAdapter with URL: {self.dagster_url}")
        try:
            # Extract hostname from URL
            parsed_url = urlparse(self.dagster_url)
            hostname = parsed_url.netloc

            logger.info(f"Connecting to Dagster at hostname: {hostname}")
            self.client = DagsterGraphQLClient(hostname=hostname)
            logger.info("DagsterGraphQLClient initialized successfully")
        except DagsterGraphQLClientError as e:
            logger.error(f"Failed to initialize DagsterGraphQLClient: {str(e)}")
            raise
        self.settings = get_settings()

    async def start_prediction_pipeline(self, record: HousingRecord) -> str:
        """Start a prediction pipeline for a housing record.

        Args:
            record: The housing record to process

        Returns:
            str: Dagster run ID

        Raises:
            Exception: If there's an error starting the pipeline
        """
        try:
            logger.info(f"Starting prediction pipeline for record: {record.id}")
            # Convert record to dict for configuration
            raw_data = record.model_dump()
            raw_data.pop("id", None)  # Remove id if present

            # Log the Dagster URL we're using
            logger.info(f"Using Dagster URL: {self.dagster_url}")

            logger.info("Submitting job execution to Dagster: housing_prediction_job")
            # Submit job run with record data
            run_id = self.client.submit_job_execution(
                "housing_prediction_job",
                run_config={
                    "ops": {"raw_input": {"config": {"data": raw_data}}},
                    "resources": {
                        "postgres": {"config": {"connection_url": self.settings.database_url}},
                        "model": {"config": {"model_path": self.settings.MODEL_PATH}},
                    },
                },
            )

            logger.info(f"Job execution submitted successfully with run_id: {run_id}")
            return str(run_id)

        except DagsterGraphQLClientError as e:
            logger.error(f"DagsterGraphQLClientError when submitting job: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error when submitting job: {str(e)}")
            raise

    async def get_pipeline_status(self, run_id: str) -> str:
        """Get the status of a pipeline run.

        Args:
            run_id: The ID of the pipeline run to check

        Returns:
            str: "pending", "running", "completed", or "failed"

        Raises:
            Exception: If there's an error checking the pipeline status
        """
        try:
            logger.info(f"Getting status for run_id: {run_id}")
            # Get run status from Dagster
            status: DagsterRunStatus = self.client.get_run_status(run_id)

            # Map Dagster status to our status
            if status == DagsterRunStatus.SUCCESS:
                mapped_status = "completed"
            elif status == DagsterRunStatus.FAILURE or status == DagsterRunStatus.CANCELED:
                mapped_status = "failed"
            elif status == DagsterRunStatus.STARTED:
                mapped_status = "running"
            else:  # All other states (STARTING, MANAGED, QUEUED, NOT_STARTED, CANCELING)
                mapped_status = "pending"

            logger.info(f"Run status: {mapped_status}")
            return mapped_status

        except DagsterGraphQLClientError as e:
            logger.error(f"DagsterGraphQLClientError when getting run status: {str(e)}")
            raise PipelineError(f"Dagster client error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error when getting run status: {str(e)}")
            raise PipelineError(f"Error checking pipeline status: {str(e)}") from e
