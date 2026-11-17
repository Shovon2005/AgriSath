"""
End-to-End Integrated System Verification Tests for AgriSathi.
Tests the unified decision support pipeline across all 6 core modules:
1. Soil Fertility & Health Assessment (with EC, OC, Fertility Class, Suggestions)
2. Crop Recommendation & Top-3 Suitability Comparison Matrix
3. Smart Irrigation (ETc, Water Volume in Litres/m3, Timing, Rain Suppression)
4. AI Fertilizer Prescription (kg/ha, 50kg bags, DAP/SSP, Organics, 3-split schedule)
5. Explainable AI (SHAP Waterfall, Contributions, Narrative, What-If Simulator)
6. Integrated Dashboard, Weather API, SQLite History, and PDF Report Export
"""

import pytest
from agrisathi.core.validator import validate_farm_input
from agrisathi.ml.predictor import get_predictor
from agrisathi.advisory.engine import generate_full_advisory, run_full_pipeline
from agrisathi.reports.pdf_generator import generate_pdf_advisory_report
from agrisathi.data.history import get_recent_predictions
from agrisathi.advisory.irrigation import calculate_irrigation_advisory
from agrisathi.advisory.fertilizer import calculate_fertilizer_guidance


def test_full_pipeline_web_predict_flow(client, valid_farm_payload):
    """Verify that posting farm inputs to /predict renders complete multi-module dashboard."""
    payload = dict(valid_farm_payload)
    payload.update({
        "electrical_conductivity": "0.65",
        "organic_carbon": "0.75",
        "farm_area": "2.5",
        "farm_area_unit": "hectare",
        "location": "Ludhiana, Punjab",
        "season": "Kharif",
        "expected_rainfall_24h": "5.0",
    })

    response = client.post("/predict", data=payload, follow_redirects=True)
    assert response.status_code == 200
    html = response.data.decode("utf-8")

    # Module 1: Soil Fertility & Health
    assert "Soil Assessment" in html or "SOIL FERTILITY" in html
    assert "Fertility" in html
    assert any(fc in html for fc in ["Low", "Medium", "High"])
    assert "0.65 dS/m" in html or "Electrical Conductivity" in html
    assert "0.75 %" in html or "Organic Carbon" in html

    # Module 2: Crop Recommendation & Top-3 Comparison
    assert "AI Recommendation" in html
    assert "Top-3 Crop Recommendations & Suitability Comparison" in html
    assert "Yield Potential" in html or "Suitability Score" in html

    # Module 3: Smart Irrigation
    assert "Smart Irrigation" in html or "IRRIGATION NEED" in html
    assert "WATER VOLUME" in html or "Water Volume" in html
    assert "Litres" in html or " L" in html

    # Module 4: Fertilizer Prescription & Organics
    assert "Fertilizer Recommendation" in html or "Fertilizer" in html
    assert "Urea" in html
    assert "bags" in html
    assert "Organic Alternatives:" in html or "Organic" in html
    assert "Application Split Schedule:" in html

    # Module 5: Explainable AI
    assert "Explainable AI (SHAP Waterfall)" in html or "Why Was This Crop Recommended" in html
    assert "svg" in html
    assert "What-If Scenario Simulator" in html or "whatif" in html.lower()

    # Persistence verification
    recent = get_recent_predictions(limit=5)
    assert len(recent) > 0
    latest = recent[0]
    assert latest["location"] == "Ludhiana, Punjab"
    assert latest["farm_area"] == 2.5


