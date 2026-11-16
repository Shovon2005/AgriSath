"""
Domain schemas, feature definitions, and categorical mappings for AgriSathi.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List


class SoilType(str, Enum):
    CLAY = "Clay"
    LOAMY = "Loamy"
    SANDY = "Sandy"


class GrowthStage(str, Enum):
    SEEDLING = "Seedling"
    VEGETATIVE = "Vegetative"
    FLOWERING = "Flowering"
    MATURITY = "Maturity"


class WaterSourceType(str, Enum):
    GROUNDWATER = "Groundwater"
    RAINWATER = "Rainwater"
    CANAL = "Canal"
    RIVER = "River"


# Bidirectional mappings between UI strings and model integer encodings
SOIL_TYPE_TO_CODE: Dict[str, int] = {
    "clay": 1,
    "loamy": 2,
    "sandy": 3,
}

CODE_TO_SOIL_TYPE: Dict[int, str] = {
    1: "Clay",
    2: "Loamy",
    3: "Sandy",
}

GROWTH_STAGE_TO_CODE: Dict[str, int] = {
    "seedling": 1,
    "vegetative": 2,
    "flowering": 3,
    "maturity": 4,
}

CODE_TO_GROWTH_STAGE: Dict[int, str] = {
    1: "Seedling",
    2: "Vegetative",
    3: "Flowering",
    4: "Maturity",
}

WATER_SOURCE_TO_CODE: Dict[str, int] = {
    "groundwater": 1,
    "rainwater": 2,
    "canal": 3,
    "river": 4,
}

CODE_TO_WATER_SOURCE: Dict[int, str] = {
    1: "Groundwater",
    2: "Rainwater",
    3: "Canal",
    4: "River",
}


def canonical_soil_type(val: Any) -> str:
    """Normalize any soil type representation (code, string, float) to 'Clay' | 'Loamy' | 'Sandy'."""
    s = str(val).strip().lower()
    if s.endswith(".0"):
        s = s[:-2]
    if s in ("1", "clay"):
        return "Clay"
    if s in ("2", "loamy"):
        return "Loamy"
    if s in ("3", "sandy"):
        return "Sandy"
    return "Loamy"


def canonical_growth_stage(val: Any) -> str:
    """Normalize any growth stage representation to 'Seedling' | 'Vegetative' | 'Flowering' | 'Maturity'."""
    s = str(val).strip().lower()
    if s.endswith(".0"):
        s = s[:-2]
    if s in ("1", "seedling"):
        return "Seedling"
    if s in ("2", "vegetative"):
        return "Vegetative"
    if s in ("3", "flowering"):
        return "Flowering"
    if s in ("4", "maturity"):
        return "Maturity"
    return "Vegetative"


def canonical_water_source(val: Any) -> str:
    """Normalize any water source representation to 'Groundwater' | 'Rainwater' | 'Canal' | 'River'."""
    s = str(val).strip().lower()
    if s.endswith(".0"):
        s = s[:-2]
    if s in ("1", "groundwater"):
        return "Groundwater"
    if s in ("2", "rainwater"):
        return "Rainwater"
    if s in ("3", "canal"):
        return "Canal"
    if s in ("4", "river"):
        return "River"
    return "Groundwater"


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    display_name: str
    unit: str
    dtype: str
    min_val: float
    max_val: float
    default: float
    description: str


# Canonical 22 input features in order
FEATURE_DEFINITIONS: List[FeatureSpec] = [
    FeatureSpec("N", "Nitrogen", "mg/kg", "float", 0.0, 300.0, 90.0, "Soil nitrogen content"),
    FeatureSpec("P", "Phosphorus", "mg/kg", "float", 0.0, 300.0, 42.0, "Soil phosphorus content"),
    FeatureSpec("K", "Potassium", "mg/kg", "float", 0.0, 300.0, 43.0, "Soil potassium content"),
    FeatureSpec("temperature", "Temperature", "°C", "float", -10.0, 60.0, 25.0, "Ambient temperature"),
    FeatureSpec("humidity", "Relative Humidity", "%", "float", 0.0, 100.0, 80.0, "Relative atmospheric humidity"),
    FeatureSpec("ph", "Soil pH", "pH", "float", 0.0, 14.0, 6.5, "Soil reaction acidity/alkalinity"),
    FeatureSpec("rainfall", "Rainfall", "mm", "float", 0.0, 2000.0, 200.0, "Seasonal rainfall precipitation"),
    FeatureSpec("soil_moisture", "Soil Moisture", "%", "float", 0.0, 100.0, 30.0, "Volumetric soil moisture content"),
    FeatureSpec("soil_type", "Soil Type", "", "category", 1, 3, 2, "Soil texture classification"),
    FeatureSpec("sunlight_exposure", "Sunlight Exposure", "hours/day", "float", 0.0, 24.0, 8.0, "Daily sunshine duration"),
    FeatureSpec("wind_speed", "Wind Speed", "m/s", "float", 0.0, 100.0, 3.5, "Average surface wind velocity"),
    FeatureSpec("co2_concentration", "CO₂ Concentration", "ppm", "float", 200.0, 2000.0, 400.0, "Atmospheric carbon dioxide"),
    FeatureSpec("organic_matter", "Organic Matter", "%", "float", 0.0, 100.0, 4.0, "Soil organic matter fraction"),
    FeatureSpec("irrigation_frequency", "Irrigation Frequency", "times/wk", "float", 0.0, 50.0, 3.0, "Weekly irrigation frequency"),
    FeatureSpec("crop_density", "Crop Density", "%", "float", 0.0, 100.0, 15.0, "Plant canopy coverage percentage"),
    FeatureSpec("pest_pressure", "Pest Pressure", "%", "float", 0.0, 100.0, 20.0, "Pest/disease incidence index"),
    FeatureSpec("fertilizer_usage", "Fertilizer Usage", "kg/ha", "float", 0.0, 1000.0, 100.0, "Annual fertilizer application rate"),
    FeatureSpec("growth_stage", "Growth Stage", "", "category", 1, 4, 1, "Phenological crop stage"),
    FeatureSpec("urban_area_proximity", "Urban Area Proximity", "km", "float", 0.0, 500.0, 15.0, "Distance to nearest urban market"),
    FeatureSpec("water_source_type", "Water Source", "", "category", 1, 4, 1, "Primary irrigation water source"),
    FeatureSpec("frost_risk", "Frost Risk", "%", "float", 0.0, 100.0, 5.0, "Seasonal frost probability index"),
    FeatureSpec("water_usage_efficiency", "Water Usage Efficiency", "ratio", "float", 0.0, 20.0, 2.5, "Crop water use efficiency ratio"),
]

FEATURE_NAMES: List[str] = [spec.name for spec in FEATURE_DEFINITIONS]
CATEGORICAL_FEATURES: List[str] = ["soil_type", "growth_stage", "water_source_type"]
NUMERIC_FEATURES: List[str] = [f for f in FEATURE_NAMES if f not in CATEGORICAL_FEATURES]
FEATURE_MAP: Dict[str, FeatureSpec] = {spec.name: spec for spec in FEATURE_DEFINITIONS}
