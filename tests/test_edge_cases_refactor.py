"""
Unit tests targeting edge cases, robustness, and refactored pathways.
"""

import math
import pandas as pd
import pytest
from agrisathi.core.schemas import safe_float, area_to_hectares
from agrisathi.advisory.comparison import build_crop_comparison_matrix
from agrisathi.reports.pdf_generator import generate_pdf_advisory_report
from agrisathi.utils.weather import fetch_weather_data
from agrisathi.ml.whatif import simulate_what_if
from agrisathi.ml.explain import generate_shap_waterfall
from agrisathi.advisory.engine import run_full_pipeline
from agrisathi.core.exceptions import ValidationError


def test_safe_float_booleans_and_special_values():
    # Booleans must NOT be parsed as 1.0 or 0.0
    assert safe_float(True, 99.0) == 99.0
    assert safe_float(False, 99.0) == 99.0
    assert safe_float(None, 42.0) == 42.0
    assert safe_float("   ", 42.0) == 42.0
    assert safe_float(float("nan"), 10.0) == 10.0
    assert safe_float(float("inf"), 10.0) == 10.0
    assert safe_float("85.5%", 0.0) == 85.5
    assert safe_float("0.0", 5.0) == 0.0
    assert safe_float(0, 5.0) == 0.0


def test_area_to_hectares_edge_cases():
    assert area_to_hectares(10.0, "hectare") == 10.0
    assert area_to_hectares(10.0, "acre") == round(10.0 * 0.404686, 4)
    assert area_to_hectares(10.0, "bigha") == round(10.0 * 0.1338, 4)
    # NaN and negative values must safely return standard 1.0 hectare
    assert area_to_hectares(float("nan"), "hectare") == 1.0
    assert area_to_hectares(-5.0, "hectare") == 1.0
    assert area_to_hectares(0.0, "hectare") == 1.0


def test_crop_comparison_polymorphism_and_nulls():
    # 1. String list input
    res_str = build_crop_comparison_matrix(["rice", "maize"], {"soil_type": "Loamy"})
    assert len(res_str["items"]) == 2
    assert res_str["items"][0]["crop"] == "Rice"
    assert res_str["items"][1]["crop"] == "Maize"

    # 2. Dict input with None and string percentage
    crops = [
        {"crop": "rice", "percentage": "88.5%"},
        {"crop": "wheat", "probability": 0.65},
        {"crop": "jute", "percentage": None, "probability": None},
        None,  # Null item must be safely skipped
    ]
    res_dict = build_crop_comparison_matrix(crops, {"soil_type": "Clay", "ph": 6.8})
    assert len(res_dict["items"]) == 3
    assert res_dict["items"][0]["confidence"] == 88.5
    assert res_dict["items"][1]["confidence"] == 65.0
    assert res_dict["items"][2]["confidence"] == 0.0


def test_pdf_report_with_null_confidence_and_strings():
    prediction = {
        "recommended_crop": "rice",
        "confidence": None,
        "input_data": {"farm_area": 2.0, "farm_area_unit": "acre"},
        "important_features": [{"feature": "Rainfall", "impact_percentage": "35%", "direction": "positive"}],
    }
    advisory = {
        "crop_profile": {"display_name": "Rice (Oryza sativa)"},
        "crop_comparison": {
            "comparison_rows": [
                {"rank": 1, "crop": "rice", "confidence": None},
                {"rank": 2, "crop": "maize", "confidence": "72.4%"},
            ]
        },
    }
    pdf_bytes = generate_pdf_advisory_report(prediction, advisory)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")


def test_weather_zero_coordinates_preserved():
    # Verify lat=0.0 and lon=0.0 are preserved and not replaced by default baseline coordinates
    weather = fetch_weather_data(location="Equator Test", latitude=0.0, longitude=0.0)
    assert weather["latitude"] == 0.0
    assert weather["longitude"] == 0.0


def test_api_weather_invalid_lat_lon_handling(client):
    # Non-numeric lat/lon should fall back without 500 error
    res = client.get("/api/v1/weather?lat=invalid&lon=corrupt")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "weather" in data


def test_api_history_invalid_limit(client):
    # Non-numeric limit should fall back to default limit without 500 error
    res = client.get("/api/v1/history?limit=not_a_number")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"


def test_whatif_rejects_boolean_values(valid_farm_payload):
    # What-If must reject boolean adjustments on numeric features
    with pytest.raises(ValidationError):
        simulate_what_if(valid_farm_payload, {"temperature": True})

    # What-If must reject boolean adjustments on categorical features
    with pytest.raises(ValidationError):
        simulate_what_if(valid_farm_payload, {"soil_type": False})


def test_shap_waterfall_narrative_includes_driving_factors(valid_farm_payload):
    from agrisathi.ml.predictor import get_predictor
    predictor = get_predictor()
    wf = generate_shap_waterfall(
        predictor.pipeline,
        pd.DataFrame([valid_farm_payload]),
        "rice",
        farm_data=valid_farm_payload,
    )
    narrative = wf["natural_language_explanation"]
    assert "Rice" in narrative
    assert "AI confidence" in narrative
    # Positives must be included in narrative
    assert "primary positive driving factors" in narrative


def test_run_full_pipeline_custom_predictor(valid_farm_payload):
    class MockPredictor:
        def predict(self, sanitized):
            return {
                "recommended_crop": "maize",
                "confidence": 99.0,
                "probabilities": [{"crop": "maize", "percentage": 99.0, "probability": 0.99}],
                "top_three": [{"crop": "maize", "percentage": 99.0, "probability": 0.99}],
                "important_features": [],
            }

    sanitized, pred, adv = run_full_pipeline(valid_farm_payload, predictor=MockPredictor())
    assert pred["recommended_crop"] == "maize"
    assert adv["crop_name"] == "maize"
