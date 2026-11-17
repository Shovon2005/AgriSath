"""
Unit tests for crop agronomic profiles.
"""

from agrisathi.advisory.profiles import (
    get_crop_profiles,
    get_crop_profile,
    SOIL_PROPERTIES,
    FERTILIZER_CONVERSIONS,
)


EXPECTED_CROPS = [
    "rice", "maize", "chickpea", "kidneybeans", "pigeonpeas", "mothbeans",
    "mungbean", "blackgram", "lentil", "pomegranate", "banana", "mango",
    "grapes", "watermelon", "muskmelon", "apple", "orange", "papaya",
    "coconut", "cotton", "jute", "coffee"
]


def test_all_22_crops_present():
    profiles = get_crop_profiles()
    assert len(profiles) == 22
    for crop in EXPECTED_CROPS:
        assert crop in profiles, f"Crop {crop} missing from profiles"
        data = profiles[crop]
        assert "display_name" in data
        assert "opt_n" in data and data["opt_n"] > 0
        assert "opt_p" in data and data["opt_p"] > 0
        assert "opt_k" in data and data["opt_k"] > 0
        assert "min_ph" in data and "max_ph" in data
        assert data["min_ph"] <= data["max_ph"]
        assert data["water_demand"] in ("Low", "Medium", "High")


def test_get_single_crop_profile():
    rice = get_crop_profile("Rice")
    assert rice["category"] == "Cereal"
    assert rice["water_demand"] == "High"


def test_get_fallback_profile():
    unknown = get_crop_profile("unknown_exotic_crop")
    assert unknown["opt_n"] == 80
    assert unknown["display_name"] == "Unknown_Exotic_Crop"


def test_soil_properties_definitions():
    for soil in ["Clay", "Loamy", "Sandy"]:
        assert soil in SOIL_PROPERTIES
        assert "water_retention" in SOIL_PROPERTIES[soil]


def test_fertilizer_conversions():
    assert FERTILIZER_CONVERSIONS["urea_n_fraction"] == 0.46
    assert FERTILIZER_CONVERSIONS["dap_p_fraction"] == 0.46
    assert FERTILIZER_CONVERSIONS["mop_k_fraction"] == 0.60


def test_dynamic_rules_loading():
    from agrisathi.advisory.profiles import (
        get_agronomic_rules,
        get_soil_thresholds,
        get_irrigation_rules,
        get_organic_guidelines,
    )
    rules = get_agronomic_rules()
    assert "soil_properties" in rules
    assert "fertilizer_conversions" in rules

    thresholds = get_soil_thresholds()
    assert "ph" in thresholds
    assert "nitrogen" in thresholds

    irrig = get_irrigation_rules()
    assert "critical_moisture" in irrig
    assert irrig["critical_moisture"] == 12.0

    org = get_organic_guidelines()
    assert "fym" in org
    assert "vermicompost" in org

