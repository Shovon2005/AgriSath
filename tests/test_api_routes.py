"""
Automated tests for RESTful JSON API endpoints.
"""

import pytest
from agrisathi.web.app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_api_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


def test_api_crops(client):
    response = client.get("/api/v1/crops")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 22
    assert "rice" in data["crops"]


def test_api_single_crop(client):
    # Valid crop lookup
    res_ok = client.get("/api/v1/crops/rice")
    assert res_ok.status_code == 200
    data_ok = res_ok.get_json()
    assert data_ok["crop"] == "rice"
    assert data_ok["profile"]["category"] == "Cereal"

    # Non-existent crop
    res_bad = client.get("/api/v1/crops/unknown_crop_123")
    assert res_bad.status_code == 404
    data_bad = res_bad.get_json()
    assert data_bad["error"] == "Crop Not Found"


def test_api_predict_success(client, valid_farm_payload):
    response = client.post("/api/v1/predict", json=valid_farm_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "prediction" in data
    assert "advisory" in data
    assert data["prediction"]["recommended_crop"] in ("rice", "jute")
    assert len(data["prediction"]["probabilities"]) == 5
    assert len(data["prediction"]["important_features"]) == 5


def test_api_predict_missing_json(client):
    response = client.post("/api/v1/predict", data="not json", content_type="text/plain")
    assert response.status_code == 400


def test_api_predict_validation_error(client, valid_farm_payload):
    valid_farm_payload["N"] = -50  # Out of bounds
    response = client.post("/api/v1/predict", json=valid_farm_payload)
    assert response.status_code == 422
    data = response.get_json()
    assert "N" in data["details"]


def test_api_report_pdf_download(client, valid_farm_payload):
    response = client.post("/api/v1/report", json=valid_farm_payload)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert response.data.startswith(b"%PDF-")


def test_api_report_errors(client, valid_farm_payload):
    # Missing JSON body
    res_empty = client.post("/api/v1/report", data="not json", content_type="text/plain")
    assert res_empty.status_code == 400
    assert res_empty.get_json()["error"] == "Bad Request"

    # Validation error
    res_val = client.post("/api/v1/report", json={"N": -10})
    assert res_val.status_code == 422
    assert "error" in res_val.get_json()

    # Processing error (AgriSathiError)
    from unittest.mock import patch
    from agrisathi.core.exceptions import PredictionError
    with patch("agrisathi.web.routes.api.get_predictor") as mock_gp:
        mock_gp.return_value.predict.side_effect = PredictionError("Simulated inference crash")
        res_proc = client.post("/api/v1/report", json=valid_farm_payload)
        assert res_proc.status_code == 500
        data = res_proc.get_json()
        assert data["error"] == "Processing Error"
        assert "Simulated inference crash" in data["message"]


def test_api_405_handler(client):
    # GET to POST-only endpoint returns JSON 405
    response = client.get("/api/v1/predict")
    assert response.status_code == 405
    data = response.get_json()
    assert data["error"] == "Method Not Allowed"


def test_api_404_handler(client):
    response = client.get("/api/v1/nonexistent_route")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_api_rules(client):
    res = client.get("/api/v1/rules")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "soil_properties" in data["rules"]
    assert "fertilizer_conversions" in data["rules"]
    assert "soil_thresholds" in data["rules"]


def test_api_rules_reload(client):
    res = client.post("/api/v1/rules/reload")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "reloaded" in data["message"].lower()


def test_api_scenarios(client):
    res = client.get("/api/v1/scenarios")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["count"] >= 4
    assert "rice" in data["scenarios"]


def test_api_single_scenario(client):
    res_ok = client.get("/api/v1/scenarios/rice")
    assert res_ok.status_code == 200
    assert res_ok.get_json()["scenario"]["key"] == "rice"

    res_bad = client.get("/api/v1/scenarios/nonexistent_scenario")
    assert res_bad.status_code == 404


def test_api_create_scenario(client):
    from agrisathi.data.scenarios import reload_farm_scenarios
    from agrisathi.config import Config

    orig_text = Config.SCENARIOS_PATH.read_text(encoding="utf-8")
    try:
        custom_sc = {
            "key": "test_wheat",
            "title": "🌾 Test Wheat Scenario",
            "category": "Cereals",
            "parameters": {
                "N": 80, "P": 40, "K": 40, "temperature": 20.0, "humidity": 60.0,
                "ph": 6.8, "rainfall": 80.0, "soil_type": "Loamy",
            }
        }
        res = client.post("/api/v1/scenarios", json=custom_sc)
        assert res.status_code == 201
        assert res.get_json()["status"] == "success"

        # Verify retrieval
        res_get = client.get("/api/v1/scenarios/test_wheat")
        assert res_get.status_code == 200
        assert res_get.get_json()["scenario"]["title"] == "🌾 Test Wheat Scenario"
    finally:
        Config.SCENARIOS_PATH.write_text(orig_text, encoding="utf-8")
        reload_farm_scenarios()


def test_api_weather_baselines(client):
    res = client.get("/api/v1/weather/baselines")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["count"] >= 5
    assert "punjab" in data["baselines"]
    assert "bengal" in data["baselines"]


def test_api_crop_update(client):
    new_profile = {
        "display_name": "Golden Quinoa",
        "category": "Pseudocereal",
        "opt_n": 75,
        "opt_p": 35,
        "opt_k": 50,
        "min_ph": 6.0,
        "max_ph": 7.5,
        "water_demand": "Low",
    }
    from agrisathi.advisory.profiles import reset_profiles_cache
    from agrisathi.config import Config

    orig_text = Config.CROP_PROFILES_PATH.read_text(encoding="utf-8")
    try:
        res = client.post("/api/v1/crops/quinoa", json=new_profile)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["profile"]["display_name"] == "Golden Quinoa"
    finally:
        Config.CROP_PROFILES_PATH.write_text(orig_text, encoding="utf-8")
        reset_profiles_cache()

