"""
Smart Irrigation Advisory Engine.
Estimates water stress indices based on soil moisture, climate parameters, and crop demand.
"""

from typing import Dict, Any, List
from agrisathi.advisory.profiles import get_crop_profile
from agrisathi.core.schemas import (
    canonical_soil_type,
    canonical_growth_stage,
    canonical_water_source,
)


def calculate_irrigation_advisory(
    farm_data: Dict[str, Any],
    crop_name: str = None,
    crop_profile: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Computes precise irrigation scheduling, priority level, and water management guidelines.
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

    moisture = float(farm_data.get("soil_moisture", 25.0))
    temperature = float(farm_data.get("temperature", 25.0))
    humidity = float(farm_data.get("humidity", 70.0))
    rainfall = float(farm_data.get("rainfall", 100.0))
    wind_speed = float(farm_data.get("wind_speed", 3.0))

    crop_demand = crop_profile.get("water_demand", "Medium")
    crop_title = crop_profile.get("display_name", crop_name or "Target Crop")

    soil_type = canonical_soil_type(farm_data.get("soil_type_label") or farm_data.get("soil_type", "Loamy"))
    growth_stage = canonical_growth_stage(farm_data.get("growth_stage_label") or farm_data.get("growth_stage", "Vegetative"))
    water_source = canonical_water_source(farm_data.get("water_source_type_label") or farm_data.get("water_source_type", "Groundwater"))

    actions: List[str] = []

    # Evapotranspiration index
    high_et = (temperature > 32.0 and humidity < 50.0) or (wind_speed > 6.0 and temperature > 28.0)

    # 1. Critical Water Scarcity
    if moisture < 12.0:
        priority = "High"
        message = f"Critical soil moisture depletion ({moisture:.1f}%). Immediate irrigation required to prevent permanent wilting."
        actions.append("Initiate deep irrigation immediately (40-50 mm equivalent depth).")
        actions.append("Prioritize early morning or evening application to minimize atmospheric evaporation loss.")
    elif moisture < 15.0:
        if crop_demand == "High" or growth_stage == "Flowering":
            priority = "High"
            message = f"Immediate irrigation required. {crop_title} is undergoing acute moisture stress at critical growth stage."
            actions.append("Initiate deep irrigation immediately (40-50 mm equivalent depth).")
            actions.append("Prioritize early morning or evening application to minimize atmospheric evaporation loss.")
        elif temperature > 30.0:
            priority = "High"
            message = "High irrigation priority due to severe soil moisture depletion combined with high temperatures."
            actions.append("Irrigate within 24 hours to prevent permanent wilting point.")
        else:
            priority = "Medium"
            message = "Soil moisture is depleted. Irrigation is recommended within 48 hours."
            actions.append("Apply moderate irrigation to restore soil moisture capacity.")

    # 2. Moderate Moisture Condition
    elif moisture < 22.0:
        if high_et and crop_demand != "Low":
            priority = "Medium"
            message = "High evaporative demand is drying soil rapidly. Schedule irrigation within 2-3 days."
            actions.append("Monitor root zone moisture and plan irrigation cycle.")
        elif crop_demand == "High":
            priority = "Medium"
            message = f"{crop_title} has high water demand; schedule supplemental watering."
            actions.append("Maintain consistent moisture in root zone.")
        else:
            priority = "Low"
            message = "Soil moisture is currently acceptable. Monitor weather forecast before irrigating."
            actions.append("Observe field tensiometer or soil firmness over the next 48 hours.")

    # 3. Adequate or High Moisture
    else:
        if moisture > 45.0:
            priority = "Low"
            message = "Soil is heavily water-saturated. Cease all irrigation and inspect drainage to prevent root hypoxia."
            actions.append("Ensure drainage ditches are clear to evacuate ponding surface water.")
        elif rainfall > 150.0:
            priority = "Low"
            message = "Soil moisture is abundant following significant rainfall. No irrigation required."
            if soil_type == "Clay":
                actions.append("Ensure field drainage canals are clear to prevent waterlogging.")
        elif moisture > 35.0 and crop_demand != "High":
            priority = "Low"
            message = "Soil moisture is surplus. Cease irrigation to avoid root hypoxia and fungal rot."
            actions.append("Facilitate surface runoff drainage if water pools.")
        elif high_et and rainfall < 60.0:
            priority = "Medium"
            message = "Soil moisture is currently adequate, but rapid evaporative loss necessitates scheduling irrigation within 3-4 days."
            actions.append("Monitor root zone moisture and prepare irrigation supply.")
        else:
            priority = "Low"
            message = "Soil moisture is currently optimal for crop metabolic activity."
            actions.append("Continue standard moisture monitoring.")

    # Special note on sandy soils
    if soil_type == "Sandy" and priority in ("High", "Medium"):
        actions.append("Sandy soil has rapid percolation: apply frequent, smaller irrigation volumes rather than heavy flood irrigation.")

    # Special note on clay soils with high moisture
    if soil_type == "Clay" and moisture > 35.0:
        actions.append("Clay soil is heavily saturated; ensure active field drainage channels to prevent root asphyxiation.")

    # Growth stage adjustments
    if growth_stage == "Seedling" and priority in ("High", "Medium"):
        actions.append("Seedling stage has shallow rooting depth: maintain light, uniform surface moisture to avoid seedling desiccation.")
    elif growth_stage == "Maturity" and moisture >= 18.0:
        actions.append("Crop has reached Maturity stage: gradually reduce irrigation volume to encourage uniform ripening and avoid pre-harvest mold.")

    # Water source guidance
    if water_source == "Rainwater" and rainfall < 40.0:
        actions.append("Rainwater harvesting reserves may be limited under dry conditions; verify secondary irrigation access.")
    elif water_source == "Groundwater" and moisture < 20.0:
        actions.append("Monitor groundwater salinity/EC levels before heavy pumping during dry spells.")

    return {
        "priority": priority,
        "message": message,
        "soil_moisture": moisture,
        "evapotranspiration_risk": "High" if high_et else "Normal",
        "crop_water_demand": crop_demand,
        "recommended_actions": actions,
    }
