"""
Agronomic knowledge base and crop profile manager.
"""

import json
from typing import Dict, Any, Optional
from agrisathi.config import Config
from agrisathi.core.exceptions import AdvisoryCalculationError


# Soil texture agronomic properties
SOIL_PROPERTIES = {
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

# Commercial fertilizer elemental concentrations
# Urea: 46% N
# DAP (Di-ammonium phosphate): 18% N, 46% P2O5
# MOP (Muriate of potash): 60% K2O
FERTILIZER_CONVERSIONS = {
    "urea_n_fraction": 0.46,
    "dap_n_fraction": 0.18,
    "dap_p_fraction": 0.46,
    "mop_k_fraction": 0.60
}

_PROFILES_CACHE: Optional[Dict[str, Any]] = None


def reset_profiles_cache():
    """Reset cached crop profiles."""
    global _PROFILES_CACHE
    _PROFILES_CACHE = None


def get_crop_profiles() -> Dict[str, Any]:
    """Load and return crop agronomic profiles (cached)."""
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
