"""
Backward-compatibility root bridge for recommendation module.
Delegates to backend.recommendation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from backend.recommendation import (  # noqa: F401
    soil_assessment,
    irrigation_recommendation,
    fertilizer_recommendation,
    risk_assessment,
)
