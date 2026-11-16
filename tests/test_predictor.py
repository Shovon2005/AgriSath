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
