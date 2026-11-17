"""
Interactive What-If Simulation Engine (Module 5 XAI).
Allows farmers and agronomists to simulate hypothetical changes in weather, soil, or farm inputs
and observe sensitivity shifts in crop recommendations.
"""

from typing import Dict, Any, List
from agrisathi.core.validator import validate_farm_input, FEATURE_NAMES
from agrisathi.core.schemas import (
    EXTENDED_FEATURE_DEFINITIONS,
    canonical_soil_type,
    canonical_growth_stage,
    canonical_water_source,
)
from agrisathi.ml.predictor import get_predictor


_CANONICAL_CATEGORICAL_MAP = {
    "soil_type": (canonical_soil_type, 2),
    "growth_stage": (canonical_growth_stage, 2),
    "water_source_type": (canonical_water_source, 1),
}


def simulate_what_if(
    baseline_data: Dict[str, Any],
    adjustments: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Simulates hypothetical adjustments applied to baseline farm conditions.
    Computes delta in probabilities, rank shifts, and sensitivity narratives.
    """
    predictor = get_predictor()

    # Validate and sanitize baseline with sensible defaults allowed for what-if exploration
    sanitized_base = validate_farm_input(baseline_data, allow_defaults=True)
    base_prediction = predictor.predict(sanitized_base)

    # Apply adjustments over baseline
    modified_data = dict(sanitized_base)
    applied_changes: List[Dict[str, Any]] = []

    supported_fields = set(FEATURE_NAMES) | {s.name for s in EXTENDED_FEATURE_DEFINITIONS}

    for field, new_val in adjustments.items():
        if field not in supported_fields or new_val is None:
            continue

        if isinstance(new_val, str) and not new_val.strip():
            continue

        # Remove cached display label to prevent stale label shadowing
        modified_data.pop(f"{field}_label", None)

        if isinstance(new_val, bool):
            modified_data[field] = new_val
            continue

        if field in _CANONICAL_CATEGORICAL_MAP:
            canon_fn, default_val = _CANONICAL_CATEGORICAL_MAP[field]
            old_display = sanitized_base.get(f"{field}_label") or canon_fn(sanitized_base.get(field, default_val))
            new_display = canon_fn(new_val)

            if old_display != new_display:
                modified_data[field] = new_display
                applied_changes.append({
                    "field": field,
                    "old_value": old_display,
                    "new_value": new_display,
                    "delta": 0.0,
                })
        else:
            old_val = sanitized_base.get(field)
            try:
                num_new = float(new_val)
                modified_data[field] = num_new
                if old_val is None or abs(num_new - float(old_val)) > 1e-4:
                    applied_changes.append({
                        "field": field,
                        "old_value": old_val,
                        "new_value": num_new,
                        "delta": round(num_new - float(old_val), 2) if old_val is not None else 0.0,
                    })
            except (ValueError, TypeError):
                modified_data[field] = new_val

    # Validate and predict on modified data
    sanitized_mod = validate_farm_input(modified_data, allow_defaults=True)
    sim_prediction = predictor.predict(sanitized_mod)

    # Compare crop probabilities
    base_probs = {p["crop"].lower(): p["percentage"] for p in base_prediction["probabilities"]}
    sim_probs = {p["crop"].lower(): p["percentage"] for p in sim_prediction["probabilities"]}

    all_crops = list(dict.fromkeys(list(base_probs.keys()) + list(sim_probs.keys())))
    shifts = []
    for c in all_crops:
        bp = base_probs.get(c, 0.0)
        sp = sim_probs.get(c, 0.0)
        shift = round(sp - bp, 1)
        shifts.append({
            "crop": c.title(),
            "baseline_percentage": bp,
            "simulated_percentage": sp,
            "shift_percentage": shift,
            "direction": "positive" if shift > 0 else ("negative" if shift < 0 else "neutral"),
        })

    shifts.sort(key=lambda x: abs(x["shift_percentage"]), reverse=True)

    base_crop = base_prediction["recommended_crop"].title()
    sim_crop = sim_prediction["recommended_crop"].title()
    rec_changed = (base_crop.lower() != sim_crop.lower())

    # Build sensitivity narrative
    change_summaries = []
    for ch in applied_changes:
        field_name = ch["field"].replace("_", " ").title()
        if ch["delta"] != 0.0:
            sign = "+" if ch["delta"] > 0 else ""
            change_summaries.append(f"{field_name} by {sign}{ch['delta']}")
        else:
            change_summaries.append(f"{field_name} from {ch['old_value']} to {ch['new_value']}")

    changes_text = ", ".join(change_summaries) if change_summaries else "selected parameters"

    if rec_changed:
        insight = (
            f"Changing {changes_text} shifted the primary AI recommendation from "
            f"{base_crop} ({base_prediction['confidence']}%) to {sim_crop} ({sim_prediction['confidence']}%)."
        )
    else:
        conf_delta = round(sim_prediction['confidence'] - base_prediction['confidence'], 1)
        sign = "+" if conf_delta >= 0 else ""
        insight = (
            f"Under modified conditions ({changes_text}), {base_crop} remains the primary recommendation "
            f"with confidence shifting by {sign}{conf_delta}% (now {sim_prediction['confidence']}%)."
        )

    return {
        "baseline_crop": base_crop,
        "baseline_confidence": base_prediction["confidence"],
        "simulated_crop": sim_crop,
        "simulated_confidence": sim_prediction["confidence"],
        "recommendation_changed": rec_changed,
        "changes_applied": applied_changes,
        "probability_shifts": shifts[:6],
        "insight_summary": insight,
        "baseline_prediction": base_prediction,
        "simulated_prediction": sim_prediction,
    }
