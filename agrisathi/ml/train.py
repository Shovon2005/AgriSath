"""
Training script for AgriSathi crop recommendation model.
"""

import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from agrisathi.config import Config
from agrisathi.core.schemas import FEATURE_NAMES
from agrisathi.ml.dataset import load_dataset
from agrisathi.ml.pipeline import build_pipeline
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.ml.train")


def train_and_evaluate(
    test_size: float = 0.20,
    random_state: int = 42,
    save_artifacts: bool = True,
):
    """Train Random Forest classifier on dataset and save artifacts."""
    logger.info("Loading crop dataset...")
    X, y = load_dataset()
    logger.info("Dataset loaded with shape: %s, target classes: %d", X.shape, y.nunique())

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    logger.info("Building model pipeline...")
    pipeline = build_pipeline(random_state=random_state)

    logger.info("Training pipeline...")
    pipeline.fit(X_train, y_train)

    logger.info("Evaluating on test split...")
    y_pred = pipeline.predict(X_test)
    accuracy = float(accuracy_score(y_test, y_pred))
    report = classification_report(y_test, y_pred, output_dict=True)

    logger.info("Evaluation Complete. Accuracy: %.4f (%.2f%%)", accuracy, accuracy * 100)

    metrics = {
        "accuracy": accuracy,
        "sample_count": len(X),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "n_classes": int(y.nunique()),
        "classes": sorted(list(y.unique())),
        "classification_report": report,
    }

    if save_artifacts:
        Config.ensure_directories()

        # 1. Save pipeline
        joblib.dump(pipeline, Config.MODEL_PATH)
        logger.info("Saved model to %s", Config.MODEL_PATH)

        # 2. Save feature list (pickle for backward compatibility, json for standard config)
        joblib.dump(FEATURE_NAMES, Config.FEATURE_INFO_PATH)
        with open(Config.FEATURE_INFO_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(FEATURE_NAMES, f, indent=2)
        logger.info("Saved feature info to %s", Config.FEATURE_INFO_PATH)

        # 3. Save metrics artifact
        with open(Config.MODEL_METRICS_PATH, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        logger.info("Saved metrics to %s", Config.MODEL_METRICS_PATH)

        # 4. Reset predictor singleton to avoid serving stale cached model
        from agrisathi.ml.predictor import CropPredictor
        CropPredictor.reset_instance()

    return pipeline, metrics


if __name__ == "__main__":
    train_and_evaluate()
