"""FastAPI handler implementation."""
from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status

from src.adapter.driving.fastapi.models import (
    PredictionCompletedResponse,
    PredictionFailedResponse,
    PredictionPendingResponse,
    PredictionSubmissionResponse,
)
from src.core.domain.entities.prediction import PredictionStatus
from src.core.port.input_port import (
    InputPort,
    PredictionRequestProtocol,
    PredictionResponseProtocol,
)
from src.core.service.prediction_service import PredictionService


class FastAPIHandler(InputPort):
    """FastAPI handler implementation."""

    def __init__(self, prediction_service: PredictionService):
        """Initialize the handler with the prediction service.

        Args:
            prediction_service: The prediction service to use
        """
        self._prediction_service = prediction_service

    async def submit_prediction_request(
        self, request: PredictionRequestProtocol
    ) -> PredictionSubmissionResponse:
        """Submit a prediction request."""
        try:
            # Convert request to housing record
            record = request.to_housing_record()

            # Submit to prediction service
            run_id = await self._prediction_service.submit_prediction_request(record)

            # Create response with PENDING status
            response = PredictionSubmissionResponse(
                run_id=run_id, status=PredictionStatus.PENDING, prediction=None
            )

            return response

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing prediction request: {str(e)}",
            ) from e

    async def get_prediction_result(self, run_id: str) -> PredictionResponseProtocol:
        """Get the prediction result."""
        try:
            result = await self._prediction_service.get_prediction_result(run_id)

            # If result is a string, it's a status from the ETL pipeline
            if isinstance(result, str):
                # Map ETL status to PredictionStatus
                status_map = {
                    "pending": PredictionStatus.PENDING,
                    "running": PredictionStatus.RUNNING,
                    "completed": PredictionStatus.COMPLETED,
                    "failed": PredictionStatus.FAILED,
                }

                # If failed, return failed response with error
                if result == "failed":
                    return PredictionFailedResponse(
                        run_id=run_id, status=PredictionStatus.FAILED, completed_at=datetime.now()
                    )

                # For pending/running, return pending response
                return PredictionPendingResponse(
                    run_id=run_id,
                    status=status_map.get(result, PredictionStatus.PENDING),
                )

            # If result is a Prediction, convert to appropriate response type
            if result.status == PredictionStatus.COMPLETED:
                return PredictionCompletedResponse(
                    run_id=result.run_id,
                    status=result.status,
                    prediction=result.value,
                    completed_at=result.created_at,
                )
            elif result.status == PredictionStatus.FAILED:
                return PredictionFailedResponse(
                    run_id=result.run_id, status=result.status, completed_at=result.created_at
                )
            else:
                return PredictionPendingResponse(
                    run_id=result.run_id,
                    status=result.status,
                )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error retrieving prediction result: {str(e)}"
            ) from e
