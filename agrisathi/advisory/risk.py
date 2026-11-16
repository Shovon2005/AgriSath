"""
Multi-Hazard Environmental Risk Assessment Engine.
Monitors frost risk, pest pressure, heat/drought stress, fungal susceptibility, and urban interface factors.
"""

from typing import Dict, Any, List
from agrisathi.advisory.profiles import get_crop_profile
from agrisathi.core.schemas import canonical_soil_type


def assess_environmental_risks(
    farm_data: Dict[str, Any],
    crop_name: str = None,
    crop_profile: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Evaluates biological, meteorological, and environmental hazards threatening crop production.
    Accepts crop_name (str) and/or crop_profile (dict or str).
    """
    if isinstance(crop_name, dict) and crop_profile is None:
        crop_profile = crop_name
        crop_name = None

    if isinstance(crop_profile, str):
        crop_name = crop_profile
        crop_profile = None

    if crop_profile is None:
        crop_profile = get_crop_profile(crop_name or "rice")

    frost_risk = float(farm_data.get("frost_risk", 10.0))
    pest_pressure = float(farm_data.get("pest_pressure", 20.0))
    temperature = float(farm_data.get("temperature", 25.0))
    humidity = float(farm_data.get("humidity", 70.0))
    wind_speed = float(farm_data.get("wind_speed", 3.0))
    rainfall = float(farm_data.get("rainfall", 100.0))
    soil_moisture = float(farm_data.get("soil_moisture", 30.0))
    urban_dist = float(farm_data.get("urban_area_proximity", 25.0))
    raw_soil = farm_data.get("soil_type_label") or farm_data.get("soil_type", "Loamy")
    soil_type = canonical_soil_type(raw_soil)

    crop_title = crop_profile.get("display_name", crop_name or "Target Crop")
    is_frost_sensitive = crop_profile.get("frost_sensitive", True)
    min_temp = float(crop_profile.get("min_temp", 10.0))
    max_temp = float(crop_profile.get("max_temp", 38.0))
    water_demand = crop_profile.get("water_demand", "Medium")

    legacy_risks: List[str] = []
    matrix: List[Dict[str, str]] = []

    high_risk_count = 0

    # 1. Frost & Cold Injury Hazards
    if frost_risk > 60.0 or temperature < 4.0:
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
    elif frost_risk > 35.0 or temperature < 8.0:
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
    if pest_pressure > 65.0:
        high_risk_count += 1
        legacy_risks.append(f"High pest-pressure indicator ({pest_pressure:.1f}%).")
        matrix.append({
            "hazard": "Pest & Insect Infestation",
            "level": "High",
            "impact": "Extensive defoliation, sucking injury, virus transmission.",
            "mitigation": "Implement Integrated Pest Management (IPM), deploy pheromone/sticky traps, and apply targeted bio-pesticides (e.g. neem oil / Beauveria bassiana).",
        })
    elif pest_pressure > 35.0:
        legacy_risks.append(f"Moderate pest pressure ({pest_pressure:.1f}%).")
        matrix.append({
            "hazard": "Pest Activity",
            "level": "Medium",
            "impact": "Scattered insect infestation on foliage.",
            "mitigation": "Conduct field scouting twice weekly and remove weed hosts on field bunds.",
        })

    # 3. Fungal Pathogen Index
    if humidity > 85.0 and temperature > 24.0:
        legacy_risks.append("Elevated fungal disease incubation hazard (high humidity + warm canopy).")
        matrix.append({
            "hazard": "Fungal Blight / Mildew",
            "level": "Medium",
            "impact": "Foliar blight, rust, or root-rot development.",
            "mitigation": "Improve row spacing for canopy aeration and consider preventative bio-fungicide spray.",
        })

    # 4. Thermal Extremes & Heat Stress
    if temperature > 38.0:
        high_risk = temperature > 42.0
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
    if soil_moisture < 12.0 and rainfall < 50.0:
        high_risk_count += 1
        legacy_risks.append(f"Severe agricultural drought hazard (moisture: {soil_moisture:.1f}%, seasonal rainfall: {rainfall:.1f} mm).")
        matrix.append({
            "hazard": "Agricultural Drought",
            "level": "High",
            "impact": "Severe moisture stress approaching permanent wilting point; acute yield penalty.",
            "mitigation": "Apply conservation tillage, organic mulch, and prioritize emergency drip irrigation.",
        })
    elif soil_moisture < 16.0 and rainfall < 80.0:
        legacy_risks.append(f"Moderate moisture deficit hazard (moisture: {soil_moisture:.1f}%).")
        matrix.append({
            "hazard": "Moisture Deficit",
            "level": "Medium",
            "impact": "Stomatal closure, reduced photosynthetic rate, stunted biomass.",
            "mitigation": "Schedule deficit irrigation during cooler periods and suppress weed competition.",
        })
    elif rainfall > 300.0 or (soil_moisture > 40.0 and soil_type == "Clay" and water_demand != "High"):
        legacy_risks.append(f"Excessive moisture / waterlogging hazard (rainfall: {rainfall:.1f} mm, moisture: {soil_moisture:.1f}%).")
        matrix.append({
            "hazard": "Waterlogging / Hypoxia",
            "level": "Medium",
            "impact": "Root anaerobic stress, nutrient leaching, and fungal root-rot development.",
            "mitigation": "Clear lateral drainage ditches and construct raised planting beds.",
        })

    # 6. Wind & Lodging
    if wind_speed > 14.0:
        legacy_risks.append(f"High wind velocity ({wind_speed:.1f} m/s) poses lodging danger.")
        matrix.append({
            "hazard": "Wind Lodging",
            "level": "Medium",
            "impact": "Physical crop stem breakage and soil moisture desiccation.",
            "mitigation": "Erect temporary windbreak netting or earth up plant base.",
        })

    # 7. Urban Proximity
    if urban_dist < 5.0:
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
