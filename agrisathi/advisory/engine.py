"""
Unified Advisory Engine.
Orchestrates soil health, fertilizer dosing, irrigation scheduling, and multi-hazard risk assessment.
"""

from typing import Dict, Any, List, Optional, Tuple
from agrisathi.advisory.profiles import get_crop_profile
from agrisathi.advisory.soil import assess_soil_health
from agrisathi.advisory.fertilizer import calculate_fertilizer_guidance
from agrisathi.advisory.irrigation import calculate_irrigation_advisory
from agrisathi.advisory.risk import assess_environmental_risks
from agrisathi.advisory.comparison import build_crop_comparison_matrix


def generate_full_advisory(
    farm_data: Dict[str, Any],
    recommended_crop: str,
    top_crops: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Coordinates all agronomic advisory sub-engines for the target recommended crop.
    Also builds Top-3 crop suitability comparison matrix.
    """
    crop_profile = get_crop_profile(recommended_crop)

    soil = assess_soil_health(farm_data, recommended_crop, crop_profile)
    fertilizer = calculate_fertilizer_guidance(farm_data, recommended_crop, crop_profile)
    irrigation = calculate_irrigation_advisory(farm_data, recommended_crop, crop_profile)
    risks = assess_environmental_risks(farm_data, recommended_crop, crop_profile)

    crops_to_compare = top_crops if top_crops else [{"crop": recommended_crop, "percentage": 100.0}]
    comparison = build_crop_comparison_matrix(crops_to_compare, farm_data, limit=3)

    return {
        "crop_name": recommended_crop,
        "crop_profile": crop_profile,
        "soil": soil,
        "fertilizer": fertilizer,
        "irrigation": irrigation,
        "risks": risks,
        "crop_comparison": comparison,
    }


def run_full_pipeline(
    raw_data: Dict[str, Any],
    allow_defaults: bool = False,
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Unified pipeline executing input validation, ML crop inference, and complete agronomic advisory."""
    from agrisathi.core.validator import validate_farm_input
    from agrisathi.ml.predictor import get_predictor

    sanitized = validate_farm_input(raw_data, allow_defaults=allow_defaults)
    prediction = get_predictor().predict(sanitized)
    advisory = generate_full_advisory(
        sanitized,
        prediction["recommended_crop"],
        top_crops=prediction.get("top_three"),
    )
    return sanitized, prediction, advisory


