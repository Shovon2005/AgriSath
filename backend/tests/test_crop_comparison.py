"""
Unit tests for Crop Suitability Comparison Engine (Module 2).
Verifies Top-3 ranking, attribute evaluation (season, soil, pH, thermal fit),
and comparison matrix generation.
"""

from agrisathi.advisory.comparison import build_crop_comparison_matrix
from agrisathi.advisory.engine import generate_full_advisory


def test_build_crop_comparison_matrix():
    top_crops = [
        {"crop": "rice", "percentage": 82.5, "probability": 0.825},
        {"crop": "maize", "percentage": 10.2, "probability": 0.102},
        {"crop": "jute", "percentage": 4.1, "probability": 0.041},
        {"crop": "cotton", "percentage": 2.0, "probability": 0.020},
    ]
    farm_data = {
        "soil_type": "Clay",
        "season": "Kharif",
        "ph": 6.5,
        "rainfall": 200.0,
        "temperature": 25.0,
    }

    matrix = build_crop_comparison_matrix(top_crops, farm_data, limit=3)

    assert len(matrix["items"]) == 3
    assert matrix["items"][0]["crop"] == "Rice"
    assert matrix["items"][0]["rank"] == 1
    assert matrix["items"][0]["soil_fit"] == "Optimal"
    assert matrix["items"][0]["season_fit"] == "Optimal"
    assert matrix["items"][1]["crop"] == "Maize"
    assert matrix["items"][2]["crop"] == "Jute"
    assert "Rice" in matrix["summary"]
    assert "top_three" in matrix
    assert matrix["top_three"] == ["Rice", "Maize", "Jute"]


def test_comparison_empty_payload():
    matrix = build_crop_comparison_matrix([], {})
    assert matrix["items"] == []
    assert "No crop" in matrix["summary"]


def test_engine_integration_with_comparison(valid_farm_payload):
    top_crops = [
        {"crop": "rice", "percentage": 90.0},
        {"crop": "maize", "percentage": 8.0},
    ]
    advisory = generate_full_advisory(valid_farm_payload, "rice", top_crops=top_crops)
    assert "crop_comparison" in advisory
    assert len(advisory["crop_comparison"]["items"]) == 2
    assert advisory["crop_comparison"]["primary_crop"] == "Rice"
