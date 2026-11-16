"""
Smart Irrigation Advisory Engine.
Estimates water stress indices based on soil moisture, climate parameters, and crop demand
using dynamic irrigation rules and FAO-56 Penman-Monteith ETc estimation.
"""

from typing import Dict, Any, List
from agrisathi.advisory.profiles import get_crop_profile, get_irrigation_rules
from agrisathi.core.schemas import (
    canonical_soil_type,
    canonical_growth_stage,
    canonical_water_source,
)


def _safe_float(val: Any, default: float) -> float:
    """Null-safe float parser respecting valid 0.0 values."""
    if val is None:
        return default
    try:
        f = float(val)
        return default if (f != f or f == float("inf") or f == float("-inf")) else f
    except (ValueError, TypeError):
        return default


def calculate_irrigation_advisory(
    farm_data: Dict[str, Any],
    crop_name: str = None,
    crop_profile: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Computes precise irrigation scheduling, priority level, and water management guidelines.
    Accepts crop_name (str) and/or crop_profile (dict or str).
    Uses dynamic irrigation rules.
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

    rules = get_irrigation_rules()
    crit_moisture = _safe_float(rules.get("critical_moisture"), 12.0)
    stress_moisture = _safe_float(rules.get("acute_stress_moisture"), 15.0)
    mod_moisture = _safe_float(rules.get("moderate_moisture"), 22.0)
    surplus_moisture = _safe_float(rules.get("surplus_moisture"), 35.0)
    waterlogged_moisture = _safe_float(rules.get("waterlogged_moisture"), 45.0)
    rec_depth_high = _safe_float(rules.get("rec_depth_high_mm"), 45.0)
    rec_depth_med = _safe_float(rules.get("rec_depth_med_mm"), 30.0)
    suppress_heavy = _safe_float(rules.get("rainfall_suppress_heavy_mm"), 15.0)
    suppress_light = _safe_float(rules.get("rainfall_suppress_light_mm"), 5.0)

    # Dynamic climate & irrigation thresholds
    et_high_temp = _safe_float(rules.get("et_high_temp_c"), 32.0)
    et_low_hum = _safe_float(rules.get("et_low_humidity"), 50.0)
    et_wind_speed = _safe_float(rules.get("et_wind_speed_mps"), 6.0)
    et_wind_temp = _safe_float(rules.get("et_wind_temp_c"), 28.0)
    abundant_rain = _safe_float(rules.get("abundant_rainfall_mm"), 150.0)
    low_rain_et = _safe_float(rules.get("low_rainfall_et_mm"), 60.0)
    rainwater_min_rain = _safe_float(rules.get("rainwater_reserve_min_rain_mm"), 40.0)
    gw_dry_moist = _safe_float(rules.get("groundwater_dry_moisture"), 20.0)
    maturity_red_moist = _safe_float(rules.get("maturity_reduction_moisture"), 18.0)

    moisture = _safe_float(farm_data.get("soil_moisture"), 25.0)
    temperature = _safe_float(farm_data.get("temperature"), 25.0)
    humidity = _safe_float(farm_data.get("humidity"), 70.0)
    rainfall = _safe_float(farm_data.get("rainfall"), 100.0)
    wind_speed = _safe_float(farm_data.get("wind_speed"), 3.0)

    crop_demand = crop_profile.get("water_demand", "Medium")
    crop_title = crop_profile.get("display_name", crop_name or "Target Crop")

    soil_type = canonical_soil_type(farm_data.get("soil_type_label") or farm_data.get("soil_type", "Loamy"))
    growth_stage = canonical_growth_stage(farm_data.get("growth_stage_label") or farm_data.get("growth_stage", "Vegetative"))
    water_source = canonical_water_source(farm_data.get("water_source_type_label") or farm_data.get("water_source_type", "Groundwater"))

    actions: List[str] = []

    # Evapotranspiration index
    high_et = (temperature > et_high_temp and humidity < et_low_hum) or (wind_speed > et_wind_speed and temperature > et_wind_temp)

    # 1. Critical Water Scarcity
    if moisture < crit_moisture:
        priority = "High"
        message = f"Critical soil moisture depletion ({moisture:.1f}%). Immediate irrigation required to prevent permanent wilting."
        actions.append(f"Initiate deep irrigation immediately ({rec_depth_high:.0f} mm equivalent depth).")
        actions.append("Prioritize early morning or evening application to minimize atmospheric evaporation loss.")
    elif moisture < stress_moisture:
        if crop_demand == "High" or growth_stage == "Flowering":
            priority = "High"
            message = f"Immediate irrigation required. {crop_title} is undergoing acute moisture stress at critical growth stage."
            actions.append(f"Initiate deep irrigation immediately ({rec_depth_high:.0f} mm equivalent depth).")
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
    elif moisture < mod_moisture:
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
        if moisture > waterlogged_moisture:
            priority = "Low"
            message = "Soil is heavily water-saturated. Cease all irrigation and inspect drainage to prevent root hypoxia."
            actions.append("Ensure drainage ditches are clear to evacuate ponding surface water.")
        elif rainfall > abundant_rain:
            priority = "Low"
            message = "Soil moisture is abundant following significant rainfall. No irrigation required."
            if soil_type == "Clay":
                actions.append("Ensure field drainage canals are clear to prevent waterlogging.")
        elif moisture > surplus_moisture and crop_demand != "High":
            priority = "Low"
            message = "Soil moisture is surplus. Cease irrigation to avoid root hypoxia and fungal rot."
            actions.append("Facilitate surface runoff drainage if water pools.")
        elif high_et and rainfall < low_rain_et:
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
    if soil_type == "Clay" and moisture > surplus_moisture:
        actions.append("Clay soil is heavily saturated; ensure active field drainage channels to prevent root asphyxiation.")

    # Growth stage adjustments
    if growth_stage == "Seedling" and priority in ("High", "Medium"):
        actions.append("Seedling stage has shallow rooting depth: maintain light, uniform surface moisture to avoid seedling desiccation.")
    elif growth_stage == "Maturity" and moisture >= maturity_red_moist:
        actions.append("Crop has reached Maturity stage: gradually reduce irrigation volume to encourage uniform ripening and avoid pre-harvest mold.")

    # Water source guidance
    if water_source == "Rainwater" and rainfall < rainwater_min_rain:
        actions.append("Rainwater harvesting reserves may be limited under dry conditions; verify secondary irrigation access.")
    elif water_source == "Groundwater" and moisture < gw_dry_moist:
        actions.append("Monitor groundwater salinity/EC levels before heavy pumping during dry spells.")

    # 4. Daily Crop Evapotranspiration (ETc) estimation via FAO-56 Penman/Hargreaves principles
    base_et0 = max(1.5, min(8.5, 0.16 * (temperature + 4.0) * (1.0 - (humidity / 160.0)) + (wind_speed * 0.12)))

    # Stage crop coefficient Kc
    kc_mid = _safe_float(crop_profile.get("kc_mid"), 1.05)
    if growth_stage == "Seedling":
        kc = round(kc_mid * 0.45, 2)
    elif growth_stage == "Vegetative":
        kc = round(kc_mid * 0.85, 2)
    elif growth_stage == "Flowering":
        kc = round(kc_mid * 1.15, 2)
    else:  # Maturity
        kc = round(kc_mid * 0.70, 2)

    etc_mm_day = round(base_et0 * kc, 1)

    # 5. Farm Area Water Volume Calculation (in Litres and m³)
    raw_area_ha = _safe_float(farm_data.get("farm_area_ha"), 1.0)
    farm_area_ha = max(0.01, raw_area_ha)

    # Recommended irrigation depth in mm
    if priority == "High":
        rec_depth_mm = rec_depth_high
    elif priority == "Medium":
        rec_depth_mm = rec_depth_med
    else:
        rec_depth_mm = 0.0

    # 1 mm depth over 1 hectare = 10,000 Litres (10 m³)
    water_quantity_litres = int(round(rec_depth_mm * farm_area_ha * 10000.0))
    daily_water_litres = int(round(etc_mm_day * farm_area_ha * 10000.0))
    water_quantity_m3 = round(water_quantity_litres / 1000.0, 1)
    daily_water_m3 = round(daily_water_litres / 1000.0, 1)

    # 6. Expected Rainfall (24-48h forecast) Integration (respecting 0.0)
    raw_rain = farm_data.get("expected_rainfall_24h")
    if raw_rain is None:
        raw_rain = farm_data.get("forecast_rainfall")
    expected_rain = _safe_float(raw_rain, 0.0)

    rainfall_suppressed = False

    if expected_rain >= suppress_heavy and priority in ("High", "Medium"):
        rainfall_suppressed = True
        actions.insert(0, f"Upcoming Rainfall Alert: {expected_rain:.1f} mm forecast in next 24-48 hours. Postpone chemical fertilizer & heavy irrigation to conserve water and prevent nutrient leaching.")
        message = f"Rainfall expected ({expected_rain:.1f} mm). Postpone irrigation until precipitation passes and reassess field soil moisture."
        next_irrigation = "Postpone: Rainfall forecast within 24-48 hours"
        irrigation_req = "No (Rain Forecast)"
    elif expected_rain >= suppress_light and priority == "Medium":
        rainfall_suppressed = True
        actions.insert(0, f"Light rain expected ({expected_rain:.1f} mm). Hold irrigation to assess effective soil wetting.")
        next_irrigation = "Hold: Check soil after expected rainfall"
        irrigation_req = "No (Rain Expected)"
    elif priority == "High":
        next_irrigation = "Immediate (within 24 hours)"
        irrigation_req = "Yes (Immediate)"
    elif priority == "Medium":
        next_irrigation = "Within 48 hours"
        irrigation_req = "Yes (Scheduled)"
    else:
        next_irrigation = "Not required for 4-6 days"
        irrigation_req = "No (Adequate Moisture)"

    return {
        "priority": priority,
        "irrigation_required": irrigation_req,
        "is_required": (priority in ("High", "Medium") and not rainfall_suppressed),
        "next_irrigation_time": next_irrigation,
        "daily_water_requirement_mm": etc_mm_day,
        "daily_water_litres": daily_water_litres,
        "daily_water_m3": daily_water_m3,
        "recommended_irrigation_depth_mm": rec_depth_mm if not rainfall_suppressed else 0.0,
        "water_quantity_litres": water_quantity_litres if not rainfall_suppressed else 0,
        "water_quantity_m3": water_quantity_m3 if not rainfall_suppressed else 0.0,
        "farm_area_ha": farm_area_ha,
        "expected_rainfall_24h": expected_rain,
        "rainfall_suppressed": rainfall_suppressed,
        "crop_coefficient_kc": kc,
        "message": message,
        "soil_moisture": moisture,
        "evapotranspiration_risk": "High" if high_et else "Normal",
        "crop_water_demand": crop_demand,
        "recommended_actions": actions,
    }
