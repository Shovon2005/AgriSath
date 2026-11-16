"""
Dynamic Farm Scenarios and Agro-Climatic Presets Repository.
Loads, manages, and saves farm simulation scenarios dynamically from data/farm_scenarios.json.
Eliminates static hardcoded scenario dictionaries from web views.
"""

import json
import re
from typing import Dict, Any, Optional
from agrisathi.config import Config
from agrisathi.core.exceptions import ValidationError
from agrisathi.core.validator import validate_farm_input
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.data.scenarios")

_SCENARIOS_CACHE: Optional[Dict[str, Any]] = None

_DEFAULT_FALLBACK_SCENARIOS = {
    "rice": {
        "key": "rice",
        "title": "🌾 Wetland Rice",
        "category": "Cereals",
        "parameters": {
            "N": 90, "P": 42, "K": 43, "temperature": 21.0, "humidity": 82.0, "ph": 6.5,
            "rainfall": 202.0, "soil_moisture": 30.0, "soil_type": "Clay",
            "sunlight_exposure": 8.5, "wind_speed": 10.0, "co2_concentration": 435.0,
            "organic_matter": 3.2, "irrigation_frequency": 4, "crop_density": 12.0,
            "pest_pressure": 55.0, "fertilizer_usage": 180.0, "growth_stage": "Vegetative",
            "urban_area_proximity": 15.0, "water_source_type": "Canal", "frost_risk": 5.0,
            "water_usage_efficiency": 1.2, "farm_area": 2.5, "farm_area_unit": "hectare",
            "electrical_conductivity": 0.5, "organic_carbon": 0.85, "location": "West Bengal, India",
            "season": "Kharif", "expected_rainfall_24h": 0.0
        }
    },
    "chickpea": {
        "key": "chickpea",
        "title": "🥜 Semi-Arid Chickpea",
        "category": "Pulses",
        "parameters": {
            "N": 40, "P": 60, "K": 80, "temperature": 18.0, "humidity": 25.0, "ph": 7.2,
            "rainfall": 40.0, "soil_moisture": 12.0, "soil_type": "Sandy",
            "sunlight_exposure": 10.0, "wind_speed": 5.0, "co2_concentration": 390.0,
            "organic_matter": 2.0, "irrigation_frequency": 1, "crop_density": 10.0,
            "pest_pressure": 15.0, "fertilizer_usage": 60.0, "growth_stage": "Seedling",
            "urban_area_proximity": 30.0, "water_source_type": "Groundwater", "frost_risk": 2.0,
            "water_usage_efficiency": 3.8, "farm_area": 4.0, "farm_area_unit": "acre",
            "electrical_conductivity": 0.4, "organic_carbon": 0.60, "location": "Madhya Pradesh, India",
            "season": "Rabi", "expected_rainfall_24h": 0.0
        }
    },
    "cotton": {
        "key": "cotton",
        "title": "🌿 Commercial Cotton",
        "category": "Cash Crop",
        "parameters": {
            "N": 120, "P": 50, "K": 30, "temperature": 28.0, "humidity": 65.0, "ph": 7.5,
            "rainfall": 80.0, "soil_moisture": 22.0, "soil_type": "Clay",
            "sunlight_exposure": 9.0, "wind_speed": 4.0, "co2_concentration": 410.0,
            "organic_matter": 3.5, "irrigation_frequency": 2, "crop_density": 14.0,
            "pest_pressure": 45.0, "fertilizer_usage": 120.0, "growth_stage": "Vegetative",
            "urban_area_proximity": 20.0, "water_source_type": "Canal", "frost_risk": 0.0,
            "water_usage_efficiency": 2.2, "farm_area": 1.5, "farm_area_unit": "hectare",
            "electrical_conductivity": 0.7, "organic_carbon": 0.90, "location": "Gujarat, India",
            "season": "Kharif", "expected_rainfall_24h": 0.0
        }
    },
    "alert": {
        "key": "alert",
        "title": "⚠️ Multi-Risk Stress",
        "category": "Risk Simulation",
        "parameters": {
            "N": 20, "P": 15, "K": 10, "temperature": 39.5, "humidity": 88.0, "ph": 4.5,
            "rainfall": 15.0, "soil_moisture": 9.0, "soil_type": "Sandy",
            "sunlight_exposure": 11.5, "wind_speed": 16.5, "co2_concentration": 420.0,
            "organic_matter": 0.9, "irrigation_frequency": 1, "crop_density": 8.0,
            "pest_pressure": 92.0, "fertilizer_usage": 50.0, "growth_stage": "Flowering",
            "urban_area_proximity": 3.0, "water_source_type": "Groundwater", "frost_risk": 75.0,
            "water_usage_efficiency": 1.0, "farm_area": 2.0, "farm_area_unit": "hectare",
            "electrical_conductivity": 4.5, "organic_carbon": 0.30, "location": "Arid Zone",
            "season": "Whole Year", "expected_rainfall_24h": 0.0
        }
    }
}


