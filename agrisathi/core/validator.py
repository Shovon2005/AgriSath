"""
Input validation and sanitization for farm parameters.
"""

import math
from typing import Dict, Any, Tuple
from agrisathi.core.exceptions import ValidationError
from agrisathi.core.schemas import (
    FEATURE_MAP,
    FEATURE_NAMES,
    CATEGORICAL_FEATURES,
    SOIL_TYPE_TO_CODE,
    GROWTH_STAGE_TO_CODE,
    WATER_SOURCE_TO_CODE,
    CODE_TO_SOIL_TYPE,
    CODE_TO_GROWTH_STAGE,
    CODE_TO_WATER_SOURCE,
    canonical_season,
    area_to_hectares,
)


def normalize_categorical(field_name: str, raw_value: Any) -> Tuple[int, str]:
    """
    Normalize categorical value into (integer_code, display_string).
    Accepts integer codes (1, 2, 3, 4), floats (1.0, 2.0), and string representations ("Loamy", "Clay").
    """
    if isinstance(raw_value, bool):
        raise ValidationError(
            f"Invalid {field_name} '{raw_value}'. Booleans are not allowed.",
            {"field": field_name, "value": raw_value},
        )

    str_val = str(raw_value).strip().lower()
    if str_val.endswith(".0"):
        str_val = str_val[:-2]

    if field_name == "soil_type":
        # Check direct code or string
        if str_val in ("1", "clay"):
            return 1, "Clay"
        if str_val in ("2", "loamy"):
            return 2, "Loamy"
        if str_val in ("3", "sandy"):
            return 3, "Sandy"
        raise ValidationError(
            f"Invalid soil_type '{raw_value}'. Allowed values: Clay, Loamy, Sandy.",
            {"field": field_name, "value": raw_value},
        )

    if field_name == "growth_stage":
        if str_val in ("1", "seedling"):
            return 1, "Seedling"
        if str_val in ("2", "vegetative"):
            return 2, "Vegetative"
        if str_val in ("3", "flowering"):
            return 3, "Flowering"
        if str_val in ("4", "maturity"):
            return 4, "Maturity"
        raise ValidationError(
            f"Invalid growth_stage '{raw_value}'. Allowed values: Seedling, Vegetative, Flowering, Maturity.",
            {"field": field_name, "value": raw_value},
        )

    if field_name == "water_source_type":
        if str_val in ("1", "groundwater"):
            return 1, "Groundwater"
        if str_val in ("2", "rainwater"):
            return 2, "Rainwater"
        if str_val in ("3", "canal"):
            return 3, "Canal"
        if str_val in ("4", "river"):
            return 4, "River"
        raise ValidationError(
            f"Invalid water_source_type '{raw_value}'. Allowed values: Groundwater, Rainwater, Canal, River.",
            {"field": field_name, "value": raw_value},
        )

    raise ValidationError(f"Unknown categorical field '{field_name}'", {"field": field_name})


