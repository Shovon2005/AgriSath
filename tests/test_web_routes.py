"""
Automated tests for Flask Web UI routes.
"""

import pytest
from agrisathi.web.app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"AgriSathi" in response.data
    assert b"Enter Farm Parameters" in response.data


def test_home_page_demo_preset(client):
    response = client.get("/?demo=rice")
    assert response.status_code == 200
    # Should contain pre-filled value for rice N (90)
    assert b'value="90"' in response.data or b'value="90.0"' in response.data


def test_predict_form_submission(client, valid_farm_payload):
    response = client.post("/predict", data=valid_farm_payload)
    assert response.status_code == 200
    assert b"AI Recommendation" in response.data
    assert b"Soil Assessment" in response.data
    assert b"Smart Irrigation" in response.data
    assert b"Download Official PDF Report" in response.data
    # Verify branding and confidence display
    assert b"AgriSathi" in response.data
    assert b"AgriAI" not in response.data
    assert b"% Match" in response.data
    assert b"Soil Type" in response.data
    assert b"Soil Type Label" not in response.data


def test_download_report_form_submission(client, valid_farm_payload):
    response = client.post("/download-report", data=valid_farm_payload)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert response.data.startswith(b"%PDF-")


def test_predict_validation_failure(client, valid_farm_payload):
    valid_farm_payload["ph"] = 25.0  # Invalid pH
    response = client.post("/predict", data=valid_farm_payload)
    assert response.status_code == 422
    assert b"Input Validation Notice" in response.data


def test_download_report_validation_failure(client, valid_farm_payload):
    valid_farm_payload["ph"] = 25.0  # Invalid pH
    response = client.post("/download-report", data=valid_farm_payload)
    assert response.status_code == 422
    assert b"Input Validation Notice" in response.data
