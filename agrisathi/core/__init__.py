"""Core domain definitions and validation."""

from agrisathi.core.exceptions import (
    AgriSathiError,
    ValidationError,
    ModelNotFoundError,
    PredictionError,
    AdvisoryCalculationError,
    ReportGenerationError,
)
from agrisathi.core.schemas import (
    FEATURE_NAMES,
    FEATURE_DEFINITIONS,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    FEATURE_MAP,
    SOIL_TYPE_TO_CODE,
    CODE_TO_SOIL_TYPE,
    GROWTH_STAGE_TO_CODE,
    CODE_TO_GROWTH_STAGE,
    WATER_SOURCE_TO_CODE,
    CODE_TO_WATER_SOURCE,
)

__all__ = [
    "AgriSathiError",
    "ValidationError",
    "ModelNotFoundError",
    "PredictionError",
    "AdvisoryCalculationError",
    "ReportGenerationError",
    "FEATURE_NAMES",
    "FEATURE_DEFINITIONS",
    "CATEGORICAL_FEATURES",
    "NUMERIC_FEATURES",
    "FEATURE_MAP",
    "SOIL_TYPE_TO_CODE",
    "CODE_TO_SOIL_TYPE",
    "GROWTH_STAGE_TO_CODE",
    "CODE_TO_GROWTH_STAGE",
    "WATER_SOURCE_TO_CODE",
    "CODE_TO_WATER_SOURCE",
]
