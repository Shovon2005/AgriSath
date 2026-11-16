"""
High-precision crop prediction service.
"""

from typing import Dict, Any, List
from pathlib import Path
import threading
import joblib
import pandas as pd

from agrisathi.config import Config
from agrisathi.core.exceptions import ModelNotFoundError, PredictionError
from agrisathi.core.schemas import (
    FEATURE_NAMES,
    CODE_TO_SOIL_TYPE,
    CODE_TO_GROWTH_STAGE,
    CODE_TO_WATER_SOURCE,
    canonical_soil_type,
    canonical_growth_stage,
    canonical_water_source,
)
from agrisathi.ml.explain import explain_local_prediction
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.ml.predictor")


class CropPredictor:
    """Thread-safe prediction service with lazy artifact loading."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path: Path = None):
        if self._initialized:
            return
        self.model_path = model_path or Config.MODEL_PATH
        self.pipeline = None
        self._load_model()
        self._initialized = True

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (useful for testing and artifact reloading)."""
        with cls._lock:
            cls._instance = None
        from agrisathi.ml.explain import reset_explainer_cache
        reset_explainer_cache()

    def reload(self, model_path: Path = None):
        """Reload the model pipeline from disk."""
        if model_path:
            self.model_path = model_path
        self._load_model()
        from agrisathi.ml.explain import reset_explainer_cache
        reset_explainer_cache()

    def _load_model(self):
        if not self.model_path.exists():
            raise ModelNotFoundError(
                f"Trained model artifact not found at {self.model_path}. Please run training first."
            )
        try:
            self.pipeline = joblib.load(self.model_path)
            logger.info("Successfully loaded crop recommendation model from %s", self.model_path)
        except Exception as e:
            raise ModelNotFoundError(f"Failed loading model artifact: {e}") from e

    def predict(self, sanitized_data: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
        """
        Execute prediction, class probability ranking, and local explainability.
        """
        if self.pipeline is None:
            self._load_model()

        try:
            # Prepare row formatted with string categoricals expected by pipeline
            row = {}
            for col in FEATURE_NAMES:
                val = sanitized_data[col]
                if col == "soil_type":
                    val = canonical_soil_type(sanitized_data.get("soil_type_label", val))
                elif col == "growth_stage":
                    val = canonical_growth_stage(sanitized_data.get("growth_stage_label", val))
                elif col == "water_source_type":
                    val = canonical_water_source(sanitized_data.get("water_source_type_label", val))
                row[col] = val

            input_df = pd.DataFrame([row], columns=FEATURE_NAMES)

            # AI Prediction
            predicted_crop = self.pipeline.predict(input_df)[0]

            # Probabilities
            probs = self.pipeline.predict_proba(input_df)[0]
            classes = self.pipeline.classes_

            prob_pairs = [
                {
                    "crop": str(crop),
                    "probability": float(prob),
                    "percentage": round(float(prob) * 100, 1),
                }
                for crop, prob in zip(classes, probs)
            ]
            prob_pairs.sort(key=lambda x: x["probability"], reverse=True)
            for idx, p in enumerate(prob_pairs, start=1):
                p["rank"] = idx

            top_probabilities = prob_pairs[:top_k]
            top_three = prob_pairs[:3]

            # Primary confidence
            confidence = top_probabilities[0]["percentage"] if top_probabilities else 100.0

            # Local Explainability (SHAP)
            explanations = explain_local_prediction(
                pipeline=self.pipeline,
                input_df=input_df,
                predicted_crop=predicted_crop,
                top_k=top_k,
            )

            return {
                "recommended_crop": predicted_crop,
                "confidence": confidence,
                "probabilities": top_probabilities,
                "top_three": top_three,
                "important_features": explanations,
                "input_data": sanitized_data,
            }


        except Exception as e:
            logger.error("Inference failed: %s", e, exc_info=True)
            raise PredictionError(f"Prediction engine failed: {e}") from e


def get_predictor() -> CropPredictor:
    """Convenience getter for singleton predictor."""
    return CropPredictor()
