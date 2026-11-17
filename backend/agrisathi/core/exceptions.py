"""
Custom domain exceptions for AgriSathi.
"""


class AgriSathiError(Exception):
    """Base exception for all AgriSathi operations."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(AgriSathiError):
    """Raised when user input fails domain schema validation."""
    pass


class ModelNotFoundError(AgriSathiError):
    """Raised when machine learning artifacts cannot be loaded."""
    pass


class PredictionError(AgriSathiError):
    """Raised during model prediction failure."""
    pass


class AdvisoryCalculationError(AgriSathiError):
    """Raised when agronomic calculations fail."""
    pass


class ReportGenerationError(AgriSathiError):
    """Raised when PDF report generation fails."""
    pass
