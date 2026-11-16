"""
Agronomic knowledge base, dynamic rule repository, and crop profile manager.
Loads agronomic parameters, soil properties, fertilizer conversions, and thresholds
dynamically from configuration files, eliminating static hardcoded dictionaries.
"""

import json
from typing import Dict, Any, Optional
from agrisathi.config import Config
from agrisathi.core.exceptions import AdvisoryCalculationError


# Robust in-memory fallbacks if JSON configuration is missing or malformed
_DEFAULT_SOIL_PROPERTIES = {
    "Clay": {
        "water_retention": "High",
        "drainage": "Poor to Moderate",
        "nutrient_holding": "High",
        "aeration": "Low",
        "description": "Heavy textured soil with high moisture and nutrient retention capacity, prone to waterlogging."
    },
    "Loamy": {
        "water_retention": "Optimal",
        "drainage": "Well Drained",
        "nutrient_holding": "High",
        "aeration": "Optimal",
        "description": "Balanced soil texture offering ideal aeration, moisture retention, and fertility for most crops."
    },
    "Sandy": {
        "water_retention": "Low",
        "drainage": "Excessive",
        "nutrient_holding": "Low",
        "aeration": "High",
        "description": "Light, coarse soil with rapid percolation; requires frequent light irrigation and split fertilizer doses."
    }
}

_DEFAULT_FERTILIZER_CONVERSIONS = {
    "urea_n_fraction": 0.46,
    "dap_n_fraction": 0.18,
    "dap_p_fraction": 0.46,
    "ssp_p_fraction": 0.16,
    "mop_k_fraction": 0.60,
    "commercial_bag_weight_kg": 50.0,
    "surplus_multiplier": 1.5,
}

_DEFAULT_ORGANIC_GUIDELINES = {
    "fym": {
        "name": "Farm Yard Manure (FYM)",
        "dosage_t_ha": "10 - 15 t/ha",
        "rate_per_ha_tonnes": 10.0,
        "benefits": "Improves soil humus, CEC, microbial diversity, and water retention capacity."
    },
    "vermicompost": {
        "name": "Vermicompost",
        "dosage_t_ha": "2.5 - 5.0 t/ha",
        "rate_per_ha_tonnes": 3.0,
        "benefits": "Rich in bioavailable micronutrients, plant growth hormones (auxins/gibberellins), and beneficial microbes."
    },
    "neem_cake": {
        "name": "Neem Cake",
        "dosage_kg_ha": "250 - 500 kg/ha",
        "rate_per_ha_kg": 250.0,
        "benefits": "Natural nitrification inhibitor; reduces nitrogen leaching while suppressing soil-borne nematodes and root pests."
    },
    "biofertilizers": {
        "pulses": "Rhizobium leguminosarum (200 g/10 kg seed) + Phosphate Solubilizing Bacteria (PSB 2 kg/ha) for symbiotic nitrogen fixation.",
        "cereals": "Azotobacter / Azospirillum (2 kg/ha) + PSB (2 kg/ha) incorporated with organic manure to boost natural nutrient cycling."
    }
}

_DEFAULT_SOIL_THRESHOLDS = {
    "ph": {
        "strongly_acidic": 5.0,
        "slightly_acidic": 6.0,
        "optimal_min": 6.0,
        "optimal_max": 7.5,
        "moderately_alkaline": 8.5
    },
    "electrical_conductivity": {
        "low": 0.1,
        "optimal_max": 2.0,
        "severe_salinity": 4.0
    },
    "organic_matter": {
        "critical_low": 1.5,
        "suboptimal": 3.0
    },
    "organic_carbon": {
        "critical_low": 0.50,
        "optimal_min": 0.75
    },
    "nitrogen": {
        "min": 30.0,
        "max": 140.0,
        "fertility_medium": 30.0,
        "fertility_high": 50.0
    },
    "phosphorus": {
        "min": 25.0,
        "max": 100.0,
        "fertility_medium": 20.0,
        "fertility_high": 35.0
    },
    "potassium": {
        "min": 30.0,
        "max": 140.0,
        "fertility_medium": 25.0,
        "fertility_high": 45.0
    }
}