def reload_farm_scenarios() -> Dict[str, Any]:
    """Force reload of farm scenarios from JSON file."""
    global _SCENARIOS_CACHE
    path = Config.SCENARIOS_PATH
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _SCENARIOS_CACHE = data.get("scenarios", _DEFAULT_FALLBACK_SCENARIOS)
        except Exception as e:
            logger.warning("Failed loading farm scenarios from %s: %s", path, e)
            _SCENARIOS_CACHE = _DEFAULT_FALLBACK_SCENARIOS
    else:
        _SCENARIOS_CACHE = _DEFAULT_FALLBACK_SCENARIOS
    return _SCENARIOS_CACHE


def get_farm_scenarios() -> Dict[str, Any]:
    """Retrieve all available farm scenarios."""
    global _SCENARIOS_CACHE
    if _SCENARIOS_CACHE is None:
        reload_farm_scenarios()
    return _SCENARIOS_CACHE


def get_scenario_parameters_map() -> Dict[str, Dict[str, Any]]:
    """Retrieve mapping of scenario keys to raw parameter dictionaries."""
    scenarios = get_farm_scenarios()
    return {
        key: sc.get("parameters", sc)
        for key, sc in scenarios.items()
    }


def get_farm_scenario(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single farm scenario by its key."""
    scenarios = get_farm_scenarios()
    return scenarios.get(key.strip().lower())


def save_farm_scenario(key: str, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dynamically validate, sanitize, and save/update a farm scenario in the persistent JSON store.
    Enforces valid key format and agronomic parameter schemas.
    """
    global _SCENARIOS_CACHE
    if not isinstance(key, str) or not key.strip():
        raise ValidationError("Scenario key must be a non-empty string.")

    clean_key = key.strip().lower()
    if not re.match(r"^[a-z0-9_\-]+$", clean_key):
        raise ValidationError(
            f"Invalid scenario key '{clean_key}'. Key may only contain alphanumeric characters, underscores, and hyphens."
        )

    scenarios = get_farm_scenarios()

    raw_params = scenario_data.get("parameters") if isinstance(scenario_data.get("parameters"), dict) else scenario_data

    # Validate parameters to ensure valid agronomic ranges
    sanitized_params = validate_farm_input(raw_params, allow_defaults=True)

    # Clean display labels from storage payload to keep JSON concise
    clean_params = {k: v for k, v in sanitized_params.items() if not k.endswith("_label")}

    title = str(scenario_data.get("title") or f"🌱 {clean_key.title()} Scenario").strip()
    category = str(scenario_data.get("category") or "Custom").strip()

    entry = {
        "key": clean_key,
        "title": title,
        "category": category,
        "parameters": clean_params,
    }

    scenarios[clean_key] = entry
    path = Config.SCENARIOS_PATH
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"version": "1.0", "scenarios": scenarios}, f, indent=2)

    _SCENARIOS_CACHE = scenarios
    return entry


def delete_farm_scenario(key: str) -> bool:
    """
    Dynamically remove a farm scenario from the persistent store.
    Returns True if removed, False if scenario did not exist.
    """
    global _SCENARIOS_CACHE
    clean_key = str(key or "").strip().lower()
    scenarios = get_farm_scenarios()

    if clean_key not in scenarios:
        return False

    del scenarios[clean_key]
    path = Config.SCENARIOS_PATH
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"version": "1.0", "scenarios": scenarios}, f, indent=2)

    _SCENARIOS_CACHE = scenarios
    return True
