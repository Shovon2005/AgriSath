"""
Backward-compatibility root bridge for explain module.
Delegates to backend.explain.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from backend.explain import (  # noqa: F401
    clean_feature_name,
    explain_prediction,
)
