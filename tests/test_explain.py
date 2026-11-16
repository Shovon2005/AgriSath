"""
Unit tests for Explainable AI (XAI) feature attributions.
"""

from agrisathi.core.validator import validate_farm_input
from agrisathi.ml.predictor import get_predictor
from agrisathi.ml.explain import clean_feature_label, get_global_importances


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