def validate_farm_input(raw_data: Dict[str, Any], allow_defaults: bool = False) -> Dict[str, Any]:
    """
    Validates and normalizes raw form/API data.
    Returns sanitized dictionary containing all 22 typed features and readable labels.
    """
    if not isinstance(raw_data, dict):
        raise ValidationError("Input payload must be a key-value dictionary.")

    sanitized: Dict[str, Any] = {}
    display_info: Dict[str, str] = {}
    errors: Dict[str, str] = {}

    for name in FEATURE_NAMES:
        spec = FEATURE_MAP[name]
        val = raw_data.get(name) if name in raw_data else None

        # Optional field: soil_moisture is optional in decision support (defaults to standard 30.0%)
        if name == "soil_moisture" and (val is None or (isinstance(val, str) and not val.strip())):
            val = spec.default

        # Auto-derive organic_matter from organic_carbon if omitted or empty
        if name == "organic_matter" and (val is None or (isinstance(val, str) and not val.strip())):
            raw_oc_cand = raw_data.get("organic_carbon") or raw_data.get("oc")
            if raw_oc_cand is not None and str(raw_oc_cand).strip() != "":
                try:
                    val = round(float(raw_oc_cand) * 1.724, 2)
                except (ValueError, TypeError):
                    pass

        if val is None or (isinstance(val, str) and not val.strip()):
            if allow_defaults:
                val = spec.default
            else:
                errors[name] = f"Missing required parameter '{name}'." if name not in raw_data else f"Field '{name}' cannot be empty."
                continue

        spec = FEATURE_MAP[name]

        if name in CATEGORICAL_FEATURES:
            try:
                code, display = normalize_categorical(name, val)
                sanitized[name] = code
                display_info[f"{name}_label"] = display
            except ValidationError as e:
                errors[name] = e.message
        else:
            if isinstance(val, bool):
                errors[name] = f"Field '{name}' must be a valid number, not boolean."
                continue

            try:
                numeric_val = float(val)
            except (ValueError, TypeError):
                errors[name] = f"Field '{name}' must be a valid number."
                continue

            if math.isnan(numeric_val) or math.isinf(numeric_val):
                errors[name] = f"Field '{name}' must be a finite real number."
                continue

            # Boundary checks
            if numeric_val < spec.min_val or numeric_val > spec.max_val:
                errors[name] = (
                    f"'{spec.display_name}' ({numeric_val} {spec.unit}) is outside "
                    f"valid physical range [{spec.min_val}, {spec.max_val}]."
                )
                continue

            sanitized[name] = numeric_val

    if errors:
        raise ValidationError("Input parameter validation failed.", details=errors)

    # Attach display metadata
    sanitized.update(display_info)

    # Process extended agricultural parameters
    # 1. Farm Area and Unit
    raw_area = raw_data.get("farm_area")
    raw_unit = str(raw_data.get("farm_area_unit") or "hectare").strip().lower()
    if raw_area is not None and str(raw_area).strip() != "":
        try:
            area_val = float(raw_area)
            if area_val <= 0 or math.isnan(area_val) or math.isinf(area_val):
                area_val = 1.0
        except (ValueError, TypeError):
            area_val = 1.0
    else:
        area_val = 1.0

    sanitized["farm_area"] = round(area_val, 2)
    sanitized["farm_area_unit"] = "acre" if "acre" in raw_unit else "hectare"
    sanitized["farm_area_ha"] = area_to_hectares(area_val, raw_unit)

    # 2. Electrical Conductivity (EC in dS/m)
    raw_ec = raw_data.get("electrical_conductivity")
    if raw_ec is None:
        raw_ec = raw_data.get("ec")
    if raw_ec is not None and str(raw_ec).strip() != "":
        try:
            ec_val = float(raw_ec)
            if ec_val < 0.0 or ec_val > 30.0 or math.isnan(ec_val) or math.isinf(ec_val):
                ec_val = 0.6
        except (ValueError, TypeError):
            ec_val = 0.6
    else:
        ec_val = 0.6
    sanitized["electrical_conductivity"] = round(ec_val, 2)
    sanitized["ec"] = sanitized["electrical_conductivity"]

    # 3. Organic Carbon (OC in %) vs Organic Matter (OM in %)
    raw_oc = raw_data.get("organic_carbon")
    if raw_oc is None:
        raw_oc = raw_data.get("oc")
    if raw_oc is not None and str(raw_oc).strip() != "":
        try:
            oc_val = float(raw_oc)
            if oc_val < 0.0 or oc_val > 15.0 or math.isnan(oc_val) or math.isinf(oc_val):
                oc_val = round(sanitized.get("organic_matter", 3.5) / 1.724, 2)
        except (ValueError, TypeError):
            oc_val = round(sanitized.get("organic_matter", 3.5) / 1.724, 2)
    else:
        oc_val = round(sanitized.get("organic_matter", 3.5) / 1.724, 2)
    sanitized["organic_carbon"] = round(oc_val, 2)
    sanitized["oc"] = sanitized["organic_carbon"]

    # 4. Location and Season
    loc_val = str(raw_data.get("location") or "Local Farm").strip()
    sanitized["location"] = loc_val or "Local Farm"

    season_raw = raw_data.get("season")
    sanitized["season"] = canonical_season(season_raw)

    # 5. Expected Rainfall (24-48h forecast)
    raw_exp_rain = raw_data.get("expected_rainfall_24h")
    if raw_exp_rain is None:
        raw_exp_rain = raw_data.get("forecast_rainfall")
    if raw_exp_rain is not None and str(raw_exp_rain).strip() != "":
        try:
            exp_rain_val = float(raw_exp_rain)
            if exp_rain_val < 0.0 or math.isnan(exp_rain_val) or math.isinf(exp_rain_val):
                exp_rain_val = 0.0
        except (ValueError, TypeError):
            exp_rain_val = 0.0
    else:
        exp_rain_val = 0.0
    sanitized["expected_rainfall_24h"] = round(exp_rain_val, 1)

    return sanitized

