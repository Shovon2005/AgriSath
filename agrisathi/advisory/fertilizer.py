"""
Crop-Specific Fertilizer Recommendation Engine.
Calculates NPK nutritional deficits and commercial fertilizer dosages (Urea, DAP, SSP, MOP)
using dynamic agronomic conversion rates and organic alternatives.
"""

from typing import Dict, Any, List
from agrisathi.advisory.profiles import (
    get_fertilizer_conversions,
    get_organic_guidelines,
    resolve_crop_profile,
)
from agrisathi.core.schemas import safe_float as _safe_float


def calculate_fertilizer_guidance(
    farm_data: Dict[str, Any],
    crop_name: str = None,
    crop_profile: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Computes precise fertilizer guidance based on current soil NPK and target crop requirements.
    Accepts crop_name (str) and/or crop_profile (dict or str).
    Uses dynamic conversions and organic guidelines.
    """
    farm_data = farm_data or {}
    crop_name, crop_profile = resolve_crop_profile(crop_name, crop_profile, default_crop="rice")

    conversions = get_fertilizer_conversions()
    guidelines = get_organic_guidelines()

    urea_n_fraction = _safe_float(conversions.get("urea_n_fraction"), 0.46)
    dap_n_fraction = _safe_float(conversions.get("dap_n_fraction"), 0.18)
    dap_p_fraction = _safe_float(conversions.get("dap_p_fraction"), 0.46)
    ssp_p_fraction = _safe_float(conversions.get("ssp_p_fraction"), 0.16)
    mop_k_fraction = _safe_float(conversions.get("mop_k_fraction"), 0.60)
    bag_weight = _safe_float(conversions.get("commercial_bag_weight_kg"), 50.0)
    surplus_mult = _safe_float(conversions.get("surplus_multiplier"), 1.5)

    current_n = _safe_float(farm_data.get("N"), 50.0)
    current_p = _safe_float(farm_data.get("P"), 50.0)
    current_k = _safe_float(farm_data.get("K"), 50.0)

    opt_n = _safe_float(crop_profile.get("opt_n"), 80.0)
    opt_p = _safe_float(crop_profile.get("opt_p"), 40.0)
    opt_k = _safe_float(crop_profile.get("opt_k"), 40.0)

    crop_title = crop_profile.get("display_name", crop_name or "Target Crop")

    # Deficits in kg/ha, rounded to 1 decimal place
    deficit_n = round(max(0.0, opt_n - current_n), 1)
    deficit_p = round(max(0.0, opt_p - current_p), 1)
    deficit_k = round(max(0.0, opt_k - current_k), 1)

    # 1. Calculate DAP needed for Phosphorus deficit
    # DAP: 18% N, 46% P2O5
    if deficit_p > 0.0:
        dap_kg_ha = deficit_p / dap_p_fraction
        n_supplied_by_dap = dap_kg_ha * dap_n_fraction
    else:
        dap_kg_ha = 0.0
        n_supplied_by_dap = 0.0

    # 2. Remaining Nitrogen supplied via Urea (46% N)
    remaining_n = max(0.0, deficit_n - n_supplied_by_dap)
    urea_kg_ha = remaining_n / urea_n_fraction if remaining_n > 0.0 else 0.0

    # 3. Potassium supplied via MOP (60% K2O)
    mop_kg_ha = deficit_k / mop_k_fraction if deficit_k > 0.0 else 0.0

    # 4. Alternative Phosphorus source: SSP (Single Superphosphate, 16% P2O5)
    ssp_kg_ha = deficit_p / ssp_p_fraction if deficit_p > 0.0 else 0.0

    urea_rounded = round(urea_kg_ha, 1)
    dap_rounded = round(dap_kg_ha, 1)
    ssp_rounded = round(ssp_kg_ha, 1)
    mop_rounded = round(mop_kg_ha, 1)

    # 5. Farm Area Scaling (Total kg & commercial bags)
    raw_area_ha = _safe_float(farm_data.get("farm_area_ha"), 1.0)
    farm_area_ha = max(0.01, raw_area_ha)

    rates = {"urea": urea_rounded, "dap": dap_rounded, "ssp": ssp_rounded, "mop": mop_rounded}
    totals = {k: round(v * farm_area_ha, 1) for k, v in rates.items()}
    bags = {k: round(v / bag_weight, 1) for k, v in totals.items()}

    # 6. Organic Alternatives and Bio-fertilizers
    crop_category = crop_profile.get("category", "General")
    ph = _safe_float(farm_data.get("ph"), 6.5)

    fym_rate = _safe_float(guidelines.get("fym", {}).get("rate_per_ha_tonnes"), 10.0)
    vermicompost_rate = _safe_float(guidelines.get("vermicompost", {}).get("rate_per_ha_tonnes"), 3.0)
    neem_rate = _safe_float(guidelines.get("neem_cake", {}).get("rate_per_ha_kg"), 250.0)
    bio_text = guidelines.get("biofertilizers", {})

    organic_alternatives = {
        "compost_fym_tonnes": round(fym_rate * farm_area_ha, 1),
        "vermicompost_tonnes": round(vermicompost_rate * farm_area_ha, 1),
        "neem_cake_kg": round(neem_rate * farm_area_ha, 1),
        "biofertilizer": (
            bio_text.get("pulses", "Rhizobium leguminosarum (200 g/10 kg seed) + PSB (2 kg/ha) for symbiotic nitrogen fixation.")
            if crop_category == "Pulses"
            else bio_text.get("cereals", "Azotobacter / Azospirillum (2 kg/ha) + PSB (2 kg/ha) incorporated with organic manure.")
        ),
        "soil_conditioning": (
            "Soil is slightly acidic; SSP is preferred over DAP as it delivers 11% essential sulfur and 19% calcium."
            if ph < 6.0
            else "Incorporate compost/green manure to improve cation exchange capacity (CEC) and mitigate nutrient volatilization."
        )
    }

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

    # Surplus checks using dynamic surplus multiplier
    if current_n > opt_n * surplus_mult and opt_n > 0:
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

    if current_p > opt_p * surplus_mult and opt_p > 0:
        recommendations.append(
            f"Soil Phosphorus ({current_p:.0f} mg/kg) is in notable surplus over target ({opt_p:.0f} mg/kg); "
            "omit phosphate applications to avoid zinc and iron micronutrient lockup."
        )

    if current_k > opt_k * surplus_mult and opt_k > 0:
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

        split_urea_1 = round(urea_rounded * 0.33, 1)
        split_urea_2 = round(urea_rounded * 0.33, 1)
        split_urea_3 = round(urea_rounded - split_urea_1 - split_urea_2, 1)

        if urea_rounded > 0.0 and (urea_rounded < 1.5 or split_urea_1 == 0.0):
            basal_parts.append(f"100% of Urea ({urea_rounded:.1f} kg/ha)")
            top_dressing = [
                "Top-Dressing: No split top-dressing required for minimal nitrogen dosage; full requirement satisfied at basal application."
            ]
        elif urea_rounded > 0.0:
            basal_parts.append(f"33% of Urea ({split_urea_1:.1f} kg/ha)")
            top_dressing = [
                f"First Top-Dressing (active vegetative stage): Apply 33% of Urea ({split_urea_2:.1f} kg/ha) with light irrigation.",
                f"Second Top-Dressing (panicle/flowering initiation): Apply remaining {split_urea_3:.1f} kg/ha of Urea.",
            ]
        else:
            top_dressing = [
                "Top-Dressing: No synthetic nitrogen top-dressing required as baseline soil nitrogen is sufficient."
            ]

        schedule = [f"Basal Application (at sowing): Apply {', '.join(basal_parts)}."] + top_dressing

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
            "ssp_kg_ha": ssp_rounded,
            "mop_kg_ha": mop_rounded,
        },
        "farm_area_ha": farm_area_ha,
        "commercial_bag_weight_kg": bag_weight,
        "total_farm_requirements": {
            "urea_kg": totals["urea"],
            "urea_bags_50kg": bags["urea"],
            "dap_kg": totals["dap"],
            "dap_bags_50kg": bags["dap"],
            "ssp_kg": totals["ssp"],
            "ssp_bags_50kg": bags["ssp"],
            "mop_kg": totals["mop"],
            "mop_bags_50kg": bags["mop"],
        },
        "organic_alternatives": organic_alternatives,
        "application_schedule": schedule,
    }
