"""
Unit tests for CropPredictor service.
"""

from agrisathi.core.validator import validate_farm_input
from agrisathi.ml.predictor import CropPredictor, get_predictor


def test_predictor_singleton():
    p1 = get_predictor()
    p2 = CropPredictor()
    assert p1 is p2


def test_predict_rice_conditions(valid_farm_payload):
    sanitized = validate_farm_input(valid_farm_payload)
    predictor = get_predictor()
    result = predictor.predict(sanitized)

    assert result["recommended_crop"] in ("rice", "jute")
    top_crops = [p["crop"] for p in result["probabilities"]]
    assert "rice" in top_crops or "jute" in top_crops
    assert result["confidence"] > 40.0
    assert len(result["probabilities"]) == 5
    assert len(result["important_features"]) == 5


def test_predict_arid_chickpea(arid_farm_payload):
    sanitized = validate_farm_input(arid_farm_payload)
    predictor = get_predictor()
    result = predictor.predict(sanitized)

    assert result["recommended_crop"] in ("chickpea", "mothbeans", "lentil", "blackgram")
    assert len(result["probabilities"]) == 5
    assert len(result["important_features"]) == 5


def test_predict_float_and_lowercase_categoricals(valid_farm_payload):
    # Pass float codes and lowercase strings directly
    payload = dict(valid_farm_payload)
    payload["soil_type"] = 1.0  # Float 1.0
    payload["growth_stage"] = "vegetative"  # Lowercase string
    payload["water_source_type"] = "3.0"  # String float code
    predictor = get_predictor()
    result = predictor.predict(payload)
    assert result["recommended_crop"] in ("rice", "jute")
    assert result["confidence"] > 0
    assert len(result["important_features"]) == 5


def test_predictor_reset_and_reload():
    from agrisathi.ml import explain
    p1 = get_predictor()
    assert p1.pipeline is not None

    # Test reload
    p1.reload()
    assert p1.pipeline is not None
    assert explain._EXPLAINER_CACHE is None

    # Test reset_instance
    CropPredictor.reset_instance()
    assert CropPredictor._instance is None
    assert explain._EXPLAINER_CACHE is None
    p2 = get_predictor()
    assert p2 is not None
    assert p2.pipeline is not None

