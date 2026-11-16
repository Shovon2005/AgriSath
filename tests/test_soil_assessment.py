"""
Unit tests for Enhanced Soil Assessment Engine (Module 1).
Verifies fertility classification (Low, Medium, High), EC salinity checks,
OC organic carbon evaluations, deficiency/excess diagnosis, and improvement suggestions.
"""

import pytest
from agrisathi.advisory.soil import assess_soil_health


def test_soil_fertility_high():
    farm_data = {
        "N": 90.0,
        "P": 50.0,
        "K": 60.0,
        "ph": 6.8,
        "organic_matter": 4.0,
        "organic_carbon": 1.2,
        "electrical_conductivity": 0.5,
        "soil_type": "Loamy",
    }
    result = assess_soil_health(farm_data, "rice")
    assert result["fertility_class"] in ("High", "Medium")
    assert result["score"] >= 80
    assert result["electrical_conductivity"] == 0.5
    assert result["organic_carbon"] == 1.2
    assert "nutrients_analysis" in result
    assert result["nutrients_analysis"]["nitrogen"]["status"] == "Optimal"


def test_soil_fertility_low_and_deficiencies():
    farm_data = {
        "N": 15.0,
        "P": 10.0,
        "K": 12.0,
        "ph": 4.5,
        "organic_matter": 0.8,
        "organic_carbon": 0.3,
        "electrical_conductivity": 0.4,
        "soil_type": "Sandy",
    }
    result = assess_soil_health(farm_data, "rice")
    assert result["fertility_class"] == "Low"
    assert result["status"] == "Poor"
    assert len(result["deficiencies"]) >= 3
    assert any("Nitrogen" in d for d in result["deficiencies"])
    assert any("Phosphorus" in d for d in result["deficiencies"])
    assert any("lime" in a.lower() for a in result["corrective_actions"])


def test_soil_salinity_hazard():
    farm_data = {
        "N": 70.0,
        "P": 40.0,
        "K": 50.0,
        "ph": 7.8,
        "organic_matter": 2.5,
        "organic_carbon": 0.7,
        "electrical_conductivity": 4.8,  # Strongly saline
        "soil_type": "Clay",
    }
    result = assess_soil_health(farm_data, "rice")
    assert any("saline" in issue.lower() for issue in result["issues"])
    assert any("leaching" in action.lower() for action in result["corrective_actions"])
    assert result["nutrients_analysis"]["electrical_conductivity"]["status"] == "Saline"


def test_soil_nutrient_excesses():
    farm_data = {
        "N": 180.0,
        "P": 120.0,
        "K": 160.0,
        "ph": 7.0,
        "organic_matter": 3.0,
        "electrical_conductivity": 0.8,
        "soil_type": "Loamy",
    }
    result = assess_soil_health(farm_data, "rice")
    assert len(result["excesses"]) >= 2
    assert any("Nitrogen" in ex for ex in result["excesses"])
    assert any("lodging" in issue.lower() for issue in result["issues"])
