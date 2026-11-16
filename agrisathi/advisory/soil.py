"""
Soil Health Assessment Engine.
Analyzes soil reaction (pH), organic matter, texture, and nutrient retention.
"""

from typing import Dict, Any, List
from agrisathi.advisory.profiles import SOIL_PROPERTIES
from agrisathi.core.schemas import canonical_soil_type


def assess_soil_health(
    farm_data: Dict[str, Any],
    crop_profile: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Comprehensive agronomic soil health assessment.
    Returns status, numerical soil health score (0-100), issues list, and recommendations.
    """
    ph = float(farm_data.get("ph", 6.5))
    om = float(farm_data.get("organic_matter", 3.5))
    n = float(farm_data.get("N", 50))
    p = float(farm_data.get("P", 50))
    k = float(farm_data.get("K", 50))
    raw_soil = farm_data.get("soil_type_label") or farm_data.get("soil_type", "Loamy")
    soil_type = canonical_soil_type(raw_soil)

    issues: List[str] = []
    actions: List[str] = []
    score = 100

    # 1. pH Assessment
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
        issues.append("Soil pH is within the optimal agronomic range (6.0 - 7.5).")

    # Crop-specific pH tolerance
    if crop_profile:
        min_c_ph = crop_profile.get("min_ph", 5.5)
        max_c_ph = crop_profile.get("max_ph", 7.5)
        if ph < min_c_ph or ph > max_c_ph:
            crop_name = crop_profile.get("display_name", "Target crop")
            issues.append(f"Current pH {ph} is outside ideal range ({min_c_ph} - {max_c_ph}) for {crop_name}.")
            score -= 10

    # 2. Organic Matter (OM) Assessment
    if om < 1.5:
        issues.append("Organic matter is critically deficient (< 1.5%).")
        actions.append("Apply 10-15 t/ha well-decomposed Farm Yard Manure (FYM) or vermicompost.")
        score -= 20
    elif om < 3.0:
        issues.append("Organic matter is below optimal levels (< 3.0%).")
        actions.append("Practice green manuring (e.g. Sesbania/Dhaincha) and retain crop residues.")
        score -= 10
    else:
        issues.append("Soil organic matter content is healthy (≥ 3.0%).")

    # 3. Macro-nutrient Baseline Check
    if n < 30:
        issues.append("Nitrogen level is relatively low (< 30 mg/kg).")
        score -= 10
    if p < 25:
        issues.append("Phosphorus level is relatively low (< 25 mg/kg).")
        score -= 10
    if k < 30:
        issues.append("Potassium level is relatively low (< 30 mg/kg).")
        score -= 10

    # 4. Soil Texture Synergy
    texture_info = SOIL_PROPERTIES.get(soil_type, SOIL_PROPERTIES["Loamy"])

    score = max(10, min(100, score))
    if score >= 85:
        status = "Good"
    elif score >= 60:
        status = "Needs Attention"
    else:
        status = "Poor"

    return {
        "status": status,
        "score": score,
        "ph": ph,
        "organic_matter": om,
        "soil_texture": soil_type,
        "texture_characteristics": texture_info,
        "issues": issues,
        "corrective_actions": actions,
    }
