"""
Comprehensive unit tests for Agronomic Advisory Engines.
"""

from agrisathi.core.validator import validate_farm_input
from agrisathi.advisory.soil import assess_soil_health
from agrisathi.advisory.fertilizer import calculate_fertilizer_guidance
from agrisathi.advisory.irrigation import calculate_irrigation_advisory
from agrisathi.advisory.risk import assess_environmental_risks
from agrisathi.advisory.engine import generate_full_advisory
from agrisathi.advisory.profiles import get_crop_profile


def test_soil_health_assessment_healthy(valid_farm_payload):
    sanitized = validate_farm_input(valid_farm_payload)
    profile = get_crop_profile("rice")
    result = assess_soil_health(sanitized, profile)

    assert result["status"] in ("Good", "Needs Attention")
    assert result["score"] >= 60
    assert len(result["issues"]) > 0


def test_soil_health_acidic_and_low_om():
    acidic_payload = {
        "ph": 4.2,
        "organic_matter": 0.8,
        "N": 15,
        "P": 10,
        "K": 12,
        "soil_type": "Sandy"
    }
    result = assess_soil_health(acidic_payload)
    assert result["status"] == "Poor"
    assert result["score"] < 50
    assert any("acidic" in i.lower() for i in result["issues"])
    assert any("organic matter" in i.lower() for i in result["issues"])
    assert len(result["corrective_actions"]) > 0


def test_fertilizer_recommendations_with_deficit(valid_farm_payload):
    sanitized = validate_farm_input(valid_farm_payload)
    # Low N, P, K
    sanitized["N"] = 20
    sanitized["P"] = 15
    sanitized["K"] = 10
    result = calculate_fertilizer_guidance(sanitized, "rice")

    assert result["deficits"]["N"] > 0
    assert result["deficits"]["P"] > 0
    assert result["deficits"]["K"] > 0
    assert result["commercial_fertilizers"]["urea_kg_ha"] > 0
    assert result["commercial_fertilizers"]["dap_kg_ha"] > 0
    assert result["commercial_fertilizers"]["mop_kg_ha"] > 0
    assert len(result["application_schedule"]) == 3


def test_irrigation_high_priority_dry_soil():
    dry_payload = {
        "soil_moisture": 11.0,
        "temperature": 35.0,
        "humidity": 30.0,
        "rainfall": 5.0,
        "wind_speed": 7.0,
        "soil_type": "Sandy",
        "growth_stage": "Flowering"
    }
    result = calculate_irrigation_advisory(dry_payload, "rice")
    assert result["priority"] == "High"
    assert len(result["recommended_actions"]) >= 2


def test_risk_assessment_frost_and_pest():
    high_risk_payload = {
        "frost_risk": 85.0,
        "pest_pressure": 90.0,
        "temperature": 1.0,
        "humidity": 90.0,
        "wind_speed": 16.0,
        "urban_area_proximity": 2.0
    }
    result = assess_environmental_risks(high_risk_payload, "rice")
    assert result["overall_risk_level"] == "Critical"
    assert result["high_risk_count"] == 2
    assert len(result["risk_matrix"]) >= 3


def test_full_advisory_engine(valid_farm_payload):
    sanitized = validate_farm_input(valid_farm_payload)
    advisory = generate_full_advisory(sanitized, "rice")

    assert "soil" in advisory
    assert "fertilizer" in advisory
    assert "irrigation" in advisory
    assert "risks" in advisory
    assert advisory["crop_name"] == "rice"