def test_whatif_api_simulation_flow(client, valid_farm_payload):
    """Verify that /api/v1/what-if correctly computes simulated crop and probability shifts."""
    baseline = dict(valid_farm_payload)
    adjustments = {
        "rainfall": 280.0,  # High rain shift towards rice
        "N": 120.0,
    }

    res = client.post(
        "/api/v1/what-if",
        json={"baseline": baseline, "adjustments": adjustments},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    sim = data["simulation"]
    assert "simulated_crop" in sim
    assert "simulated_confidence" in sim
    assert "probability_shifts" in sim
    assert isinstance(sim["probability_shifts"], list)
    assert len(sim["probability_shifts"]) > 0


def test_weather_api_geocoding_and_data(client):
    """Verify that /api/v1/weather responds with temperature, humidity, and rainfall."""
    res = client.get("/api/v1/weather?location=Kolkata")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    w = data["weather"]
    assert "temperature" in w
    assert "humidity" in w
    assert "rainfall" in w
    assert isinstance(w["temperature"], (int, float))


def test_history_pages_flow(client, valid_farm_payload):
    """Verify that historical records can be listed and retrieved individually."""
    # Ensure at least one record exists
    payload = dict(valid_farm_payload)
    payload["location"] = "Amritsar, Punjab"
    client.post("/predict", data=payload)

    # List view
    res = client.get("/history")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "Historical Advisory Reports" in html or "Predictions Archive" in html

    # API view
    res_api = client.get("/api/v1/history")
    assert res_api.status_code == 200
    data = res_api.get_json()
    assert data["status"] == "success"
    assert isinstance(data["history"], list)

    if data["history"]:
        first_id = data["history"][0]["id"]
        detail_res = client.get(f"/history/{first_id}")
        assert detail_res.status_code == 200
        detail_html = detail_res.data.decode("utf-8")
        assert f"Historical Assessment #{first_id}" in detail_html
        assert "Module 1: Soil Fertility" in detail_html


def test_pdf_report_export_complete_data(valid_farm_payload):
    """Verify that PDF generation produces a valid, rich PDF byte stream with all modules."""
    farm_data = dict(valid_farm_payload)
    farm_data.update({
        "electrical_conductivity": 0.8,
        "organic_carbon": 0.9,
        "farm_area": 3.0,
        "farm_area_unit": "hectare",
        "location": "Bardhaman, West Bengal",
        "season": "Kharif",
        "expected_rainfall_24h": 0.0,
    })
    sanitized = validate_farm_input(farm_data)
    predictor = get_predictor()
    pred = predictor.predict(sanitized)
    pred["input_data"] = sanitized

    advisory = generate_full_advisory(
        sanitized,
        pred["recommended_crop"],
        top_crops=pred.get("top_three"),
    )

    pdf_bytes = generate_pdf_advisory_report(
        pred,
        advisory,
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 5000
    assert pdf_bytes.startswith(b"%PDF-")


def test_irrigation_rainfall_suppression_logic():
    """Verify that forecasted rainfall suppresses or reduces irrigation urgency."""
    dry_payload = {
        "crop_name": "rice",
        "soil_type": "Loamy",
        "temperature": 28.0,
        "humidity": 65.0,
        "rainfall": 10.0,
        "soil_moisture": 14.0,  # Dry soil: priority High
        "growth_stage": "Vegetative",
        "farm_area_ha": 2.0,
        "expected_rainfall_24h": 25.0,  # 25 mm forecast suppresses irrigation
    }
    presc_rain = calculate_irrigation_advisory(dry_payload, "rice")

    assert presc_rain["rainfall_suppressed"] is True
    assert presc_rain["expected_rainfall_24h"] == 25.0
    assert "rain" in presc_rain["irrigation_required"].lower()


def test_fertilizer_farm_area_scaling():
    """Verify that fertilizer quantities scale proportionally with farm area."""
    payload_1ha = {
        "N": 40.0,
        "P": 20.0,
        "K": 20.0,
        "ph": 6.5,
        "farm_area_ha": 1.0,
    }
    payload_2ha = {
        "N": 40.0,
        "P": 20.0,
        "K": 20.0,
        "ph": 6.5,
        "farm_area_ha": 2.0,
    }

    p1 = calculate_fertilizer_guidance(payload_1ha, "rice")
    p2 = calculate_fertilizer_guidance(payload_2ha, "rice")

    urea_1 = p1["total_farm_requirements"]["urea_kg"]
    urea_2 = p2["total_farm_requirements"]["urea_kg"]
    assert pytest.approx(urea_2, rel=0.01) == urea_1 * 2
    assert p2["total_farm_requirements"]["urea_bags_50kg"] >= p1["total_farm_requirements"]["urea_bags_50kg"]
    assert "vermicompost_tonnes" in p1["organic_alternatives"]
    assert "compost_fym_tonnes" in p1["organic_alternatives"]


def test_run_full_pipeline_orchestration(valid_farm_payload):
    """Verify that run_full_pipeline returns sanitized inputs, prediction, and full advisory in one call."""
    sanitized, prediction, advisory = run_full_pipeline(valid_farm_payload)
    assert sanitized["N"] == valid_farm_payload["N"]
    assert "recommended_crop" in prediction
    assert "confidence" in prediction
    assert advisory["crop_name"] == prediction["recommended_crop"]
    assert "soil" in advisory
    assert "fertilizer" in advisory
    assert "irrigation" in advisory
    assert "risks" in advisory
