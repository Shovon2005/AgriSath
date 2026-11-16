"""
Unit tests for Explainable AI (Module 5): SHAP Waterfall plot and What-If analysis.
Verifies waterfall step calculations, natural language synthesis, and interactive simulation.
"""

from agrisathi.ml.predictor import get_predictor
from agrisathi.ml.explain import synthesize_explanation_narrative
from agrisathi.ml.whatif import simulate_what_if


def test_shap_waterfall_generation(valid_farm_payload):
    predictor = get_predictor()
    prediction = predictor.predict(valid_farm_payload)

    assert "waterfall" in prediction
    wf = prediction["waterfall"]
    assert "base_value" in wf
    assert "final_value" in wf
    assert "steps" in wf
    assert len(wf["steps"]) > 0
    assert "natural_language_explanation" in wf
    assert len(wf["natural_language_explanation"]) > 20
    assert "svg_plot" in wf
    assert "<svg" in wf["svg_plot"]


def test_explanation_narrative_synthesis():
    contributions = [
        {"feature": "Rainfall (mm)", "direction": "positive", "shap_value": 0.25},
        {"feature": "Nitrogen", "direction": "positive", "shap_value": 0.18},
        {"feature": "Temperature (°C)", "direction": "negative", "shap_value": -0.05},
    ]
    farm_data = {"rainfall": 202.0, "temperature": 21.0}
    narrative = synthesize_explanation_narrative("rice", 92.5, contributions, farm_data)

    assert "Rice" in narrative
    assert "92.5%" in narrative
    assert "Rainfall (mm)" in narrative
    assert "202 mm" in narrative


def test_what_if_simulation(valid_farm_payload):
    baseline = valid_farm_payload.copy()
    baseline["rainfall"] = 40.0
    baseline["N"] = 30.0

    # Simulate massive increase in rainfall and nitrogen
    modifications = {"rainfall": 250.0, "N": 100.0}

    result = simulate_what_if(baseline, modifications)

    assert "baseline_crop" in result
    assert "simulated_crop" in result
    assert "probability_shifts" in result
    assert len(result["changes_applied"]) == 2
    assert "insight_summary" in result
    assert len(result["insight_summary"]) > 10


def test_what_if_api_endpoint(client, valid_farm_payload):
    response = client.post(
        "/api/v1/what-if",
        json={
            "baseline": valid_farm_payload,
            "adjustments": {"rainfall": 250.0, "temperature": 28.0},
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "simulation" in data
    assert "probability_shifts" in data["simulation"]


def test_what_if_categorical_adjustment(valid_farm_payload):
    """Verify that changing categorical variables in what-if correctly updates prediction."""
    baseline = valid_farm_payload.copy()
    baseline["soil_type"] = 1  # Clay
    baseline["soil_type_label"] = "Clay"

    result = simulate_what_if(baseline, {"soil_type": "Sandy"})
    assert len(result["changes_applied"]) == 1
    assert result["changes_applied"][0]["field"] == "soil_type"
    assert result["changes_applied"][0]["new_value"] == "Sandy"

