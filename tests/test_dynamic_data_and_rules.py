"""
Comprehensive tests verifying dynamic data loading, elimination of hardcoded static data,
and verification of bug fixes across AgriSathi modules.
"""

import pytest
import json
from agrisathi.config import Config
from agrisathi.advisory.profiles import (
    get_agronomic_rules,
    get_fertilizer_conversions,
    get_risk_rules,
    reload_agronomic_rules,
)
from agrisathi.advisory.soil import assess_soil_health
from agrisathi.advisory.fertilizer import calculate_fertilizer_guidance
from agrisathi.advisory.irrigation import calculate_irrigation_advisory
from agrisathi.advisory.risk import assess_environmental_risks
from agrisathi.advisory.comparison import build_crop_comparison_matrix
from agrisathi.utils.weather import fetch_weather_data
from agrisathi.data.scenarios import (
    get_farm_scenarios,
    get_scenario_parameters_map,
    get_farm_scenario,
    save_farm_scenario,
    delete_farm_scenario,
)
from agrisathi.core.exceptions import ValidationError
from agrisathi.core.validator import validate_farm_input
from agrisathi.ml.whatif import simulate_what_if
from agrisathi.ml.explain import generate_shap_waterfall


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


def test_dynamic_environmental_risk_rules():
    """Verify that environmental risk assessment dynamically utilizes thresholds from rules."""
    rules = get_agronomic_rules()
    orig_pest_sev = rules["environmental_risk_rules"]["pest"]["severe_pest_index"]

    try:
        # Dynamically lower severe pest index threshold to 15%
        rules["environmental_risk_rules"]["pest"]["severe_pest_index"] = 15.0
        r_rules = get_risk_rules()
        assert r_rules["pest"]["severe_pest_index"] == 15.0

        # Farm with pest pressure 20.0 should now trigger High pest risk
        payload = {"pest_pressure": 20.0, "frost_risk": 0.0, "temperature": 25.0, "humidity": 60.0}
        res = assess_environmental_risks(payload, "rice")
        assert res["high_risk_count"] >= 1
        assert any(m["hazard"] == "Pest & Insect Infestation" for m in res["risk_matrix"])
    finally:
        rules["environmental_risk_rules"]["pest"]["severe_pest_index"] = orig_pest_sev
        reload_agronomic_rules()


def test_all_advisory_modules_null_safe():
    """Verify that passing dictionaries with None values does not crash any advisory module."""
    null_payload = {
        "N": None, "P": None, "K": None, "ph": None,
        "soil_moisture": None, "temperature": None, "humidity": None,
        "rainfall": None, "wind_speed": None, "frost_risk": None,
        "pest_pressure": None, "organic_carbon": None, "electrical_conductivity": None,
        "farm_area_ha": None, "expected_rainfall_24h": None,
    }

    soil_res = assess_soil_health(null_payload, "rice")
    assert "status" in soil_res
    assert "score" in soil_res

    fert_res = calculate_fertilizer_guidance(null_payload, "rice")
    assert "commercial_fertilizers" in fert_res

    irrig_res = calculate_irrigation_advisory(null_payload, "rice")
    assert "priority" in irrig_res
    assert "water_quantity_litres" in irrig_res

    risk_res = assess_environmental_risks(null_payload, "rice")
    assert "overall_risk_level" in risk_res

    comp_res = build_crop_comparison_matrix([{"crop": "rice"}], null_payload)
    assert len(comp_res["items"]) == 1


def test_whatif_categorical_human_readable_labels():
    """Verify What-If logs canonical human-readable labels instead of raw integer codes."""
    base_data = get_scenario_parameters_map()["rice"]
    res = simulate_what_if(base_data, {"soil_type": "Sandy"})
    assert "changes_applied" in res
    soil_ch = next(c for c in res["changes_applied"] if c["field"] == "soil_type")
    assert soil_ch["old_value"] in ("Clay", "Loamy")
    assert soil_ch["new_value"] == "Sandy"
    assert "Soil Type from" in res["insight_summary"]


def test_whatif_empty_string_ignored():
    """Verify What-If gracefully ignores empty string adjustments without parameter corruption."""
    base_data = get_scenario_parameters_map()["rice"]
    res = simulate_what_if(base_data, {"temperature": ""})
    # Empty string should not change temperature or be added as change
    assert not any(c["field"] == "temperature" for c in res["changes_applied"])


def test_scenario_key_validation():
    """Verify that saving scenarios with invalid keys raises ValidationError."""
    with pytest.raises(ValidationError):
        save_farm_scenario("", {"title": "Bad"})

    with pytest.raises(ValidationError):
        save_farm_scenario("   ", {"title": "Bad"})

    with pytest.raises(ValidationError):
        save_farm_scenario("invalid/key/path", {"title": "Bad"})

    with pytest.raises(ValidationError):
        save_farm_scenario("invalid key with spaces", {"title": "Bad"})


def test_scenario_save_and_deletion():
    """Verify dynamic scenario creation and deletion in the repository."""
    test_key = "temp_test_scenario"
    test_data = {
        "key": test_key,
        "title": "🌾 Temporary Scenario",
        "category": "Testing",
        "parameters": {"N": 90, "P": 40, "K": 40, "ph": 6.5, "soil_type": "Loamy"}
    }
    saved = save_farm_scenario(test_key, test_data)
    assert saved["key"] == test_key

    # Confirm it's retrievable
    retrieved = get_farm_scenario(test_key)
    assert retrieved is not None
    assert retrieved["title"] == "🌾 Temporary Scenario"

    # Delete scenario
    deleted = delete_farm_scenario(test_key)
    assert deleted is True

    # Confirm it no longer exists
    assert get_farm_scenario(test_key) is None
    # Deleting non-existent key returns False
    assert delete_farm_scenario("non_existent_key_999") is False


def test_waterfall_dynamic_fallback():
    """Verify SHAP waterfall graceful fallback generates dynamic steps from feature definitions."""
    import pandas as pd
    res = generate_shap_waterfall(None, pd.DataFrame(), "rice", top_k=4)
    assert res["base_value"] > 0
    assert res["final_value"] > res["base_value"]
    assert len(res["steps"]) == 4
    # Real feature names, not static dummy text
    step_features = [s["feature"] for s in res["steps"]]
    assert "Nitrogen" in step_features
    assert "Phosphorus" in step_features
    assert "<svg" in res["svg_plot"]
