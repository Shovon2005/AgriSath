"""
Comprehensive tests verifying dynamic data loading, elimination of hardcoded static data,
and verification of bug fixes across AgriSathi modules.
"""

import pytest
import json
from pathlib import Path
from agrisathi.config import Config
from agrisathi.advisory.profiles import (
    get_agronomic_rules,
    get_soil_properties,
    get_fertilizer_conversions,
    get_organic_guidelines,
    get_soil_thresholds,
    get_irrigation_rules,
    reload_agronomic_rules,
    get_crop_profiles,
    get_crop_profile,
)
from agrisathi.advisory.soil import assess_soil_health
from agrisathi.advisory.fertilizer import calculate_fertilizer_guidance
from agrisathi.advisory.irrigation import calculate_irrigation_advisory
from agrisathi.advisory.comparison import build_crop_comparison_matrix
from agrisathi.utils.weather import (
    get_regional_weather_baselines,
    reload_weather_baselines,
    fetch_weather_data,
)
from agrisathi.data.scenarios import (
    get_farm_scenarios,
    get_scenario_parameters_map,
    get_farm_scenario,
    reload_farm_scenarios,
)
from agrisathi.core.validator import validate_farm_input
from agrisathi.ml.whatif import simulate_what_if


def test_agronomic_rules_file_exists_and_valid():
    assert Config.AGRONOMIC_RULES_PATH.exists()
    with open(Config.AGRONOMIC_RULES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "soil_properties" in data
    assert "fertilizer_conversions" in data
    assert "soil_thresholds" in data
    assert "irrigation_rules" in data


def test_regional_weather_baselines_file_exists_and_valid():
    assert Config.REGIONAL_WEATHER_PATH.exists()
    with open(Config.REGIONAL_WEATHER_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "regions" in data
    regions = data["regions"]
    assert "punjab" in regions
    assert "bengal" in regions
    assert "maharashtra" in regions
    assert "rajasthan" in regions
    assert "kerala" in regions
    assert "default" in regions


def test_farm_scenarios_file_exists_and_valid():
    assert Config.SCENARIOS_PATH.exists()
    scenarios = get_farm_scenarios()
    assert len(scenarios) >= 4
    for key in ("rice", "chickpea", "cotton", "alert"):
        assert key in scenarios
        assert "parameters" in scenarios[key]
        assert "title" in scenarios[key]


def test_dynamic_rules_custom_threshold_modification():
    """Verify that updating agronomic rules changes the advisory behavior dynamically."""
    rules = get_agronomic_rules()
    orig_bag_weight = rules["fertilizer_conversions"].get("commercial_bag_weight_kg", 50.0)

    try:
        # Dynamically change bag weight to 25 kg
        rules["fertilizer_conversions"]["commercial_bag_weight_kg"] = 25.0
        conversions = get_fertilizer_conversions()
        assert conversions["commercial_bag_weight_kg"] == 25.0

        payload = {
            "N": 30.0,
            "P": 20.0,
            "K": 20.0,
            "farm_area_ha": 1.0,
            "ph": 6.5,
        }
        res = calculate_fertilizer_guidance(payload, "rice")
        assert res["commercial_bag_weight_kg"] == 25.0
    finally:
        # Revert
        rules["fertilizer_conversions"]["commercial_bag_weight_kg"] = orig_bag_weight
        reload_agronomic_rules()


def test_zero_values_not_masked_by_defaults():
    """Verify edge case: zero-values (0.0) for OC, EC, and rainfall are strictly respected."""
    raw_payload = {
        "N": 80,
        "P": 40,
        "K": 40,
        "temperature": 25.0,
        "humidity": 70.0,
        "ph": 6.5,
        "rainfall": 100.0,
        "soil_moisture": 25.0,
        "soil_type": "Loamy",
        "sunlight_exposure": 8.0,
        "wind_speed": 3.0,
        "co2_concentration": 400.0,
        "organic_matter": 2.5,
        "irrigation_frequency": 3,
        "crop_density": 15.0,
        "pest_pressure": 20.0,
        "fertilizer_usage": 100.0,
        "growth_stage": "Vegetative",
        "urban_area_proximity": 15.0,
        "water_source_type": "Groundwater",
        "frost_risk": 5.0,
        "water_usage_efficiency": 2.5,
        "organic_carbon": 0.0,
        "electrical_conductivity": 0.0,
        "expected_rainfall_24h": 0.0,
    }
    sanitized = validate_farm_input(raw_payload)
    assert sanitized["organic_carbon"] == 0.0
    assert sanitized["electrical_conductivity"] == 0.0
    assert sanitized["expected_rainfall_24h"] == 0.0

    soil_res = assess_soil_health(sanitized, "rice")
    assert soil_res["organic_carbon"] == 0.0
    assert soil_res["electrical_conductivity"] == 0.0

    irrig_res = calculate_irrigation_advisory(sanitized, "rice")
    assert irrig_res["expected_rainfall_24h"] == 0.0
    assert irrig_res["rainfall_suppressed"] is False


def test_comparison_matrix_empty_crops_safety():
    """Verify that build_crop_comparison_matrix handles empty input without KeyError."""
    empty_res = build_crop_comparison_matrix([], {"soil_type": "Loamy"})
    assert empty_res["items"] == []
    assert empty_res["comparison_rows"] == []
    assert empty_res["primary_crop"] == ""
    assert empty_res["top_three"] == []
    assert "summary" in empty_res


def test_whatif_categorical_switch_cleanly():
    """Verify What-If updates categorical variables and recalculates probability shifts."""
    base_data = get_scenario_parameters_map()["rice"]
    res = simulate_what_if(base_data, {"soil_type": "Sandy", "rainfall": 25.0})
    assert "baseline_crop" in res
    assert "simulated_crop" in res
    assert "changes_applied" in res
    assert any(c["field"] == "soil_type" for c in res["changes_applied"])
    assert any(c["field"] == "rainfall" for c in res["changes_applied"])
    assert len(res["probability_shifts"]) > 0


def test_weather_dynamic_state_baseline_matching():
    """Verify that entering different states resolves to their dynamic baselines when offline."""
    w_punjab = fetch_weather_data(location="Punjab, India")
    assert w_punjab["temperature"] == 22.0 or w_punjab["status"] == "online"

    w_rajasthan = fetch_weather_data(location="Rajasthan Desert")
    assert w_rajasthan["temperature"] == 32.0 or w_rajasthan["status"] == "online"

    w_kerala = fetch_weather_data(location="Kerala Backwaters")
    assert w_kerala["temperature"] == 28.0 or w_kerala["status"] == "online"
