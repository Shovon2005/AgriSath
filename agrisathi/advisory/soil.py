"""
Soil Health Assessment Engine.
Analyzes soil reaction (pH), organic matter, texture, and nutrient retention
using dynamic agronomic thresholds.
"""

from typing import Dict, Any, List
from agrisathi.advisory.profiles import get_soil_properties, get_soil_thresholds, get_crop_profile
from agrisathi.core.schemas import canonical_soil_type


def _safe_float(val: Any, default: float) -> float:
    """Null-safe float parser respecting valid 0.0 values."""
    if val is None:
        return default
    try:
        f = float(val)
        return default if (f != f or f == float("inf") or f == float("-inf")) else f
    except (ValueError, TypeError):
        return default


def assess_soil_health(
    farm_data: Dict[str, Any],
    crop_name: str = None,
    crop_profile: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Comprehensive agronomic soil health assessment.
    Returns status, numerical soil health score (0-100), issues list, and recommendations.
    Accepts crop_name (str) and/or crop_profile (dict or str).
    Uses dynamic agronomic thresholds and parameters.
    """
    farm_data = farm_data or {}

    if isinstance(crop_name, dict) and crop_profile is None:
        crop_profile = crop_name
        crop_name = None

    if isinstance(crop_profile, str):
        crop_name = crop_profile
        crop_profile = None

    if crop_profile is None and crop_name:
        crop_profile = get_crop_profile(crop_name)

    thresholds = get_soil_thresholds()
    th_ph = thresholds.get("ph", {})
    th_ec = thresholds.get("electrical_conductivity", {})
    th_om = thresholds.get("organic_matter", {})
    th_oc = thresholds.get("organic_carbon", {})
    th_n = thresholds.get("nitrogen", {})
    th_p = thresholds.get("phosphorus", {})
    th_k = thresholds.get("potassium", {})
    th_score = thresholds.get("score_classification", {})
    th_fert = thresholds.get("fertility_breakpoints", {})

    ph = _safe_float(farm_data.get("ph"), 6.5)
    om = _safe_float(farm_data.get("organic_matter"), 3.5)

    # Null-safe extraction that respects valid 0.0 values
    raw_oc = farm_data.get("organic_carbon")
    if raw_oc is None:
        raw_oc = farm_data.get("oc")
    oc = _safe_float(raw_oc, round(om / 1.724, 2)) if raw_oc is not None else round(om / 1.724, 2)

    raw_ec = farm_data.get("electrical_conductivity")
    if raw_ec is None:
        raw_ec = farm_data.get("ec")
    ec = _safe_float(raw_ec, 0.6) if raw_ec is not None else 0.6

    n = _safe_float(farm_data.get("N"), 50.0)
    p = _safe_float(farm_data.get("P"), 50.0)
    k = _safe_float(farm_data.get("K"), 50.0)
    raw_soil = farm_data.get("soil_type_label") or farm_data.get("soil_type", "Loamy")
    soil_type = canonical_soil_type(raw_soil)

    issues: List[str] = []
    actions: List[str] = []
    deficiencies: List[str] = []
    excesses: List[str] = []
    score = 100

    # Dynamic Threshold Values
    ph_strong_acid = th_ph.get("strongly_acidic", 5.0)
    ph_slight_acid = th_ph.get("slightly_acidic", 6.0)
    ph_opt_min = th_ph.get("optimal_min", 6.0)
    ph_opt_max = th_ph.get("optimal_max", 7.5)
    ph_mod_alkaline = th_ph.get("moderately_alkaline", 8.5)

    ec_low = th_ec.get("low", 0.1)
    ec_opt_max = th_ec.get("optimal_max", 2.0)
    ec_severe = th_ec.get("severe_salinity", 4.0)

    om_crit_low = th_om.get("critical_low", 1.5)
    om_subopt = th_om.get("suboptimal", 3.0)
    oc_crit_low = th_oc.get("critical_low", 0.50)
    oc_opt_min = th_oc.get("optimal_min", 0.75)

    n_min = th_n.get("min", 30.0)
    n_max = th_n.get("max", 140.0)
    p_min = th_p.get("min", 25.0)
    p_max = th_p.get("max", 100.0)
    k_min = th_k.get("min", 30.0)
    k_max = th_k.get("max", 140.0)

    # 1. pH Assessment
    crop_ph_outside = False
    if crop_profile:
        min_c_ph = float(crop_profile.get("min_ph", 5.5))
        max_c_ph = float(crop_profile.get("max_ph", 7.5))
        crop_ph_outside = (ph < min_c_ph or ph > max_c_ph)

    if ph < ph_strong_acid:
        issues.append("Soil is strongly acidic (pH < 5.0), inducing aluminum/iron toxicity.")
        actions.append("Apply agricultural lime (calcium carbonate) or dolomite at 1.5 - 2.5 t/ha to buffer acidity.")
        score -= 25
    elif ph < ph_slight_acid:
        issues.append("Soil is slightly acidic (pH 5.0 - 6.0).")
        actions.append("Apply composted organic manure and monitor nutrient lockup.")
        score -= 10
    elif ph > ph_mod_alkaline:
        issues.append("Soil is strongly alkaline/sodic (pH > 8.5), restricting micronutrient uptake.")
        actions.append("Apply agricultural gypsum (CaSO₄) or elemental sulfur with leaching to reduce sodium saturation.")
        score -= 25
    elif ph > ph_opt_max:
        issues.append("Soil is moderately alkaline (pH 7.5 - 8.5).")
        actions.append("Incorporate acidic organic amendments like peat or composted pine mulch.")
        score -= 10
    else:
        if crop_ph_outside:
            crop_title = crop_profile.get("display_name", "Target crop")
            issues.append(f"Soil pH ({ph:.1f}) is within standard agricultural baseline (6.0 - 7.5), but suboptimal for {crop_title}.")
        else:
            issues.append("Soil pH is within the optimal agronomic range (6.0 - 7.5).")

    # Crop-specific pH tolerance
    if crop_profile and crop_ph_outside:
        min_c_ph = float(crop_profile.get("min_ph", 5.5))
        max_c_ph = float(crop_profile.get("max_ph", 7.5))
        crop_title = crop_profile.get("display_name", "Target crop")
        issues.append(f"Current pH {ph} is outside ideal range ({min_c_ph} - {max_c_ph}) for {crop_title}.")
        if ph < min_c_ph:
            actions.append(f"Current pH {ph} is below optimal ({min_c_ph} - {max_c_ph}) for {crop_title}; apply agricultural lime to buffer acidity.")
        else:
            actions.append(f"Current pH {ph} exceeds optimal ({min_c_ph} - {max_c_ph}) for {crop_title}; incorporate gypsum or sulfur-based amendments.")
        score -= 10

    # 2. Electrical Conductivity (EC) / Salinity Assessment
    if ec > ec_severe:
        issues.append(f"Soil is severely saline (EC: {ec:.2f} dS/m), creating strong osmotic root stress.")
        actions.append("Implement heavy leaching with low-salinity irrigation water and construct deep drainage ditches.")
        score -= 25
    elif ec > ec_opt_max:
        issues.append(f"Soil shows moderate salinity hazard (EC: {ec:.2f} dS/m).")
        actions.append("Avoid saline well-water irrigation; select salt-tolerant crops and apply organic mulches.")
        score -= 12
    elif ec < ec_low:
        issues.append(f"Soil EC is exceptionally low ({ec:.2f} dS/m), indicating low soluble mineral salt reserves.")
        actions.append("Incorporate balanced mineral fertilizers with micro-nutrients.")
        score -= 5
    else:
        issues.append(f"Electrical Conductivity is within the optimal non-saline range ({ec:.2f} dS/m).")

    # 3. Organic Matter (OM) and Organic Carbon (OC) Assessment
    if om < om_crit_low or oc < oc_crit_low:
        issues.append("Organic matter is critically deficient (< 1.5%).")
        actions.append("Apply 10-15 t/ha well-decomposed Farm Yard Manure (FYM) or vermicompost.")
        deficiencies.append(f"Organic Matter/Carbon ({om:.1f}% OM, {oc:.2f}% OC)")
        score -= 20
    elif om < om_subopt or oc < oc_opt_min:
        issues.append("Organic matter is below optimal levels (< 3.0%).")
        actions.append("Practice green manuring (e.g. Sesbania/Dhaincha) and retain crop residues.")
        score -= 10
    else:
        issues.append("Soil organic matter content is healthy (≥ 3.0%).")

    # 4. Macro-nutrient Baseline Check
    if n < n_min:
        issues.append(f"Nitrogen level is relatively low (< {n_min:.0f} mg/kg).")
        actions.append("Apply organic compost, well-decomposed manure, or basal nitrogenous fertilizer to restore the soil nitrogen pool.")
        deficiencies.append(f"Nitrogen ({n:.1f} mg/kg)")
        score -= 10
    elif n > n_max:
        issues.append(f"Nitrogen level is excessively high ({n:.1f} mg/kg); risk of vegetative lodging and delayed harvest.")
        actions.append("Avoid synthetic nitrogen top-dressing; irrigate cautiously to prevent nitrate leaching.")
        excesses.append(f"Nitrogen ({n:.1f} mg/kg)")
        score -= 5

    if p < p_min:
        issues.append(f"Phosphorus level is relatively low (< {p_min:.0f} mg/kg).")
        actions.append("Incorporate rock phosphate, bone meal, or single superphosphate (SSP) to support root proliferation.")
        deficiencies.append(f"Phosphorus ({p:.1f} mg/kg)")
        score -= 10
    elif p > p_max:
        issues.append(f"Phosphorus level is very high ({p:.1f} mg/kg); risk of zinc/iron micronutrient lockup.")
        actions.append("Omit phosphate applications; monitor foliage for micronutrient chlorosis.")
        excesses.append(f"Phosphorus ({p:.1f} mg/kg)")
        score -= 5

    if k < k_min:
        issues.append(f"Potassium level is relatively low (< {k_min:.0f} mg/kg).")
        actions.append("Apply muriate of potash (MOP) or incorporate potassium-rich crop residues/biochar.")
        deficiencies.append(f"Potassium ({k:.1f} mg/kg)")
        score -= 10
    elif k > k_max:
        issues.append(f"Potassium level is elevated ({k:.1f} mg/kg); competitive inhibition with calcium and magnesium uptake.")
        actions.append("Avoid potash applications to prevent cation antagonism with magnesium uptake.")
        excesses.append(f"Potassium ({k:.1f} mg/kg)")
        score -= 5

    # 5. Soil Texture Synergy
    soil_props = get_soil_properties()
    texture_info = soil_props.get(soil_type, soil_props.get("Loamy", {}))

    score = max(10, min(100, score))
    good_min = int(th_score.get("good_min", 85))
    needs_attn_min = int(th_score.get("needs_attention_min", 60))

    if score >= good_min:
        status = "Good"
    elif score >= needs_attn_min:
        status = "Needs Attention"
    else:
        status = "Poor"

    # Soil Fertility Classification: "Low", "Medium", or "High"
    fertility_points = 0
    if n >= th_n.get("fertility_high", 50.0):
        fertility_points += 2
    elif n >= th_n.get("fertility_medium", 30.0):
        fertility_points += 1

    if p >= th_p.get("fertility_high", 35.0):
        fertility_points += 2
    elif p >= th_p.get("fertility_medium", 20.0):
        fertility_points += 1

    if k >= th_k.get("fertility_high", 45.0):
        fertility_points += 2
    elif k >= th_k.get("fertility_medium", 25.0):
        fertility_points += 1

    if oc >= oc_opt_min:
        fertility_points += 2
    elif oc >= oc_crit_low:
        fertility_points += 1

    fert_ph_opt_min = _safe_float(th_fert.get("ph_optimal_min"), 6.0)
    fert_ph_opt_max = _safe_float(th_fert.get("ph_optimal_max"), 7.8)
    fert_ph_acc_min = _safe_float(th_fert.get("ph_acceptable_min"), 5.2)
    fert_ph_acc_max = _safe_float(th_fert.get("ph_acceptable_max"), 8.5)
    fert_ec_good = _safe_float(th_fert.get("ec_good_max"), 1.8)
    score_severe_min = int(th_fert.get("score_severe_min", 45))
    pts_high_min = int(th_fert.get("points_high_min", 9))
    pts_med_min = int(th_fert.get("points_medium_min", 5))

    if fert_ph_opt_min <= ph <= fert_ph_opt_max:
        fertility_points += 2
    elif fert_ph_acc_min <= ph <= fert_ph_acc_max:
        fertility_points += 1

    if ec < fert_ec_good:
        fertility_points += 1

    # Salinity and severe degradation capping
    if ec > ec_severe or score < score_severe_min:
        fertility_class = "Low"
    elif fertility_points >= pts_high_min and len(deficiencies) == 0:
        fertility_class = "High"
    elif fertility_points >= pts_med_min:
        fertility_class = "Medium"
    else:
        fertility_class = "Low"

    return {
        "status": status,
        "fertility_class": fertility_class,
        "score": score,
        "ph": ph,
        "organic_matter": om,
        "organic_carbon": oc,
        "electrical_conductivity": ec,
        "soil_texture": soil_type,
        "texture_characteristics": texture_info,
        "deficiencies": deficiencies,
        "excesses": excesses,
        "nutrients_analysis": {
            "nitrogen": {
                "value": n,
                "status": "Excess" if n > n_max else ("Deficient" if n < n_min else "Optimal"),
                "unit": "mg/kg",
            },
            "phosphorus": {
                "value": p,
                "status": "Excess" if p > p_max else ("Deficient" if p < p_min else "Optimal"),
                "unit": "mg/kg",
            },
            "potassium": {
                "value": k,
                "status": "Excess" if k > k_max else ("Deficient" if k < k_min else "Optimal"),
                "unit": "mg/kg",
            },
            "ph": {
                "value": ph,
                "status": "Alkaline" if ph > ph_opt_max else ("Acidic" if ph < ph_slight_acid else "Optimal"),
                "unit": "pH",
            },
            "electrical_conductivity": {
                "value": ec,
                "status": "Saline" if ec > ec_opt_max else "Normal",
                "unit": "dS/m",
            },
            "organic_carbon": {
                "value": oc,
                "status": "Low" if oc < oc_crit_low else ("High" if oc >= oc_opt_min else "Medium"),
                "unit": "%",
            },
        },
        "issues": issues,
        "corrective_actions": actions,
    }
