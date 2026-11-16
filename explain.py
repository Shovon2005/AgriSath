"""
Backward-compatible wrapper for Explainable AI module.
Delegates to agrisathi.ml.predictor and agrisathi.ml.explain while preserving legacy DataFrame return signatures.
"""

from typing import Dict, Any
import pandas as pd
from agrisathi.core.validator import validate_farm_input
from agrisathi.ml.predictor import get_predictor
from agrisathi.ml.explain import clean_feature_label


def clean_feature_name(name: str) -> str:
    """Legacy feature name cleaner."""
    return clean_feature_label(name)


def explain_prediction(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy prediction and explanation signature.
    Returns dictionary with:
    - prediction: str
    - probabilities: pd.DataFrame with ['crop', 'probability']
    - important_features: pd.DataFrame with ['feature', 'importance']
    """
    sanitized = validate_farm_input(data)
    predictor = get_predictor()
    res = predictor.predict(sanitized)

    prob_df = pd.DataFrame(res["probabilities"])
    feat_df = pd.DataFrame(res["important_features"])

    return {
        "prediction": res["recommended_crop"],
        "probabilities": prob_df,
        "important_features": feat_df,
    }
