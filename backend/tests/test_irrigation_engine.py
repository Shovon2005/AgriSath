"""
Unit tests for Enhanced Smart Irrigation Advisory Engine (Module 3).
Verifies crop water requirement (ETc in mm/day), farm water volume in litres,
rainfall suppression, and next irrigation time scheduling.
"""

from agrisathi.advisory.irrigation import calculate_irrigation_advisory


def test_irrigation_high_priority_litres_calculation():
    dry_payload = {
        "soil_moisture": 10.0,
        "temperature": 32.0,
        "humidity": 45.0,
        "rainfall": 5.0,
        "wind_speed": 4.0,
        "soil_type": "Clay",
        "growth_stage": "Flowering",
        "farm_area_ha": 2.5,
        "expected_rainfall_24h": 0.0,
    }
    result = calculate_irrigation_advisory(dry_payload, "rice")

    assert result["priority"] == "High"
    assert "Immediate" in result["irrigation_required"]
    assert "within 24 hours" in result["next_irrigation_time"].lower()
    assert result["daily_water_requirement_mm"] > 0.0
    # 45 mm depth * 2.5 ha * 10,000 L = 1,125,000 Litres
    assert result["water_quantity_litres"] == 1125000
    assert result["water_quantity_m3"] == 1125.0
    assert result["farm_area_ha"] == 2.5


def test_irrigation_rainfall_suppression():
    dry_payload = {
        "soil_moisture": 14.0,
        "temperature": 28.0,
        "humidity": 65.0,
        "rainfall": 10.0,
        "wind_speed": 3.0,
        "soil_type": "Loamy",
        "growth_stage": "Vegetative",
        "farm_area_ha": 1.0,
        "expected_rainfall_24h": 25.0,  # Significant rain forecast
    }
    result = calculate_irrigation_advisory(dry_payload, "maize")

    assert result["rainfall_suppressed"] is True
    assert "Rain" in result["irrigation_required"]
    assert "Postpone" in result["next_irrigation_time"]
    assert result["water_quantity_litres"] == 0
    assert any("Rainfall Alert" in act for act in result["recommended_actions"])


def test_irrigation_adequate_moisture():
    moist_payload = {
        "soil_moisture": 30.0,
        "temperature": 24.0,
        "humidity": 80.0,
        "rainfall": 120.0,
        "wind_speed": 2.0,
        "soil_type": "Loamy",
        "growth_stage": "Vegetative",
        "farm_area_ha": 1.0,
        "expected_rainfall_24h": 0.0,
    }
    result = calculate_irrigation_advisory(moist_payload, "chickpea")

    assert result["priority"] == "Low"
    assert "No" in result["irrigation_required"]
    assert result["water_quantity_litres"] == 0
