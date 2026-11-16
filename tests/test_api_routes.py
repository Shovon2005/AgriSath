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


def test_api_report_errors(client):
    # Missing JSON body
    res_empty = client.post("/api/v1/report", data="not json", content_type="text/plain")
    assert res_empty.status_code == 400
    assert res_empty.get_json()["error"] == "Bad Request"

    # Validation error
    res_val = client.post("/api/v1/report", json={"N": -10})
    assert res_val.status_code == 422
    assert "error" in res_val.get_json()


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
