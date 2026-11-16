"""
Multi-Hazard Environmental Risk Assessment Engine.
Monitors frost risk, pest pressure, heat/drought stress, fungal susceptibility, and urban interface factors
using dynamic agronomic risk thresholds.
"""

from typing import Dict, Any, List
from agrisathi.advisory.profiles import get_crop_profile, get_risk_rules
from agrisathi.core.schemas import canonical_soil_type


def _safe_float(val: Any, default: float) -> float:
    """Null-safe float parser respecting valid 0.0 values."""
    if val is None:
        return default
    try:
        f = float(val)
        return default if (f != f or f == float("inf") or f == float("-inf")) else f
    except (ValueError, TypeError):
        return default


def assess_environmental_risks(
    farm_data: Dict[str, Any],
    crop_name: str = None,
    crop_profile: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Evaluates biological, meteorological, and environmental hazards threatening crop production.
    Accepts crop_name (str) and/or crop_profile (dict or str).
    Uses dynamic agronomic risk thresholds.
    """
    farm_data = farm_data or {}

    if isinstance(crop_name, dict) and crop_profile is None:
        crop_profile = crop_name
        crop_name = None

    if isinstance(crop_profile, str):
        crop_name = crop_profile
        crop_profile = None

    if crop_profile is None:
        crop_profile = get_crop_profile(crop_name or "rice")

    rules = get_risk_rules()
    r_frost = rules.get("frost", {})
    r_pest = rules.get("pest", {})
    r_fungal = rules.get("fungal", {})
    r_heat = rules.get("heat", {})
    r_drought = rules.get("drought", {})
    r_waterlog = rules.get("waterlogging", {})
    r_wind = rules.get("wind", {})
    r_urban = rules.get("urban_proximity", {})

    frost_risk = _safe_float(farm_data.get("frost_risk"), 10.0)
    pest_pressure = _safe_float(farm_data.get("pest_pressure"), 20.0)
    temperature = _safe_float(farm_data.get("temperature"), 25.0)
    humidity = _safe_float(farm_data.get("humidity"), 70.0)
    wind_speed = _safe_float(farm_data.get("wind_speed"), 3.0)
    rainfall = _safe_float(farm_data.get("rainfall"), 100.0)
    soil_moisture = _safe_float(farm_data.get("soil_moisture"), 30.0)
    urban_dist = _safe_float(farm_data.get("urban_area_proximity"), 25.0)
    raw_soil = farm_data.get("soil_type_label") or farm_data.get("soil_type", "Loamy")
    soil_type = canonical_soil_type(raw_soil)

    crop_title = crop_profile.get("display_name", crop_name or "Target Crop")
    is_frost_sensitive = crop_profile.get("frost_sensitive", True)
    min_temp = _safe_float(crop_profile.get("min_temp"), 10.0)
    max_temp = _safe_float(crop_profile.get("max_temp"), 38.0)
    water_demand = crop_profile.get("water_demand", "Medium")

    legacy_risks: List[str] = []
    matrix: List[Dict[str, str]] = []

    high_risk_count = 0

    # 1. Frost & Cold Injury Hazards
    th_frost_sev = _safe_float(r_frost.get("severe_frost_index"), 60.0)
    th_frost_sev_temp = _safe_float(r_frost.get("severe_temp_c"), 4.0)
    th_frost_mod = _safe_float(r_frost.get("moderate_frost_index"), 35.0)
    th_frost_mod_temp = _safe_float(r_frost.get("moderate_temp_c"), 8.0)

    if frost_risk > th_frost_sev or temperature < th_frost_sev_temp:
        high_risk_count += 1
        msg = f"High frost/chilling risk indicator (frost index: {frost_risk:.1f}%, temp: {temperature:.1f}°C)."
        if is_frost_sensitive:
            msg += f" {crop_title} is highly vulnerable to cellular frost damage."
        legacy_risks.append(msg)
        matrix.append({
            "hazard": "Frost / Freezing Injury",
            "level": "High",
            "impact": "Cellular rupture, seedling dieback, blossom freeze.",
            "mitigation": "Install anti-frost sprinkler systems, smoke generation, or row-cover fleece blankets.",
        })
    elif frost_risk > th_frost_mod or temperature < th_frost_mod_temp:
        legacy_risks.append(f"Moderate frost/chilling hazard (temp: {temperature:.1f}°C, index: {frost_risk:.1f}%).")
        matrix.append({
            "hazard": "Frost / Cold Stress",
            "level": "Medium",
            "impact": "Mild cold shock and delayed vegetative growth.",
            "mitigation": "Maintain light nocturnal soil moisture to increase thermal soil mass.",
        })
    elif temperature < min_temp:
        legacy_risks.append(
            f"Sub-optimal thermal regime: ambient temperature {temperature:.1f}°C is below minimum requirement ({min_temp:.1f}°C) for {crop_title}."
        )
        matrix.append({
            "hazard": "Cold Temperature Stress",
            "level": "Medium",
            "impact": "Delayed vegetative development, poor pollination, and reduced metabolic activity.",
            "mitigation": "Delay transplanting, use plastic mulch to warm soil, or protect with cloches/polyhouse.",
        })

    # 2. Pest & Pathogen Pressure
    th_pest_sev = _safe_float(r_pest.get("severe_pest_index"), 65.0)
    th_pest_mod = _safe_float(r_pest.get("moderate_pest_index"), 35.0)

    if pest_pressure > th_pest_sev:
        high_risk_count += 1
        legacy_risks.append(f"High pest-pressure indicator ({pest_pressure:.1f}%).")
        matrix.append({
            "hazard": "Pest & Insect Infestation",
            "level": "High",
            "impact": "Extensive defoliation, sucking injury, virus transmission.",
            "mitigation": "Implement Integrated Pest Management (IPM), deploy pheromone/sticky traps, and apply targeted bio-pesticides (e.g. neem oil / Beauveria bassiana).",
        })
    elif pest_pressure > th_pest_mod:
        legacy_risks.append(f"Moderate pest pressure ({pest_pressure:.1f}%).")
        matrix.append({
            "hazard": "Pest Activity",
            "level": "Medium",
            "impact": "Scattered insect infestation on foliage.",
            "mitigation": "Conduct field scouting twice weekly and remove weed hosts on field bunds.",
        })

    # 3. Fungal Pathogen Index
    th_fung_hum = _safe_float(r_fungal.get("high_humidity"), 85.0)
    th_fung_temp = _safe_float(r_fungal.get("warm_temp_c"), 24.0)

    if humidity > th_fung_hum and temperature > th_fung_temp:
        legacy_risks.append("Elevated fungal disease incubation hazard (high humidity + warm canopy).")
        matrix.append({
            "hazard": "Fungal Blight / Mildew",
            "level": "Medium",
            "impact": "Foliar blight, rust, or root-rot development.",
            "mitigation": "Improve row spacing for canopy aeration and consider preventative bio-fungicide spray.",
        })

    # 4. Thermal Extremes & Heat Stress
    th_heat_high = _safe_float(r_heat.get("high_temp_c"), 38.0)
    th_heat_ext = _safe_float(r_heat.get("extreme_temp_c"), 42.0)

    if temperature > th_heat_high:
        high_risk = temperature > th_heat_ext
        if high_risk:
            high_risk_count += 1
        legacy_risks.append(f"Thermal stress warning: ambient temperature {temperature:.1f}°C exceeds threshold.")
        matrix.append({
            "hazard": "Heat Stress",
            "level": "High" if high_risk else "Medium",
            "impact": "Pollen sterility, flower abortion, accelerated transpirational drying.",
            "mitigation": "Apply reflective kaolin clay spray or provide micro-sprinkler misting.",
        })
    elif temperature > max_temp:
        legacy_risks.append(
            f"Thermal exceedance: ambient temperature {temperature:.1f}°C exceeds optimal ceiling ({max_temp:.1f}°C) for {crop_title}."
        )
        matrix.append({
            "hazard": "Heat Stress",
            "level": "Medium",
            "impact": "Heat-induced metabolic depression, premature fruit drop, or accelerated ripening.",
            "mitigation": "Provide shade netting, irrigate during evening hours, or apply foliar anti-transpirants.",
        })

    # 5. Agricultural Drought & Waterlogging
    th_dr_crit_moist = _safe_float(r_drought.get("critical_moisture"), 12.0)
    th_dr_crit_rain = _safe_float(r_drought.get("critical_rainfall"), 50.0)
    th_dr_mod_moist = _safe_float(r_drought.get("moderate_moisture"), 16.0)
    th_dr_mod_rain = _safe_float(r_drought.get("moderate_rainfall"), 80.0)
    th_wl_rain = _safe_float(r_waterlog.get("excessive_rainfall"), 300.0)
    th_wl_moist = _safe_float(r_waterlog.get("high_moisture"), 40.0)

    if soil_moisture < th_dr_crit_moist and rainfall < th_dr_crit_rain:
        high_risk_count += 1
        legacy_risks.append(f"Severe agricultural drought hazard (moisture: {soil_moisture:.1f}%, seasonal rainfall: {rainfall:.1f} mm).")
        matrix.append({
            "hazard": "Agricultural Drought",
            "level": "High",
            "impact": "Severe moisture stress approaching permanent wilting point; acute yield penalty.",
            "mitigation": "Apply conservation tillage, organic mulch, and prioritize emergency drip irrigation.",
        })
    elif soil_moisture < th_dr_mod_moist and rainfall < th_dr_mod_rain:
        legacy_risks.append(f"Moderate moisture deficit hazard (moisture: {soil_moisture:.1f}%).")
        matrix.append({
            "hazard": "Moisture Deficit",
            "level": "Medium",
            "impact": "Stomatal closure, reduced photosynthetic rate, stunted biomass.",
            "mitigation": "Schedule deficit irrigation during cooler periods and suppress weed competition.",
        })
    elif rainfall > th_wl_rain or (soil_moisture > th_wl_moist and soil_type == "Clay" and water_demand != "High"):
        legacy_risks.append(f"Excessive moisture / waterlogging hazard (rainfall: {rainfall:.1f} mm, moisture: {soil_moisture:.1f}%).")
        matrix.append({
            "hazard": "Waterlogging / Hypoxia",
            "level": "Medium",
            "impact": "Root anaerobic stress, nutrient leaching, and fungal root-rot development.",
            "mitigation": "Clear lateral drainage ditches and construct raised planting beds.",
        })

    # 6. Wind & Lodging
    th_wind = _safe_float(r_wind.get("lodging_speed_mps"), 14.0)
    if wind_speed > th_wind:
        legacy_risks.append(f"High wind velocity ({wind_speed:.1f} m/s) poses lodging danger.")
        matrix.append({
            "hazard": "Wind Lodging",
            "level": "Medium",
            "impact": "Physical crop stem breakage and soil moisture desiccation.",
            "mitigation": "Erect temporary windbreak netting or earth up plant base.",
        })

    # 7. Urban Proximity
    th_urban = _safe_float(r_urban.get("peri_urban_distance_km"), 5.0)
    if urban_dist < th_urban:
        matrix.append({
            "hazard": "Peri-Urban Encroachment",
            "level": "Low",
            "impact": "Potential airborne particulates and water runoff issues; advantageous market access.",
            "mitigation": "Regularly test irrigation water sources for heavy metal or chemical runoffs.",
        })

    if not legacy_risks:
        legacy_risks.append("No major environmental risk indicator detected under current conditions.")

    overall_level = "Critical" if high_risk_count >= 2 else ("Elevated" if high_risk_count == 1 else "Normal")

    return {
        "overall_risk_level": overall_level,
        "risks": legacy_risks,
        "risk_matrix": matrix,
        "high_risk_count": high_risk_count,
    }
