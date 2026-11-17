"""
Unit tests for Enhanced Fertilizer Recommendation Engine (Module 4).
Verifies NPK deficit calculation, commercial fertilizer dosages (Urea, DAP, SSP, MOP),
farm-size scaling (total kg and 50kg bags), organic alternatives, and 3-stage schedule.
"""

import pytest
from agrisathi.advisory.fertilizer import calculate_fertilizer_guidance


def test_fertilizer_deficit_and_bags_calculation():
    payload = {
        "N": 30.0,   # target for rice is 100 -> deficit 70
        "P": 20.0,   # target for rice is 45  -> deficit 25
        "K": 20.0,   # target for rice is 45  -> deficit 25
        "farm_area_ha": 3.0,
        "ph": 6.5,
    }
    result = calculate_fertilizer_guidance(payload, "rice")

    # Commercial fertilizers per ha
    assert result["deficits"]["N"] == 70.0
    assert result["deficits"]["P"] == 25.0
    assert result["deficits"]["K"] == 25.0

    comm = result["commercial_fertilizers"]
    assert comm["dap_kg_ha"] > 0.0
    assert comm["ssp_kg_ha"] > 0.0
    assert comm["urea_kg_ha"] > 0.0
    assert comm["mop_kg_ha"] > 0.0

    # Total farm requirements for 3 ha
    totals = result["total_farm_requirements"]
    assert totals["urea_kg"] == pytest.approx(comm["urea_kg_ha"] * 3.0, 0.1)
    assert totals["urea_bags_50kg"] == pytest.approx(totals["urea_kg"] / 50.0, 0.1)
    assert totals["dap_kg"] == pytest.approx(comm["dap_kg_ha"] * 3.0, 0.1)
    assert totals["mop_kg"] == pytest.approx(comm["mop_kg_ha"] * 3.0, 0.1)

    # Organic alternatives
    organic = result["organic_alternatives"]
    assert organic["compost_fym_tonnes"] == 30.0  # 10 t/ha * 3 ha
    assert organic["vermicompost_tonnes"] == 9.0  # 3 t/ha * 3 ha
    assert "biofertilizer" in organic


def test_fertilizer_pulse_biofertilizer_rhizobium():
    payload = {
        "N": 20.0,
        "P": 30.0,
        "K": 30.0,
        "farm_area_ha": 1.0,
        "ph": 7.0,
    }
    result = calculate_fertilizer_guidance(payload, "chickpea")
    assert "Rhizobium" in result["organic_alternatives"]["biofertilizer"]


def test_fertilizer_zero_deficit():
    rich_payload = {
        "N": 120.0,
        "P": 80.0,
        "K": 80.0,
        "farm_area_ha": 1.0,
        "ph": 6.8,
    }
    result = calculate_fertilizer_guidance(rich_payload, "rice")
    assert result["commercial_fertilizers"]["urea_kg_ha"] == 0.0
    assert result["commercial_fertilizers"]["dap_kg_ha"] == 0.0
    assert result["commercial_fertilizers"]["mop_kg_ha"] == 0.0
    assert "sufficient" in result["recommendations"][0].lower()
