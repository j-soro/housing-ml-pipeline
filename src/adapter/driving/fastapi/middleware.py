"""Middleware for the FastAPI application."""
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.adapter.driving.fastapi.metrics import REQUEST_COUNT, REQUEST_LATENCY


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track Prometheus metrics."""

    async def dispatch(self, request: Request, call_next):
        """Process the request and track metrics."""
        # Start timer
        start_time = time.time()

        # Get the path (endpoint)
        path = request.url.path

        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method, endpoint=path, status=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(method=request.method, endpoint=path).observe(duration)

        return response
