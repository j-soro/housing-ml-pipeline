"""FastAPI application for the housing ML pipeline."""
import logging
from contextlib import asynccontextmanager
from typing import Union

from dependency_injector.wiring import inject
from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.adapter.driving.fastapi.handler import FastAPIHandler
from src.adapter.driving.fastapi.models import (
    ErrorResponse,
    PredictionCompletedResponse,
    PredictionFailedResponse,
    PredictionPendingResponse,
    PredictionRequest,
    PredictionSubmissionResponse,
)
from src.config.container import Container, container
from src.core.port.input_port import InputPort

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Wire the container with this module
container.wire(modules=[__name__])


@asynccontextmanager
async def lifespan(api: FastAPI):
    """Lifecycle manager for FastAPI application."""
    # Startup
    handler = FastAPIHandler(container.resolve(InputPort))
    api.state.handler = handler
    yield
    # Shutdown
    await container.dispose()


app = FastAPI(
    title="Housing Price Prediction API",
    description="API for predicting housing prices based on various features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Set lifespan context
app.lifespan = lifespan


def get_handler() -> InputPort:
    """Get the handler from the dependencies container."""
    dependencies = Container()
    return dependencies.input_port()


# Create a dependency for the handler
handler_dependency = Depends(get_handler)


@app.post(
    "/predictions",
    response_model=PredictionSubmissionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Submit a prediction request",
    description="Submit a new housing price prediction request",
    tags=["predictions"],
)
@inject
async def submit_prediction(
    request: PredictionRequest, handler: InputPort = handler_dependency
) -> JSONResponse:
    """Submit a prediction request."""
    result = await handler.submit_prediction_request(request)
    return JSONResponse(content=jsonable_encoder(result, exclude_none=True))


@app.get(
    "/predictions/{run_id}",
    response_model=Union[
        PredictionPendingResponse, PredictionCompletedResponse, PredictionFailedResponse
    ],
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Get prediction result",
    description="Get the result of a prediction request by its Dagster run ID",
    tags=["predictions"],
)
@inject
async def get_prediction(run_id: str, handler: InputPort = handler_dependency) -> JSONResponse:
    """Get the prediction result."""
    result = await handler.get_prediction_result(run_id)
    return JSONResponse(content=jsonable_encoder(result, exclude_none=True))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
