"""
Unit and integration tests for ML pipeline and training.
"""

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


def test_train_and_evaluate_routine():
    # Run with small sample or test_size and save_artifacts=False
    pipeline, metrics = train_and_evaluate(test_size=0.3, random_state=42, save_artifacts=False)
    assert pipeline is not None
    assert metrics["accuracy"] > 0.95
    assert metrics["sample_count"] == 2200


def test_load_dataset_with_mixed_categoricals(tmp_path):
    """Ensure dataset loader normalizes string codes, floats, and lowercase names cleanly."""
    X_orig, y_orig = load_dataset()
    sample_df = X_orig.iloc[:10].copy()
    sample_df["label"] = y_orig.iloc[:10].copy()

    # Modify categoricals with string numbers, float numbers, and lowercase names
    sample_df.loc[0, "soil_type"] = "1"
    sample_df.loc[1, "soil_type"] = 2.0
    sample_df.loc[2, "soil_type"] = "sandy"
    sample_df.loc[0, "growth_stage"] = "1.0"
    sample_df.loc[1, "growth_stage"] = "flowering"
    sample_df.loc[0, "water_source_type"] = "4"
    sample_df.loc[1, "water_source_type"] = "canal"

    csv_file = tmp_path / "test_crop.csv"
    sample_df.to_csv(csv_file, index=False)

    X_loaded, y_loaded = load_dataset(csv_file)
    assert X_loaded["soil_type"].iloc[0] == "Clay"
    assert X_loaded["soil_type"].iloc[1] == "Loamy"
    assert X_loaded["soil_type"].iloc[2] == "Sandy"
    assert X_loaded["growth_stage"].iloc[0] == "Seedling"
    assert X_loaded["growth_stage"].iloc[1] == "Flowering"
    assert X_loaded["water_source_type"].iloc[0] == "River"
    assert X_loaded["water_source_type"].iloc[1] == "Canal"


