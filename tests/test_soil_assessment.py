"""
Unit tests for Enhanced Soil Assessment Engine (Module 1).
Verifies fertility classification (Low, Medium, High), EC salinity checks,
OC organic carbon evaluations, deficiency/excess diagnosis, and improvement suggestions.
"""

from agrisathi.advisory.soil import assess_soil_health


def test_soil_fertility_high():
    farm_data = {
        "N": 90.0,
        "P": 50.0,
        "K": 60.0,
        "ph": 6.8,
        "organic_matter": 4.0,
        "organic_carbon": 1.2,
        "electrical_conductivity": 0.5,
        "soil_type": "Loamy",
    }
    result = assess_soil_health(farm_data, "rice")
    assert result["fertility_class"] in ("High", "Medium")
    assert result["score"] >= 80
    assert result["electrical_conductivity"] == 0.5
    assert result["organic_carbon"] == 1.2
    assert "nutrients_analysis" in result
    assert result["nutrients_analysis"]["nitrogen"]["status"] == "Optimal"


def test_soil_fertility_low_and_deficiencies():
    farm_data = {
        "N": 15.0,
        "P": 10.0,
        "K": 12.0,
        "ph": 4.5,
        "organic_matter": 0.8,
        "organic_carbon": 0.3,
        "electrical_conductivity": 0.4,
        "soil_type": "Sandy",
    }
    result = assess_soil_health(farm_data, "rice")
    assert result["fertility_class"] == "Low"
    assert result["status"] == "Poor"
    assert len(result["deficiencies"]) >= 3
    assert any("Nitrogen" in d for d in result["deficiencies"])
    assert any("Phosphorus" in d for d in result["deficiencies"])
    assert any("lime" in a.lower() for a in result["corrective_actions"])


def test_soil_salinity_hazard():
    farm_data = {
        "N": 70.0,
        "P": 40.0,
        "K": 50.0,
        "ph": 7.8,
        "organic_matter": 2.5,
        "organic_carbon": 0.7,
        "electrical_conductivity": 4.8,  # Strongly saline
        "soil_type": "Clay",
    }
    result = assess_soil_health(farm_data, "rice")
    assert any("saline" in issue.lower() for issue in result["issues"])
    assert any("leaching" in action.lower() for action in result["corrective_actions"])
    assert result["nutrients_analysis"]["electrical_conductivity"]["status"] == "Saline"


def test_soil_nutrient_excesses():
    farm_data = {
        "N": 180.0,
        "P": 120.0,
        "K": 160.0,
        "ph": 7.0,
        "organic_matter": 3.0,
        "electrical_conductivity": 0.8,
        "soil_type": "Loamy",
    }
    result = assess_soil_health(farm_data, "rice")
    assert len(result["excesses"]) >= 2
    assert any("Nitrogen" in ex for ex in result["excesses"])
    assert any("lodging" in issue.lower() for issue in result["issues"])


def test_soil_zero_values_preserved():
    """Verify that 0.0 values for OC and EC are preserved and not overridden by defaults."""
    farm_data = {
        "N": 50.0,
        "P": 40.0,
        "K": 40.0,
        "ph": 6.5,
        "organic_matter": 2.0,
        "organic_carbon": 0.0,
        "electrical_conductivity": 0.0,
        "soil_type": "Loamy",
    }
    result = assess_soil_health(farm_data, "rice")
    assert result["organic_carbon"] == 0.0
    assert result["electrical_conductivity"] == 0.0


def test_soil_deficiency_and_status_consistency():
    """Verify consistency between deficiencies list and nutrients_analysis table status."""
    farm_data = {
        "N": 28.0,
        "P": 20.0,
        "K": 25.0,
        "ph": 6.5,
        "organic_matter": 3.0,
        "soil_type": "Loamy",
    }
    result = assess_soil_health(farm_data, "rice")
    # Both list and status dict must agree that N, P, K are Deficient
    assert any("Nitrogen" in d for d in result["deficiencies"])
    assert result["nutrients_analysis"]["nitrogen"]["status"] == "Deficient"
    assert any("Phosphorus" in d for d in result["deficiencies"])
    assert result["nutrients_analysis"]["phosphorus"]["status"] == "Deficient"
    assert any("Potassium" in d for d in result["deficiencies"])
    assert result["nutrients_analysis"]["potassium"]["status"] == "Deficient"


def test_soil_salinity_fertility_capped():
    """Verify that severe salinity (EC > 4.0) forces fertility class to Low."""
    farm_data = {
        "N": 90.0,
        "P": 50.0,
        "K": 60.0,
        "ph": 6.8,
        "organic_matter": 4.0,
        "organic_carbon": 1.2,
        "electrical_conductivity": 5.5,  # Severe salinity
        "soil_type": "Clay",
    }
    result = assess_soil_health(farm_data, "rice")
    assert result["fertility_class"] == "Low"

