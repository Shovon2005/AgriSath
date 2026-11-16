"""
Unit tests for Weather Client and Historical Prediction Persistence (Phase 7).
Verifies weather client fallback, SQLite prediction storage, querying, and filtering.
"""

import pytest
from agrisathi.utils.weather import fetch_weather_data, geocode_location
from agrisathi.data.history import (
    save_prediction_record,
    get_recent_predictions,
    get_prediction_by_id,
    clear_history,
)


def test_weather_fallback():
    data = fetch_weather_data(location="Punjab")
    assert "temperature" in data
    assert "humidity" in data
    assert "rainfall" in data
    assert "wind_speed" in data
    assert "expected_rainfall_24h" in data
    assert data["temperature"] > 0


def test_weather_unknown_location_fallback():
    data = fetch_weather_data(location="UnknownVillageXYZ123")
    assert data["status"] in ("online", "cached_fallback")
    assert data["temperature"] == 25.0  # default baseline


def test_history_save_and_retrieve(valid_farm_payload):
    clear_history()

    dummy_prediction = {
        "recommended_crop": "rice",
        "confidence": 94.5,
    }
    dummy_advisory = {
        "soil": {"status": "Good", "fertility_class": "High", "score": 90},
        "irrigation": {"priority": "Low", "water_quantity_litres": 0},
        "fertilizer": {"recommendations": ["Apply Urea"]},
        "risks": {"risks": ["Low risk"]},
    }

    rec_id = save_prediction_record(valid_farm_payload, dummy_prediction, dummy_advisory)
    assert rec_id > 0

    recent = get_recent_predictions(limit=10)
    assert len(recent) == 1
    assert recent[0]["crop"] == "Rice"
    assert recent[0]["confidence"] == 94.5
    assert recent[0]["fertility_class"] == "High"

    # Fetch by ID
    single = get_prediction_by_id(rec_id)
    assert single is not None
    assert single["id"] == rec_id
    assert single["crop"] == "Rice"
    assert "inputs" in single
    assert single["inputs"]["N"] == 90


def test_history_filter_by_crop(valid_farm_payload):
    clear_history()

    pred_rice = {"recommended_crop": "rice", "confidence": 90.0}
    pred_maize = {"recommended_crop": "maize", "confidence": 85.0}
    advisory = {"soil": {}, "irrigation": {}, "fertilizer": {}, "risks": {}}

    save_prediction_record(valid_farm_payload, pred_rice, advisory)
    save_prediction_record(valid_farm_payload, pred_maize, advisory)

    rice_recs = get_recent_predictions(crop_filter="rice")
    assert len(rice_recs) == 1
    assert rice_recs[0]["crop"] == "Rice"

    maize_recs = get_recent_predictions(crop_filter="maize")
    assert len(maize_recs) == 1
    assert maize_recs[0]["crop"] == "Maize"


def test_api_weather_and_history(client, valid_farm_payload):
    # Test weather endpoint
    resp_w = client.get("/api/v1/weather?location=Delhi")
    assert resp_w.status_code == 200
    data_w = resp_w.get_json()
    assert "weather" in data_w
    assert "temperature" in data_w["weather"]

    # Test history endpoint
    resp_h = client.get("/api/v1/history")
    assert resp_h.status_code == 200
    data_h = resp_h.get_json()
    assert "history" in data_h


def test_history_detail_view_and_pdf(client, valid_farm_payload):
    clear_history()
    # Create record via /predict
    res_post = client.post("/predict", data=valid_farm_payload)
    assert res_post.status_code == 200

    recent = get_recent_predictions(limit=1)
    assert len(recent) == 1
    rec_id = recent[0]["id"]

    # View history detail page
    res_detail = client.get(f"/history/{rec_id}")
    assert res_detail.status_code == 200
    html = res_detail.data.decode("utf-8")
    assert f"Historical Assessment #{rec_id}" in html
    assert "Module 1: Soil Fertility" in html
    assert "Module 3: Smart Irrigation" in html
    assert "Module 4: Fertilizer Plan" in html

    # Download PDF directly via /history/<id>/pdf
    res_pdf = client.get(f"/history/{rec_id}/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.mimetype == "application/pdf"
    assert res_pdf.data.startswith(b"%PDF-")


def test_history_sqlite_closed_connections(valid_farm_payload):
    # Verify multiple writes and reads execute cleanly without file lock contention
    clear_history()
    dummy_pred = {"recommended_crop": "rice", "confidence": 91.0}
    dummy_adv = {"soil": {}, "irrigation": {}, "fertilizer": {}, "risks": {}}

    for i in range(15):
        save_prediction_record(valid_farm_payload, dummy_pred, dummy_adv)
        recs = get_recent_predictions(limit=5)
        assert len(recs) == min(i + 1, 5)
