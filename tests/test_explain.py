"""
Unit tests for Explainable AI (XAI) feature attributions.
"""

from agrisathi.core.validator import validate_farm_input
from agrisathi.ml.predictor import get_predictor
from agrisathi.ml.explain import (
    clean_feature_label,
    get_global_importances,
    explain_local_prediction,
)


def test_clean_feature_label():
    assert "Nitrogen" in clean_feature_label("numeric__N")
    assert "Loamy" in clean_feature_label("categorical__soil_type_Loamy")
    assert "Soil pH" in clean_feature_label("ph")


def test_explainability_structure(valid_farm_payload):
    sanitized = validate_farm_input(valid_farm_payload)
    predictor = get_predictor()
    result = predictor.predict(sanitized)

    explanations = result["important_features"]
    assert len(explanations) == 5

    for item in explanations:
        assert "feature" in item
        assert "importance" in item
        assert "impact_percentage" in item
        assert "direction" in item
        assert item["direction"] in ("positive", "negative")
        assert "narrative" in item


def test_fallback_global_importances():
    predictor = get_predictor()
    globals_imp = get_global_importances(predictor.pipeline, top_k=3)
    assert len(globals_imp) == 3
    assert globals_imp[0]["importance"] > 0


def test_explain_local_prediction_with_integer_categoricals(valid_farm_payload):
    import pandas as pd
    sanitized = validate_farm_input(valid_farm_payload)
    # sanitized has integer codes: soil_type=2, growth_stage=2, water_source_type=1
    df = pd.DataFrame([sanitized])
    predictor = get_predictor()
    # Call explain_local_prediction directly on dataframe with integer codes
    explanations = explain_local_prediction(predictor.pipeline, df, "rice", top_k=5)
    assert len(explanations) == 5
    # Should not fall back to global narrative ("key determinant across the farm model")
    assert any("strongly supported" in item["narrative"] or "suboptimal" in item["narrative"] for item in explanations)
