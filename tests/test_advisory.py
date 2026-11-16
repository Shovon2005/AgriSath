"""
Comprehensive unit tests for Agronomic Advisory Engines and edge cases.
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


def test_soil_health_alkaline_and_nutrient_lockup():
    alkaline_payload = {
        "ph": 8.8,
        "organic_matter": 2.2,
        "N": 25,
        "P": 15,
        "K": 20,
        "soil_type": "Clay"
    }
    result = assess_soil_health(alkaline_payload)
    assert result["status"] == "Poor"
    assert any("alkaline" in i.lower() for i in result["issues"])
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


def test_fertilizer_recommendations_no_deficit():
    rich_farm = {"N": 150, "P": 100, "K": 100}
    result = calculate_fertilizer_guidance(rich_farm, "chickpea")
    assert result["deficits"]["N"] == 0.0
    assert result["deficits"]["P"] == 0.0
    assert result["deficits"]["K"] == 0.0
    assert result["commercial_fertilizers"]["urea_kg_ha"] == 0.0


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


def test_irrigation_moderate_and_surplus_conditions():
    # Moderate condition
    mod_payload = {
        "soil_moisture": 18.0,
        "temperature": 28.0,
        "humidity": 60.0,
        "rainfall": 10.0,
        "wind_speed": 3.0,
        "soil_type": "Loamy",
        "growth_stage": "Vegetative"
    }
    res_mod = calculate_irrigation_advisory(mod_payload, "chickpea")
    assert res_mod["priority"] in ("Low", "Medium")

    # Surplus condition
    surplus_payload = {
        "soil_moisture": 40.0,
        "temperature": 24.0,
        "humidity": 85.0,
        "rainfall": 180.0,
        "wind_speed": 2.0,
        "soil_type": "Clay",
        "growth_stage": "Vegetative"
    }
    res_surplus = calculate_irrigation_advisory(surplus_payload, "chickpea")
    assert res_surplus["priority"] == "Low"


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


def test_risk_assessment_moderate_and_heat():
    heat_payload = {
        "frost_risk": 40.0,
        "pest_pressure": 40.0,
        "temperature": 43.0,
        "humidity": 40.0,
        "wind_speed": 15.0,
        "urban_area_proximity": 3.0
    }
    result = assess_environmental_risks(heat_payload, "cotton")
    assert len(result["risk_matrix"]) >= 3


def test_full_advisory_engine(valid_farm_payload):
    sanitized = validate_farm_input(valid_farm_payload)
    advisory = generate_full_advisory(sanitized, "rice")

    assert "soil" in advisory
    assert "fertilizer" in advisory
    assert "irrigation" in advisory
    assert "risks" in advisory
    assert advisory["crop_name"] == "rice"


def test_irrigation_advisory_canonical_resolution():
    # Numeric soil_type code 3 (Sandy) and maturity growth stage 4
    payload = {
        "soil_moisture": 12.0,
        "temperature": 32.0,
        "humidity": 45.0,
        "rainfall": 10.0,
        "soil_type": 3,
        "growth_stage": 4,
        "water_source_type": 2,  # Rainwater
    }
    result = calculate_irrigation_advisory(payload, "chickpea")
    assert any("Sandy soil" in act for act in result["recommended_actions"])
    assert any("Rainwater harvesting reserves" in act for act in result["recommended_actions"])


def test_soil_health_canonical_texture_lookup():
    # Lowercase string and float code
    res_str = assess_soil_health({"ph": 6.5, "organic_matter": 3.0, "soil_type": "sandy"})
    res_code = assess_soil_health({"ph": 6.5, "organic_matter": 3.0, "soil_type": 3.0})
    assert res_str["soil_texture"] == "Sandy"
    assert res_code["soil_texture"] == "Sandy"
    assert res_str["texture_characteristics"]["water_retention"] == "Low"


def test_advisory_crop_parameter_polymorphism(valid_farm_payload):
    # assess_soil_health accepts string as positional 2nd arg
    res1 = assess_soil_health(valid_farm_payload, "rice")
    assert res1["status"] in ("Good", "Needs Attention")

    # assess_soil_health accepts keyword crop_name
    res2 = assess_soil_health(valid_farm_payload, crop_name="rice")
    assert res2["status"] in ("Good", "Needs Attention")

    # assess_soil_health accepts keyword crop_profile as string
    res3 = assess_soil_health(valid_farm_payload, crop_profile="rice")
    assert res3["status"] in ("Good", "Needs Attention")

    # fertilizer, irrigation, risk accept string crop_profile keyword
    f_res = calculate_fertilizer_guidance(valid_farm_payload, crop_profile="rice")
    assert "Urea" in " ".join(f_res["recommendations"]) or "sufficient" in " ".join(f_res["recommendations"]).lower()

    i_res = calculate_irrigation_advisory(valid_farm_payload, crop_profile="rice")
    assert i_res["priority"] in ("Low", "Medium", "High")

    r_res = assess_environmental_risks(valid_farm_payload, crop_profile="rice")
    assert r_res["overall_risk_level"] in ("Normal", "Elevated", "Critical")


def test_nutrient_excess_and_surplus_warnings():
    # Excess NPK in soil assessment
    excess_soil = assess_soil_health({"ph": 6.5, "organic_matter": 3.0, "N": 190, "P": 140, "K": 180, "soil_type": "Clay"})
    assert any("Nitrogen level is excessively high" in issue for issue in excess_soil["issues"])
    assert any("Phosphorus level is very high" in issue for issue in excess_soil["issues"])
    assert any("Potassium level is elevated" in issue for issue in excess_soil["issues"])

    # Pulse crop with nitrogen surplus
    fert_pulse = calculate_fertilizer_guidance({"N": 90, "P": 40, "K": 40}, crop_name="chickpea")
    assert any("inhibits Rhizobium nodulation" in rec for rec in fert_pulse["recommendations"])

    # General crop with nitrogen surplus
    fert_cereal = calculate_fertilizer_guidance({"N": 200, "P": 40, "K": 40}, crop_name="rice")
    assert any("substantial surplus" in rec for rec in fert_cereal["recommendations"])


def test_freezing_temperature_risk_and_clay_saturation():
    # Freezing temp even if frost_risk number is low
    cold_risk = assess_environmental_risks({"temperature": 2.0, "frost_risk": 15.0}, crop_name="rice")
    assert cold_risk["overall_risk_level"] in ("Elevated", "Critical")
    assert any("Frost / Freezing Injury" in m["hazard"] for m in cold_risk["risk_matrix"])

    # Saturated clay soil
    wet_clay = calculate_irrigation_advisory({"soil_moisture": 38.0, "soil_type": "Clay", "rainfall": 50.0}, crop_name="rice")
    assert any("Clay soil is heavily saturated" in act for act in wet_clay["recommended_actions"])


def test_phosphorus_and_potassium_surplus_and_tailored_schedule():
    # P surplus and K surplus
    fert_surplus = calculate_fertilizer_guidance(
        {"N": 100, "P": 120, "K": 130}, crop_name="rice"
    )
    # Target for rice is opt_p=45, opt_k=45 -> 120 > 45*1.5, 130 > 45*1.5
    recs = " ".join(fert_surplus["recommendations"])
    assert "Phosphorus" in recs and "notable surplus" in recs
    assert "Potassium" in recs and "notable surplus" in recs

    # Zero fertilizer need produces tailored schedule
    fert_zero = calculate_fertilizer_guidance(
        {"N": 150, "P": 80, "K": 80}, crop_name="rice"
    )
    assert len(fert_zero["application_schedule"]) == 1
    assert "No chemical fertilizer application required" in fert_zero["application_schedule"][0]

    # Only DAP and MOP needed (no Urea)
    fert_no_urea = calculate_fertilizer_guidance(
        {"N": 100, "P": 20, "K": 20}, crop_name="rice"
    )
    sched = fert_no_urea["application_schedule"]
    assert any("No synthetic nitrogen top-dressing required" in s for s in sched)


def test_environmental_risks_crop_thresholds_and_drought_waterlogging():
    # Sub-optimal temperature for tropical crop (Rice min_temp is 20.0°C; ambient temp is 12.0°C)
    cool_rice = assess_environmental_risks({"temperature": 12.0, "frost_risk": 5.0}, crop_name="rice")
    assert any("Cold Temperature Stress" in m["hazard"] for m in cool_rice["risk_matrix"])
    assert any("below minimum requirement" in r for r in cool_rice["risks"])

    # High temperature for cool crop (Apple max_temp is 28.0°C; ambient temp is 32.0°C)
    warm_apple = assess_environmental_risks({"temperature": 32.0}, crop_name="apple")
    assert any("Heat Stress" in m["hazard"] for m in warm_apple["risk_matrix"])
    assert any("exceeds optimal ceiling" in r for r in warm_apple["risks"])

    # Agricultural drought hazard
    drought_res = assess_environmental_risks(
        {"soil_moisture": 8.0, "rainfall": 20.0, "temperature": 30.0}, crop_name="rice"
    )
    assert drought_res["overall_risk_level"] in ("Elevated", "Critical")
    assert any("Agricultural Drought" in m["hazard"] for m in drought_res["risk_matrix"])

    # Waterlogging hazard
    waterlog_res = assess_environmental_risks(
        {"rainfall": 350.0, "soil_moisture": 35.0, "soil_type": "Clay"}, crop_name="maize"
    )
    assert any("Waterlogging / Hypoxia" in m["hazard"] for m in waterlog_res["risk_matrix"])


def test_irrigation_heavy_saturation_and_soil_crop_ph_actions():
    # Moisture > 45% triggers heavy water saturation directive
    saturated_irrig = calculate_irrigation_advisory({"soil_moisture": 52.0}, crop_name="rice")
    assert saturated_irrig["priority"] == "Low"
    assert "heavily water-saturated" in saturated_irrig["message"]
    assert any("ponding surface water" in act for act in saturated_irrig["recommended_actions"])

    # Crop-specific pH corrective action in soil assessment
    # Chickpea ideal pH is 6.0 - 8.0. Test with pH 5.2 (below min_ph 6.0)
    low_ph_chickpea = assess_soil_health({"ph": 5.2, "organic_matter": 3.0}, crop_name="chickpea")
    assert any("apply agricultural lime" in act.lower() for act in low_ph_chickpea["corrective_actions"])



