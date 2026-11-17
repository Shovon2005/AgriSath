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


def test_global_importances_none_pipeline():
    # Calling with None or invalid pipeline must return safe default feature definitions without raising exception
    res = get_global_importances(None, top_k=4)
    assert len(res) == 4
    assert res[0]["importance"] > 0
    assert "narrative" in res[0]


def test_tree_explainer_cache_invalidation():
    from sklearn.ensemble import RandomForestClassifier
    from agrisathi.ml.explain import get_tree_explainer
    rf1 = RandomForestClassifier(n_estimators=5, random_state=1)
    rf1.fit([[1, 2], [3, 4]], [0, 1])
    rf2 = RandomForestClassifier(n_estimators=5, random_state=2)
    rf2.fit([[5, 6], [7, 8]], [0, 1])

    exp1 = get_tree_explainer(rf1)
    exp1_again = get_tree_explainer(rf1)
    assert exp1 is exp1_again  # cached

    exp2 = get_tree_explainer(rf2)
    assert exp2 is not exp1  # invalidated on new model



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


def test_reset_explainer_cache():
    from agrisathi.ml.explain import get_tree_explainer, reset_explainer_cache
    predictor = get_predictor()
    rf = predictor.pipeline.named_steps["model"]
    get_tree_explainer(rf)
    reset_explainer_cache()
    from agrisathi.ml import explain
    assert explain._EXPLAINER_CACHE is None
