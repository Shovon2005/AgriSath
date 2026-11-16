"""
Unit and integration tests for ML pipeline and training.
"""

from pathlib import Path
import pandas as pd
from agrisathi.config import Config
from agrisathi.ml.dataset import load_dataset
from agrisathi.ml.pipeline import build_pipeline
from agrisathi.ml.train import train_and_evaluate
from agrisathi.core.schemas import FEATURE_NAMES


def test_load_dataset():
    X, y = load_dataset()
    assert len(X) == 2200
    assert len(y) == 2200
    assert list(X.columns) == FEATURE_NAMES
    assert y.nunique() == 22
    # Categoricals mapped to strings
    assert isinstance(X["soil_type"].iloc[0], str)
    assert isinstance(X["growth_stage"].iloc[0], str)
    assert isinstance(X["water_source_type"].iloc[0], str)


def test_pipeline_build_and_fit():
    X, y = load_dataset()
    pipeline = build_pipeline(n_estimators=10, random_state=42)
    pipeline.fit(X.iloc[:100], y.iloc[:100])
    preds = pipeline.predict(X.iloc[:5])
    assert len(preds) == 5


def test_artifacts_exist():
    assert Config.MODEL_PATH.exists()
    assert Config.FEATURE_INFO_PATH.exists()
    assert Config.FEATURE_INFO_JSON_PATH.exists()
    assert Config.MODEL_METRICS_PATH.exists()
