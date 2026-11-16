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

    # Deficits in kg/ha, rounded to 1 decimal place
    deficit_n = round(max(0.0, opt_n - current_n), 1)
    deficit_p = round(max(0.0, opt_p - current_p), 1)
    deficit_k = round(max(0.0, opt_k - current_k), 1)

    # 1. Calculate DAP needed for Phosphorus deficit
    # DAP: 18% N, 46% P2O5
    if deficit_p > 0.0:
        dap_kg_ha = deficit_p / FERTILIZER_CONVERSIONS["dap_p_fraction"]
        n_supplied_by_dap = dap_kg_ha * FERTILIZER_CONVERSIONS["dap_n_fraction"]
    else:
        dap_kg_ha = 0.0
        n_supplied_by_dap = 0.0

    # 2. Remaining Nitrogen supplied via Urea (46% N)
    remaining_n = max(0.0, deficit_n - n_supplied_by_dap)
    urea_kg_ha = remaining_n / FERTILIZER_CONVERSIONS["urea_n_fraction"] if remaining_n > 0.0 else 0.0

    # 3. Potassium supplied via MOP (60% K2O)
    mop_kg_ha = deficit_k / FERTILIZER_CONVERSIONS["mop_k_fraction"] if deficit_k > 0.0 else 0.0

    urea_rounded = round(urea_kg_ha, 1)
    dap_rounded = round(dap_kg_ha, 1)
    mop_rounded = round(mop_kg_ha, 1)

    recommendations: List[str] = []

    if deficit_n > 0.0:
        recommendations.append(
            f"Nitrogen deficit of {deficit_n:.1f} kg/ha detected for optimal {crop_title} yield."
        )
    if deficit_p > 0.0:
        recommendations.append(
            f"Phosphorus deficit of {deficit_p:.1f} kg/ha detected for root development."
        )
    if deficit_k > 0.0:
        recommendations.append(
            f"Potassium deficit of {deficit_k:.1f} kg/ha detected for disease resistance."
        )

    if not recommendations or (urea_rounded == 0.0 and dap_rounded == 0.0 and mop_rounded == 0.0):
        if not recommendations:
            recommendations.append(
                f"Soil NPK levels ({current_n:.0f}-{current_p:.0f}-{current_k:.0f}) are sufficient for {crop_title}."
            )
        else:
            recommendations = [
                f"Soil NPK levels ({current_n:.0f}-{current_p:.0f}-{current_k:.0f}) are sufficient for {crop_title}. "
                "Minor deficits are negligible and require no synthetic fertilizer supplementation."
            ]
    else:
        recommendations.append(
            f"Recommended commercial dosage: Urea: {urea_rounded:.1f} kg/ha, "
            f"DAP: {dap_rounded:.1f} kg/ha, MOP: {mop_rounded:.1f} kg/ha."
        )

    # Surplus checks
    if current_n > opt_n * 1.5 and opt_n > 0:
        crop_category = crop_profile.get("category", "")
        if crop_category == "Pulses":
            recommendations.append(
                f"Soil Nitrogen ({current_n:.0f} mg/kg) exceeds pulse demand ({opt_n:.0f} mg/kg); "
                "excess nitrogen inhibits Rhizobium nodulation and biological nitrogen fixation."
            )
        else:
            recommendations.append(
                f"Soil Nitrogen ({current_n:.0f} mg/kg) is in substantial surplus over target ({opt_n:.0f} mg/kg); "
                "avoid nitrogenous fertilizers to prevent vegetative lodging and delayed harvest."
            )

    if current_p > opt_p * 1.5 and opt_p > 0:
        recommendations.append(
            f"Soil Phosphorus ({current_p:.0f} mg/kg) is in notable surplus over target ({opt_p:.0f} mg/kg); "
            "omit phosphate applications to avoid zinc and iron micronutrient lockup."
        )

    if current_k > opt_k * 1.5 and opt_k > 0:
        recommendations.append(
            f"Soil Potassium ({current_k:.0f} mg/kg) is in notable surplus over target ({opt_k:.0f} mg/kg); "
            "avoid potash applications to prevent cation antagonism with magnesium uptake."
        )

    # Dynamic application split guidance tailored to prescribed fertilizers
    if urea_rounded == 0.0 and dap_rounded == 0.0 and mop_rounded == 0.0:
        schedule = [
            "Soil nutrient reserves are sufficient. No chemical fertilizer application required for basal or top-dressing."
        ]
    else:
        basal_parts = []
        if dap_rounded > 0.0:
            basal_parts.append(f"100% of DAP ({dap_rounded:.1f} kg/ha)")
        if mop_rounded > 0.0:
            basal_parts.append(f"100% of MOP ({mop_rounded:.1f} kg/ha)")

        # Handle Urea application splits:
        # If urea dosage is minimal (< 1.5 kg/ha) or split doses would round to 0.0 kg/ha,
        # apply entire urea dosage as basal to avoid meaningless 0.0 kg/ha splits.
        split_urea_1 = round(urea_rounded * 0.33, 1)
        split_urea_2 = round(urea_rounded * 0.33, 1)
        split_urea_3 = round(urea_rounded - split_urea_1 - split_urea_2, 1)

        if urea_rounded > 0.0 and (urea_rounded < 1.5 or split_urea_1 == 0.0):
            basal_parts.append(f"100% of Urea ({urea_rounded:.1f} kg/ha)")
            schedule = [
                f"Basal Application (at sowing): Apply {', '.join(basal_parts)}."
            ]
            schedule.append(
                "Top-Dressing: No split top-dressing required for minimal nitrogen dosage; full requirement satisfied at basal application."
            )
        elif urea_rounded > 0.0:
            basal_parts.append(f"33% of Urea ({split_urea_1:.1f} kg/ha)")
            schedule = [
                f"Basal Application (at sowing): Apply {', '.join(basal_parts)}."
            ]
            schedule.append(
                f"First Top-Dressing (active vegetative stage): Apply 33% of Urea ({split_urea_2:.1f} kg/ha) with light irrigation."
            )
            schedule.append(
                f"Second Top-Dressing (panicle/flowering initiation): Apply remaining {split_urea_3:.1f} kg/ha of Urea."
            )
        else:
            schedule = [
                f"Basal Application (at sowing): Apply {', '.join(basal_parts)}."
            ]
            schedule.append(
                "Top-Dressing: No synthetic nitrogen top-dressing required as baseline soil nitrogen is sufficient."
            )

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
            "urea_kg_ha": urea_rounded,
            "dap_kg_ha": dap_rounded,
            "mop_kg_ha": mop_rounded,
        },
        "application_schedule": schedule,
    }
