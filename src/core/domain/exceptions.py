"""Domain exceptions for the ML pipeline."""
from typing import Optional


class PipelineError(Exception):
    """Base exception for pipeline errors."""

    def __init__(
        self,
        message: str,
        details: Optional[dict] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.details = details or {}
        self.original_error = original_error


class DataValidationError(PipelineError):
    """Raised when data validation fails."""

    pass


class DataCleaningError(PipelineError):
    """Raised when data cleaning fails."""

    pass


class PredictionError(PipelineError):
    """Raised when prediction fails."""

    pass


class StorageError(PipelineError):
    """Raised when storage operations fail."""

    pass