_DEFAULT_IRRIGATION_RULES = {
    "critical_moisture": 12.0,
    "acute_stress_moisture": 15.0,
    "moderate_moisture": 22.0,
    "surplus_moisture": 35.0,
    "waterlogged_moisture": 45.0,
    "rec_depth_high_mm": 45.0,
    "rec_depth_med_mm": 30.0,
    "rainfall_suppress_heavy_mm": 15.0,
    "rainfall_suppress_light_mm": 5.0,
    "et_high_temp_c": 32.0,
    "et_low_humidity": 50.0,
    "et_wind_speed_mps": 6.0,
    "et_wind_temp_c": 28.0,
    "abundant_rainfall_mm": 150.0,
    "low_rainfall_et_mm": 60.0,
    "rainwater_reserve_min_rain_mm": 40.0,
    "groundwater_dry_moisture": 20.0,
    "maturity_reduction_moisture": 18.0,
}

_DEFAULT_RISK_RULES = {
    "frost": {
        "severe_frost_index": 60.0,
        "severe_temp_c": 4.0,
        "moderate_frost_index": 35.0,
        "moderate_temp_c": 8.0,
    },
    "pest": {
        "severe_pest_index": 65.0,
        "moderate_pest_index": 35.0,
    },
    "fungal": {
        "high_humidity": 85.0,
        "warm_temp_c": 24.0,
    },
    "heat": {
        "extreme_temp_c": 42.0,
        "high_temp_c": 38.0,
    },
    "drought": {
        "critical_moisture": 12.0,
        "critical_rainfall": 50.0,
        "moderate_moisture": 16.0,
        "moderate_rainfall": 80.0,
    },
    "waterlogging": {
        "excessive_rainfall": 300.0,
        "high_moisture": 40.0,
    },
    "wind": {
        "lodging_speed_mps": 14.0,
    },
    "urban_proximity": {
        "peri_urban_distance_km": 5.0,
    },
}


# Dynamic caches
_RULES_CACHE: Optional[Dict[str, Any]] = None
_PROFILES_CACHE: Optional[Dict[str, Any]] = None


def reload_agronomic_rules() -> Dict[str, Any]:
    """Force reload of dynamic agronomic rules from JSON configuration."""
    global _RULES_CACHE
    path = Config.AGRONOMIC_RULES_PATH
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                _RULES_CACHE = json.load(f)
        except Exception:
            _RULES_CACHE = None

    if _RULES_CACHE is None:
        _RULES_CACHE = {
            "soil_properties": _DEFAULT_SOIL_PROPERTIES,
            "fertilizer_conversions": _DEFAULT_FERTILIZER_CONVERSIONS,
            "organic_fertilizer_guidelines": _DEFAULT_ORGANIC_GUIDELINES,
            "soil_thresholds": _DEFAULT_SOIL_THRESHOLDS,
            "irrigation_rules": _DEFAULT_IRRIGATION_RULES,
            "environmental_risk_rules": _DEFAULT_RISK_RULES,
        }

    # Update module-level convenience dictionaries
    SOIL_PROPERTIES.clear()
    SOIL_PROPERTIES.update(_RULES_CACHE.get("soil_properties", _DEFAULT_SOIL_PROPERTIES))

    FERTILIZER_CONVERSIONS.clear()
    FERTILIZER_CONVERSIONS.update(_RULES_CACHE.get("fertilizer_conversions", _DEFAULT_FERTILIZER_CONVERSIONS))

    ORGANIC_FERTILIZER_GUIDELINES.clear()
    ORGANIC_FERTILIZER_GUIDELINES.update(_RULES_CACHE.get("organic_fertilizer_guidelines", _DEFAULT_ORGANIC_GUIDELINES))

    return _RULES_CACHE


def get_agronomic_rules() -> Dict[str, Any]:
    """Retrieve all dynamic agronomic rules (cached with auto-reload)."""
    global _RULES_CACHE
    if _RULES_CACHE is None:
        reload_agronomic_rules()
    return _RULES_CACHE


def update_agronomic_rules(new_rules: Dict[str, Any]) -> Dict[str, Any]:
    """Dynamically update agronomic rules and persist to configuration JSON."""
    global _RULES_CACHE
    current_rules = get_agronomic_rules()
    for section, values in new_rules.items():
        if isinstance(values, dict) and section in current_rules and isinstance(current_rules[section], dict):
            current_rules[section].update(values)
        else:
            current_rules[section] = values

    path = Config.AGRONOMIC_RULES_PATH
    with open(path, "w", encoding="utf-8") as f:
        json.dump(current_rules, f, indent=2)

    _RULES_CACHE = current_rules
    reload_agronomic_rules()
    return _RULES_CACHE


