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
    canonical_season,
    area_to_hectares,
    safe_float,
)

_CATEGORICAL_LOOKUP = {
    "soil_type": (
        {"1": (1, "Clay"), "clay": (1, "Clay"), "2": (2, "Loamy"), "loamy": (2, "Loamy"), "3": (3, "Sandy"), "sandy": (3, "Sandy")},
        "Clay, Loamy, Sandy",
    ),
    "growth_stage": (
        {"1": (1, "Seedling"), "seedling": (1, "Seedling"), "2": (2, "Vegetative"), "vegetative": (2, "Vegetative"), "3": (3, "Flowering"), "flowering": (3, "Flowering"), "4": (4, "Maturity"), "maturity": (4, "Maturity")},
        "Seedling, Vegetative, Flowering, Maturity",
    ),
    "water_source_type": (
        {"1": (1, "Groundwater"), "groundwater": (1, "Groundwater"), "2": (2, "Rainwater"), "rainwater": (2, "Rainwater"), "3": (3, "Canal"), "canal": (3, "Canal"), "4": (4, "River"), "river": (4, "River")},
        "Groundwater, Rainwater, Canal, River",
    ),
}


def _parse_bounded_float(
    val: Any,
    default: float,
    min_val: float = 0.0,
    max_val: float = float("inf"),
    ndigits: int = 2,
) -> float:
    """Safely parse float within bounds, respecting 0.0 and falling back to default."""
    f = safe_float(val, default)
    if f < min_val or f > max_val:
        return default
    return round(f, ndigits)


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

    if field_name not in _CATEGORICAL_LOOKUP:
        raise ValidationError(f"Unknown categorical field '{field_name}'", {"field": field_name})

    mapping, allowed = _CATEGORICAL_LOOKUP[field_name]
    str_val = str(raw_value).strip().lower()
    if str_val.endswith(".0"):
        str_val = str_val[:-2]

    if str_val in mapping:
        return mapping[str_val]

    raise ValidationError(
        f"Invalid {field_name} '{raw_value}'. Allowed values: {allowed}.",
        {"field": field_name, "value": raw_value},
    )


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
            if raw_oc_cand is not None and not isinstance(raw_oc_cand, bool) and str(raw_oc_cand).strip() != "":
                parsed_oc = safe_float(raw_oc_cand, -1.0)
                if parsed_oc >= 0.0:
                    val = round(parsed_oc * 1.724, 2)

        if val is None or (isinstance(val, str) and not val.strip()):
            if allow_defaults:
                val = spec.default
            else:
                errors[name] = f"Missing required parameter '{name}'." if name not in raw_data else f"Field '{name}' cannot be empty."
                continue

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
    area_val = _parse_bounded_float(raw_area, default=1.0, min_val=0.01, ndigits=2)
    sanitized["farm_area"] = area_val
    sanitized["farm_area_unit"] = "acre" if "acre" in raw_unit else ("bigha" if "bigha" in raw_unit else "hectare")
    sanitized["farm_area_ha"] = area_to_hectares(area_val, raw_unit)

    # 2. Electrical Conductivity (EC in dS/m)
    raw_ec = raw_data.get("electrical_conductivity") if "electrical_conductivity" in raw_data else raw_data.get("ec")
    ec_val = _parse_bounded_float(raw_ec, default=0.6, min_val=0.0, max_val=30.0, ndigits=2)
    sanitized["electrical_conductivity"] = ec_val
    sanitized["ec"] = ec_val

    # 3. Organic Carbon (OC in %) vs Organic Matter (OM in %)
    raw_oc = raw_data.get("organic_carbon") if "organic_carbon" in raw_data else raw_data.get("oc")
    default_oc = round(sanitized.get("organic_matter", 3.5) / 1.724, 2)
    oc_val = _parse_bounded_float(raw_oc, default=default_oc, min_val=0.0, max_val=15.0, ndigits=2)
    sanitized["organic_carbon"] = oc_val
    sanitized["oc"] = oc_val

    # 4. Location and Season
    loc_val = str(raw_data.get("location") or "Local Farm").strip()
    sanitized["location"] = loc_val or "Local Farm"
    sanitized["season"] = canonical_season(raw_data.get("season"))

    # 5. Expected Rainfall (24-48h forecast)
    raw_exp_rain = raw_data.get("expected_rainfall_24h") if "expected_rainfall_24h" in raw_data else raw_data.get("forecast_rainfall")
    exp_rain_val = _parse_bounded_float(raw_exp_rain, default=0.0, min_val=0.0, max_val=1000.0, ndigits=1)
    sanitized["expected_rainfall_24h"] = exp_rain_val

    return sanitized

