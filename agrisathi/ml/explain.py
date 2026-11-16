"""
Explainable AI (XAI) engine using SHAP TreeExplainer for local feature contributions.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
import shap

from agrisathi.core.schemas import (
    FEATURE_MAP,
    FEATURE_DEFINITIONS,
    CATEGORICAL_FEATURES,
    canonical_soil_type,
    canonical_growth_stage,
    canonical_water_source,
)
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.ml.explain")

_EXPLAINER_CACHE = None


def clean_feature_label(raw_feature_name: str) -> str:
    """Format raw pipeline feature name into readable label."""
    name = raw_feature_name.replace("numeric__", "").replace("categorical__", "")

    # Handle one-hot encoded categoricals e.g. soil_type_Loamy
    for cat in CATEGORICAL_FEATURES:
        if name.startswith(cat + "_"):
            val = name.replace(cat + "_", "")
            spec = FEATURE_MAP.get(cat)
            display = spec.display_name if spec else cat.replace("_", " ").title()
            return f"{display}: {val}"

    spec = FEATURE_MAP.get(name)
    if spec:
        return f"{spec.display_name} ({spec.unit})" if spec.unit else spec.display_name
    return name.replace("_", " ").title()


def get_tree_explainer(rf_model):
    """Retrieve cached TreeExplainer instance, automatically invalidating if underlying model changes."""
    global _EXPLAINER_CACHE
    model_id = id(rf_model)
    if _EXPLAINER_CACHE is None or _EXPLAINER_CACHE[0] != model_id:
        _EXPLAINER_CACHE = (model_id, shap.TreeExplainer(rf_model))
    return _EXPLAINER_CACHE[1]


def explain_local_prediction(
    pipeline,
    input_df: pd.DataFrame,
    predicted_crop: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Compute local SHAP feature contributions for the specific farm input and predicted crop.
    """
    try:
        rf_model = pipeline.named_steps["model"]
        preprocessor = pipeline.named_steps["preprocessor"]

        classes = list(rf_model.classes_)
        if predicted_crop not in classes:
            return get_global_importances(pipeline, top_k)

        class_idx = classes.index(predicted_crop)

        # Transform single input with guaranteed canonical categorical strings
        clean_df = input_df.copy()
        if "soil_type" in clean_df.columns:
            clean_df["soil_type"] = clean_df["soil_type"].apply(canonical_soil_type)
        if "growth_stage" in clean_df.columns:
            clean_df["growth_stage"] = clean_df["growth_stage"].apply(canonical_growth_stage)
        if "water_source_type" in clean_df.columns:
            clean_df["water_source_type"] = clean_df["water_source_type"].apply(canonical_water_source)

        Xt = preprocessor.transform(clean_df)
        feature_names = preprocessor.get_feature_names_out()

        explainer = get_tree_explainer(rf_model)
        explanation = explainer(Xt)

        # Explanation values shape: (1, n_features, n_classes)
        if len(explanation.values.shape) == 3:
            shap_values = explanation.values[0, :, class_idx]
        else:
            shap_values = explanation.values[0, :]

        # Total absolute impact for normalization
        abs_sum = np.sum(np.abs(shap_values)) or 1.0

        contributions = []
        for feat_name, sv in zip(feature_names, shap_values):
            clean_name = clean_feature_label(feat_name)
            impact_pct = float(abs(sv) / abs_sum * 100)
            contributions.append({
                "feature": clean_name,
                "raw_name": feat_name,
                "shap_value": float(sv),
                "importance": float(abs(sv) / abs_sum),
                "impact_percentage": round(impact_pct, 1),
                "direction": "positive" if sv >= 0 else "negative",
                "narrative": (
                    f"{clean_name} strongly supported this crop recommendation."
                    if sv > 0 else
                    f"{clean_name} was slightly suboptimal for this crop."
                ),
            })

        # Sort by absolute SHAP impact descending
        contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        return contributions[:top_k]

    except Exception as e:
        logger.warning("Local SHAP calculation failed (%s); falling back to global importances.", e)
        return get_global_importances(pipeline, top_k)


def get_global_importances(pipeline, top_k: int = 5) -> List[Dict[str, Any]]:
    """Fallback using global Random Forest feature importances with robust error trapping."""
    try:
        rf_model = getattr(pipeline, "named_steps", {}).get("model") if pipeline else None
        preprocessor = getattr(pipeline, "named_steps", {}).get("preprocessor") if pipeline else None

        if rf_model is None or preprocessor is None:
            return [
                {
                    "feature": spec.display_name,
                    "raw_name": spec.name,
                    "shap_value": 1.0 / top_k,
                    "importance": 1.0 / top_k,
                    "impact_percentage": round(100.0 / top_k, 1),
                    "direction": "positive",
                    "narrative": f"{spec.display_name} is an essential farm indicator.",
                }
                for spec in FEATURE_DEFINITIONS[:top_k]
            ]

        feature_names = preprocessor.get_feature_names_out()
        importances = getattr(rf_model, "feature_importances_", None)
        if importances is None:
            importances = np.ones(len(feature_names))

        total = np.sum(importances) or 1.0
        items = []
        for name, imp in zip(feature_names, importances):
            items.append({
                "feature": clean_feature_label(name),
                "raw_name": name,
                "shap_value": float(imp),
                "importance": float(imp / total),
                "impact_percentage": round(float(imp / total * 100), 1),
                "direction": "positive",
                "narrative": f"{clean_feature_label(name)} is a key determinant across the farm model.",
            })

        items.sort(key=lambda x: x["importance"], reverse=True)
        return items[:top_k]
    except Exception as e:
        logger.warning("Global importance fallback extraction failed: %s", e)
        return [
            {
                "feature": spec.display_name,
                "raw_name": spec.name,
                "shap_value": 1.0 / top_k,
                "importance": 1.0 / top_k,
                "impact_percentage": round(100.0 / top_k, 1),
                "direction": "positive",
                "narrative": f"{spec.display_name} is an essential farm indicator.",
            }
            for spec in FEATURE_DEFINITIONS[:top_k]
        ]
