"""
Crop Suitability Comparison Engine (Module 2).
Generates multi-attribute comparison matrix and ranking evaluations for top recommended crops.
"""

from typing import Dict, Any, List
from agrisathi.advisory.profiles import get_crop_profile
from agrisathi.core.schemas import canonical_soil_type, canonical_season


def build_crop_comparison_matrix(
    top_crops: List[Dict[str, Any]],
    farm_data: Dict[str, Any],
    limit: int = 3,
) -> Dict[str, Any]:
    """
    Builds a structured side-by-side suitability comparison matrix for the top-N recommended crops.
    Evaluates season fit, soil texture affinity, water demand, pH tolerance, and thermal regime.
    Guaranteed null-safe with consistent schema even on empty inputs.
    """
    selected_crops = top_crops[:limit] if top_crops else []
    if not selected_crops:
        return {
            "items": [],
            "comparison_rows": [],
            "summary": "No crop predictions available for comparison.",
            "primary_crop": "",
            "top_three": [],
        }

    farm_soil = canonical_soil_type(farm_data.get("soil_type_label") or farm_data.get("soil_type", "Loamy"))
    farm_season = canonical_season(farm_data.get("season", "Whole Year"))
    farm_ph = float(farm_data.get("ph", 6.5))
    farm_rainfall = float(farm_data.get("rainfall", 100.0))
    farm_temp = float(farm_data.get("temperature", 25.0))

    matrix_rows: List[Dict[str, Any]] = []

    for rank, item in enumerate(selected_crops, start=1):
        crop_id = str(item.get("crop", "")).lower()
        pct = item.get("percentage")
        if pct is not None:
            confidence = float(pct)
        else:
            confidence = float(item.get("probability", 0.0)) * 100.0

        profile = get_crop_profile(crop_id)

        # 1. Season Fit
        crop_season = profile.get("season", "Whole Year")
        if farm_season == "Whole Year" or farm_season in crop_season or "Whole Year" in crop_season:
            season_fit = "Optimal"
        else:
            season_fit = f"Requires {crop_season}"

        # 2. Soil Texture Fit
        ideal_soils = profile.get("ideal_soil", ["Loamy"])
        soil_fit = "Optimal" if farm_soil in ideal_soils else "Moderate"

        # 3. pH Fit
        min_ph = float(profile.get("min_ph", 5.5))
        max_ph = float(profile.get("max_ph", 7.5))
        if min_ph <= farm_ph <= max_ph:
            ph_fit = f"Optimal ({min_ph} - {max_ph})"
        else:
            ph_fit = f"Suboptimal (Needs {min_ph} - {max_ph})"

        # 4. Thermal Regime
        min_temp = float(profile.get("min_temp", 15.0))
        max_temp = float(profile.get("max_temp", 35.0))
        temp_fit = "Suitable" if (min_temp <= farm_temp <= max_temp) else "Marginal"

        # 5. Key Advantage Narrative
        if rank == 1:
            key_advantage = f"Highest probability match ({confidence:.1f}%) aligning with prevailing rainfall ({farm_rainfall:.0f} mm) and thermal conditions."
        elif "water_demand" in profile and profile["water_demand"] == "Low" and farm_rainfall < 80.0:
            key_advantage = "Strong drought-resilient alternative with lower water requirement."
        else:
            key_advantage = f"Viable secondary alternative offering strong agronomic viability ({confidence:.1f}% confidence)."

        matrix_rows.append({
            "rank": rank,
            "crop": crop_id.title(),
            "crop_id": crop_id,
            "display_name": profile.get("display_name", crop_id.title()),
            "category": profile.get("category", "General"),
            "confidence": round(confidence, 1),
            "season": crop_season,
            "season_fit": season_fit,
            "water_demand": profile.get("water_demand", "Medium"),
            "soil_fit": soil_fit,
            "ideal_soils": ", ".join(ideal_soils),
            "ph_range": f"{min_ph} - {max_ph}",
            "ph_fit": ph_fit,
            "thermal_fit": temp_fit,
            "temp_range": f"{min_temp:.0f} - {max_temp:.0f}°C",
            "growth_duration": profile.get("duration_days", "90-120 days"),
            "yield_potential": profile.get("yield_potential", "2.0 - 4.0 t/ha"),
            "key_advantage": key_advantage,
        })

    # Comparative synthesis narrative
    first = matrix_rows[0]
    summary_parts = [
        f"Primary recommendation is {first['crop']} with {first['confidence']}% AI confidence."
    ]
    if len(matrix_rows) > 1:
        second = matrix_rows[1]
        summary_parts.append(
            f"If market demand or water constraints shift, {second['crop']} ({second['confidence']}%) represents the leading alternative with {second['water_demand'].lower()} water demand."
        )

    return {
        "items": matrix_rows,
        "comparison_rows": matrix_rows,
        "summary": " ".join(summary_parts),
        "primary_crop": matrix_rows[0]["crop"] if matrix_rows else "",
        "top_three": [row["crop"] for row in matrix_rows[:3]],
    }
