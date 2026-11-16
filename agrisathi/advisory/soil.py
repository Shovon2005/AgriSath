"""
Soil Health Assessment Engine.
Analyzes soil reaction (pH), organic matter, texture, and nutrient retention.
"""

from typing import Dict, Any, List
from agrisathi.advisory.profiles import SOIL_PROPERTIES, get_crop_profile
from agrisathi.core.schemas import canonical_soil_type


def assess_soil_health(
    farm_data: Dict[str, Any],
    crop_name: str = None,
    crop_profile: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Comprehensive agronomic soil health assessment.
    Returns status, numerical soil health score (0-100), issues list, and recommendations.
    Accepts crop_name (str) and/or crop_profile (dict or str).
    """
    if isinstance(crop_name, dict) and crop_profile is None:
        crop_profile = crop_name
        crop_name = None

    if isinstance(crop_profile, str):
        crop_name = crop_profile
        crop_profile = None

    if crop_profile is None and crop_name:
        crop_profile = get_crop_profile(crop_name)
    ph = float(farm_data.get("ph", 6.5))
    om = float(farm_data.get("organic_matter", 3.5))
    raw_oc = farm_data.get("organic_carbon") or farm_data.get("oc")
    oc = float(raw_oc) if raw_oc is not None else round(om / 1.724, 2)
    raw_ec = farm_data.get("electrical_conductivity") or farm_data.get("ec")
    ec = float(raw_ec) if raw_ec is not None else 0.6

    n = float(farm_data.get("N", 50))
    p = float(farm_data.get("P", 50))
    k = float(farm_data.get("K", 50))
    raw_soil = farm_data.get("soil_type_label") or farm_data.get("soil_type", "Loamy")
    soil_type = canonical_soil_type(raw_soil)

    issues: List[str] = []
    actions: List[str] = []
    deficiencies: List[str] = []
    excesses: List[str] = []
    score = 100

    # 1. pH Assessment
    crop_ph_outside = False
    if crop_profile:
        min_c_ph = crop_profile.get("min_ph", 5.5)
        max_c_ph = crop_profile.get("max_ph", 7.5)
        crop_ph_outside = (ph < min_c_ph or ph > max_c_ph)

    if ph < 5.0:
        issues.append("Soil is strongly acidic (pH < 5.0), inducing aluminum/iron toxicity.")
        actions.append("Apply agricultural lime (calcium carbonate) or dolomite at 1.5 - 2.5 t/ha to buffer acidity.")
        score -= 25
    elif ph < 6.0:
        issues.append("Soil is slightly acidic (pH 5.0 - 6.0).")
        actions.append("Apply composted organic manure and monitor nutrient lockup.")
        score -= 10
    elif ph > 8.5:
        issues.append("Soil is strongly alkaline/sodic (pH > 8.5), restricting micronutrient uptake.")
        actions.append("Apply agricultural gypsum (CaSO₄) or elemental sulfur with leaching to reduce sodium saturation.")
        score -= 25
    elif ph > 7.5:
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
        min_c_ph = crop_profile.get("min_ph", 5.5)
        max_c_ph = crop_profile.get("max_ph", 7.5)
        crop_title = crop_profile.get("display_name", "Target crop")
        issues.append(f"Current pH {ph} is outside ideal range ({min_c_ph} - {max_c_ph}) for {crop_title}.")
        if ph < min_c_ph:
            actions.append(f"Current pH {ph} is below optimal ({min_c_ph} - {max_c_ph}) for {crop_title}; apply agricultural lime to buffer acidity.")
        else:
            actions.append(f"Current pH {ph} exceeds optimal ({min_c_ph} - {max_c_ph}) for {crop_title}; incorporate gypsum or sulfur-based amendments.")
        score -= 10

    # 2. Electrical Conductivity (EC) / Salinity Assessment
    if ec > 4.0:
        issues.append(f"Soil is severely saline (EC: {ec:.2f} dS/m), creating strong osmotic root stress.")
        actions.append("Implement heavy leaching with low-salinity irrigation water and construct deep drainage ditches.")
        score -= 25
    elif ec > 2.0:
        issues.append(f"Soil shows moderate salinity hazard (EC: {ec:.2f} dS/m).")
        actions.append("Avoid saline well-water irrigation; select salt-tolerant crops and apply organic mulches.")
        score -= 12
    elif ec < 0.1:
        issues.append(f"Soil EC is exceptionally low ({ec:.2f} dS/m), indicating low soluble mineral salt reserves.")
        actions.append("Incorporate balanced mineral fertilizers with micro-nutrients.")
        score -= 5
    else:
        issues.append(f"Electrical Conductivity is within the optimal non-saline range ({ec:.2f} dS/m).")

    # 3. Organic Matter (OM) and Organic Carbon (OC) Assessment
    if om < 1.5 or oc < 0.5:
        issues.append("Organic matter is critically deficient (< 1.5%).")
        actions.append("Apply 10-15 t/ha well-decomposed Farm Yard Manure (FYM) or vermicompost.")
        deficiencies.append(f"Organic Matter/Carbon ({om:.1f}% OM, {oc:.2f}% OC)")
        score -= 20
    elif om < 3.0 or oc < 0.75:
        issues.append("Organic matter is below optimal levels (< 3.0%).")
        actions.append("Practice green manuring (e.g. Sesbania/Dhaincha) and retain crop residues.")
        score -= 10
    else:
        issues.append("Soil organic matter content is healthy (≥ 3.0%).")

    # 4. Macro-nutrient Baseline Check
    if n < 30:
        issues.append("Nitrogen level is relatively low (< 30 mg/kg).")
        actions.append("Apply organic compost, well-decomposed manure, or basal nitrogenous fertilizer to restore the soil nitrogen pool.")
        deficiencies.append(f"Nitrogen ({n:.1f} mg/kg)")
        score -= 10
    elif n > 140:
        issues.append(f"Nitrogen level is excessively high ({n:.1f} mg/kg); risk of vegetative lodging and delayed harvest.")
        actions.append("Avoid synthetic nitrogen top-dressing; irrigate cautiously to prevent nitrate leaching.")
        excesses.append(f"Nitrogen ({n:.1f} mg/kg)")
        score -= 5

    if p < 25:
        issues.append("Phosphorus level is relatively low (< 25 mg/kg).")
        actions.append("Incorporate rock phosphate, bone meal, or single superphosphate (SSP) to support root proliferation.")
        deficiencies.append(f"Phosphorus ({p:.1f} mg/kg)")
        score -= 10
    elif p > 100:
        issues.append(f"Phosphorus level is very high ({p:.1f} mg/kg); risk of zinc/iron micronutrient lockup.")
        actions.append("Omit phosphate applications; monitor foliage for micronutrient chlorosis.")
        excesses.append(f"Phosphorus ({p:.1f} mg/kg)")
        score -= 5

    if k < 30:
        issues.append("Potassium level is relatively low (< 30 mg/kg).")
        actions.append("Apply muriate of potash (MOP) or incorporate potassium-rich crop residues/biochar.")
        deficiencies.append(f"Potassium ({k:.1f} mg/kg)")
        score -= 10
    elif k > 140:
        issues.append(f"Potassium level is elevated ({k:.1f} mg/kg); competitive inhibition with calcium and magnesium uptake.")
        actions.append("Avoid potash applications to prevent cation antagonism with magnesium uptake.")
        excesses.append(f"Potassium ({k:.1f} mg/kg)")
        score -= 5


    # 5. Soil Texture Synergy
    texture_info = SOIL_PROPERTIES.get(soil_type, SOIL_PROPERTIES["Loamy"])

    score = max(10, min(100, score))
    if score >= 85:
        status = "Good"
    elif score >= 60:
        status = "Needs Attention"
    else:
        status = "Poor"

    # Soil Fertility Classification: "Low", "Medium", or "High"
    fertility_points = 0
    if n >= 50:
        fertility_points += 2
    elif n >= 30:
        fertility_points += 1

    if p >= 35:
        fertility_points += 2
    elif p >= 20:
        fertility_points += 1

    if k >= 45:
        fertility_points += 2
    elif k >= 25:
        fertility_points += 1

    if oc >= 0.75:
        fertility_points += 2
    elif oc >= 0.50:
        fertility_points += 1

    if 6.0 <= ph <= 7.8:
        fertility_points += 2
    elif 5.2 <= ph <= 8.5:
        fertility_points += 1

    if ec < 1.8:
        fertility_points += 1

    if fertility_points >= 9 and len(deficiencies) == 0:
        fertility_class = "High"
    elif fertility_points >= 5:
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
            "nitrogen": {"value": n, "status": "Excess" if n > 140 else ("Deficient" if n < 35 else "Optimal"), "unit": "mg/kg"},
            "phosphorus": {"value": p, "status": "Excess" if p > 100 else ("Deficient" if p < 25 else "Optimal"), "unit": "mg/kg"},
            "potassium": {"value": k, "status": "Excess" if k > 140 else ("Deficient" if k < 30 else "Optimal"), "unit": "mg/kg"},
            "ph": {"value": ph, "status": "Alkaline" if ph > 7.5 else ("Acidic" if ph < 6.0 else "Optimal"), "unit": "pH"},
            "electrical_conductivity": {"value": ec, "status": "Saline" if ec > 2.0 else "Normal", "unit": "dS/m"},
            "organic_carbon": {"value": oc, "status": "Low" if oc < 0.5 else ("High" if oc >= 0.75 else "Medium"), "unit": "%"},
        },
        "issues": issues,
        "corrective_actions": actions,
    }

