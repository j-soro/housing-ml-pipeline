"""Base test classes for Dagster assets."""
# Standard library imports
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

# Third-party imports
import dagster as dg
from dagster import Definitions, build_op_context
from dagster._core.test_utils import instance_for_test

# Local imports
from src.adapter.driven.etl.assets import (
    cleaned_data,
    prediction_result,
    prepared_data,
    raw_input,
    stored_cleaned_data,
    stored_prediction_result,
)


class BaseDagsterTest:
    """Base class for Dagster asset tests."""

    @staticmethod
    def create_test_context(config: Optional[Dict[str, Any]] = None) -> dg.OpExecutionContext:
        """Create a test context with optional config."""
        return build_op_context(config=config)

    @staticmethod
    def create_test_job(
        assets: List[dg.AssetsDefinition],
        resources: Optional[Dict[str, Any]] = None,
    ) -> dg.Definitions:
        """Create a test job with the given assets and resources."""

        @dg.job
        def test_job():
            for asset in assets:
                asset()

        return Definitions(
            assets=assets,
            resources=resources or {},
            jobs=[test_job],
        )

    @staticmethod
    def execute_test_job(
        job_def: dg.Definitions,
        run_config: Optional[Dict[str, Any]] = None,
    ) -> dg.ExecuteInProcessResult:
        """Execute a test job with the given configuration."""
        with instance_for_test():
            job = job_def.get_job_def("test_job")
            return job.execute_in_process(run_config=run_config or {})

    @staticmethod
    def create_mock_model_port(**kwargs: Any) -> Any:
        """Create a mock model port."""
        mock = MagicMock()
        mock.predict = AsyncMock(return_value=kwargs.get("predict_return", 0.0))
        mock.load_model = AsyncMock(return_value=kwargs.get("load_model_return", None))
        return mock

    @staticmethod
    def create_mock_storage_port(**kwargs: Any) -> Any:
        """Create a mock storage port."""
        mock = MagicMock()
        mock.save_housing_record = MagicMock(
            return_value=kwargs.get("save_housing_record_return", "test-id")
        )
        mock.get_housing_record = MagicMock(
            return_value=kwargs.get("get_housing_record_return", None)
        )
        mock.save_prediction = MagicMock(
            return_value=kwargs.get("save_prediction_return", "test-id")
        )
        mock.get_prediction = MagicMock(return_value=kwargs.get("get_prediction_return", None))
        return mock

    @staticmethod
    def get_all_assets() -> List[dg.AssetsDefinition]:
        """Get all asset definitions."""
        return [
            raw_input,
            cleaned_data,
            stored_cleaned_data,
            prepared_data,
            prediction_result,
            stored_prediction_result,
        ]
