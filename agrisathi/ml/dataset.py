"""
Dataset loading and preprocessing for model training and evaluation.
"""

from pathlib import Path
from typing import Tuple
import pandas as pd

from agrisathi.config import Config
from agrisathi.core.exceptions import ValidationError
from agrisathi.core.schemas import (
    FEATURE_NAMES,
    CATEGORICAL_FEATURES,
    canonical_soil_type,
    canonical_growth_stage,
    canonical_water_source,
)


def load_dataset(csv_path: Path = None) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Load crop dataset and normalize categorical columns into string labels.
    Returns (X, y).
    """
    path = csv_path or Config.DATASET_PATH
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")

    df = pd.read_csv(path)

    # Ensure required columns exist
    missing_cols = [c for c in FEATURE_NAMES if c not in df.columns]
    if missing_cols:
        raise ValidationError(f"Dataset missing required feature columns: {missing_cols}")
    if "label" not in df.columns:
        raise ValidationError("Dataset missing target column 'label'")

    # Normalize all categorical columns into canonical string representations
    df["soil_type"] = df["soil_type"].apply(canonical_soil_type)
    df["growth_stage"] = df["growth_stage"].apply(canonical_growth_stage)
    df["water_source_type"] = df["water_source_type"].apply(canonical_water_source)

    X = df[FEATURE_NAMES].copy()
    y = df["label"].copy()

    return X, y