def get_soil_properties() -> Dict[str, Any]:
    """Retrieve dynamic soil texture properties."""
    rules = get_agronomic_rules()
    return rules.get("soil_properties", _DEFAULT_SOIL_PROPERTIES)


def get_fertilizer_conversions() -> Dict[str, Any]:
    """Retrieve dynamic fertilizer elemental fractions and constants."""
    rules = get_agronomic_rules()
    return rules.get("fertilizer_conversions", _DEFAULT_FERTILIZER_CONVERSIONS)


def get_organic_guidelines() -> Dict[str, Any]:
    """Retrieve dynamic organic and bio-fertilizer guidance."""
    rules = get_agronomic_rules()
    return rules.get("organic_fertilizer_guidelines", _DEFAULT_ORGANIC_GUIDELINES)


def get_soil_thresholds() -> Dict[str, Any]:
    """Retrieve dynamic soil health assessment thresholds."""
    rules = get_agronomic_rules()
    return rules.get("soil_thresholds", _DEFAULT_SOIL_THRESHOLDS)


def get_irrigation_rules() -> Dict[str, Any]:
    """Retrieve dynamic irrigation scheduling parameters."""
    rules = get_agronomic_rules()
    return rules.get("irrigation_rules", _DEFAULT_IRRIGATION_RULES)


def get_risk_rules() -> Dict[str, Any]:
    """Retrieve dynamic multi-hazard environmental risk thresholds."""
    rules = get_agronomic_rules()
    return rules.get("environmental_risk_rules", _DEFAULT_RISK_RULES)


# Module-level exported dictionaries for backward-compatibility
SOIL_PROPERTIES: Dict[str, Any] = dict(_DEFAULT_SOIL_PROPERTIES)
FERTILIZER_CONVERSIONS: Dict[str, Any] = dict(_DEFAULT_FERTILIZER_CONVERSIONS)
ORGANIC_FERTILIZER_GUIDELINES: Dict[str, Any] = dict(_DEFAULT_ORGANIC_GUIDELINES)

# Initialize on import
reload_agronomic_rules()


def reset_profiles_cache():
    """Reset cached crop profiles and agronomic rules."""
    global _PROFILES_CACHE, _RULES_CACHE
    _PROFILES_CACHE = None
    _RULES_CACHE = None
    reload_agronomic_rules()


def get_crop_profiles() -> Dict[str, Any]:
    """Load and return crop agronomic profiles dynamically."""
    global _PROFILES_CACHE
    if _PROFILES_CACHE is None:
        path = Config.CROP_PROFILES_PATH
        if not path.exists():
            raise AdvisoryCalculationError(f"Agronomic profile database missing at {path}")
        with open(path, "r", encoding="utf-8") as f:
            _PROFILES_CACHE = json.load(f)
    return _PROFILES_CACHE


def get_crop_profile(crop_name: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve profile for a specific crop (case-insensitive and null-safe)."""
    profiles = get_crop_profiles()
    raw_str = str(crop_name or "rice").strip()
    key = raw_str.lower()
    if key not in profiles:
        # Fallback profile for unknown crop
        display = raw_str.title() if raw_str else "Target Crop"
        return {
            "display_name": display,
            "category": "General Crop",
            "opt_n": 80,
            "opt_p": 40,
            "opt_k": 40,
            "min_ph": 6.0,
            "max_ph": 7.5,
            "water_demand": "Medium",
            "min_temp": 15.0,
            "max_temp": 35.0,
            "frost_sensitive": True,
            "ideal_soil": ["Loamy"],
            "description": "General crop profile with balanced standard agricultural requirements."
        }
    return profiles[key]


def update_crop_profile(crop_name: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Dynamically update or add a crop agronomic profile in storage."""
    global _PROFILES_CACHE
    profiles = get_crop_profiles()
    key = crop_name.strip().lower()
    profiles[key] = profile_data
    path = Config.CROP_PROFILES_PATH
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)
    _PROFILES_CACHE = profiles
    return profile_data
