"""
Crop-Specific Fertilizer Recommendation Engine.
Calculates NPK nutritional deficits and commercial fertilizer dosages (Urea, DAP, MOP).
"""

from typing import Dict, Any, List
from agrisathi.advisory.profiles import FERTILIZER_CONVERSIONS, get_crop_profile


def calculate_fertilizer_guidance(
    farm_data: Dict[str, Any],
    crop_name: str = None,
    crop_profile: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Computes precise fertilizer guidance based on current soil NPK and target crop requirements.
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

    current_n = float(farm_data.get("N", 50))
    current_p = float(farm_data.get("P", 50))
    current_k = float(farm_data.get("K", 50))

    opt_n = float(crop_profile.get("opt_n", 80))
    opt_p = float(crop_profile.get("opt_p", 40))
    opt_k = float(crop_profile.get("opt_k", 40))

    crop_title = crop_profile.get("display_name", crop_name or "Target Crop")

    # Deficits in kg/ha
    deficit_n = max(0.0, opt_n - current_n)
    deficit_p = max(0.0, opt_p - current_p)
    deficit_k = max(0.0, opt_k - current_k)

    # 1. Calculate DAP needed for Phosphorus deficit
    # DAP: 18% N, 46% P2O5
    if deficit_p > 0:
        dap_kg_ha = deficit_p / FERTILIZER_CONVERSIONS["dap_p_fraction"]
        n_supplied_by_dap = dap_kg_ha * FERTILIZER_CONVERSIONS["dap_n_fraction"]
    else:
        dap_kg_ha = 0.0
        n_supplied_by_dap = 0.0

    # 2. Remaining Nitrogen supplied via Urea (46% N)
    remaining_n = max(0.0, deficit_n - n_supplied_by_dap)
    urea_kg_ha = remaining_n / FERTILIZER_CONVERSIONS["urea_n_fraction"] if remaining_n > 0 else 0.0

    # 3. Potassium supplied via MOP (60% K2O)
    mop_kg_ha = deficit_k / FERTILIZER_CONVERSIONS["mop_k_fraction"] if deficit_k > 0 else 0.0

    recommendations: List[str] = []

    if deficit_n > 0:
        recommendations.append(
            f"Nitrogen deficit of {deficit_n:.1f} kg/ha detected for optimal {crop_title} yield."
        )
    if deficit_p > 0:
        recommendations.append(
            f"Phosphorus deficit of {deficit_p:.1f} kg/ha detected for root development."
        )
    if deficit_k > 0:
        recommendations.append(
            f"Potassium deficit of {deficit_k:.1f} kg/ha detected for disease resistance."
        )

    if not recommendations:
        recommendations.append(
            f"Soil NPK levels ({current_n:.0f}-{current_p:.0f}-{current_k:.0f}) are sufficient for {crop_title}."
        )
    else:
        recommendations.append(
            f"Recommended commercial dosage: Urea: {urea_kg_ha:.1f} kg/ha, "
            f"DAP: {dap_kg_ha:.1f} kg/ha, MOP: {mop_kg_ha:.1f} kg/ha."
        )

    # Application split guidance
    schedule = [
        "Basal Application (at sowing): Apply 100% of DAP, 100% of MOP, and 33% of Urea.",
        "First Top-Dressing (active vegetative stage): Apply 33% of Urea with light irrigation.",
        "Second Top-Dressing (panicle/flowering initiation): Apply remaining 34% of Urea.",
    ]

    return {
        "crop": crop_title,
        "recommendations": recommendations,
        "soil_npk": {"N": current_n, "P": current_p, "K": current_k},
        "target_npk": {"N": opt_n, "P": opt_p, "K": opt_k},
        "deficits": {
            "N": round(deficit_n, 1),
            "P": round(deficit_p, 1),
            "K": round(deficit_k, 1),
        },
        "commercial_fertilizers": {
            "urea_kg_ha": round(urea_kg_ha, 1),
            "dap_kg_ha": round(dap_kg_ha, 1),
            "mop_kg_ha": round(mop_kg_ha, 1),
        },
        "application_schedule": schedule,
    }
