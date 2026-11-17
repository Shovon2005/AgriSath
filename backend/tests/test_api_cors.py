"""
Unit tests for CORS headers and Headless Next.js API integration.
Verifies preflight OPTIONS handling and Cross-Origin response headers across endpoints.
"""

def test_cors_options_preflight(client):
    """Verify that OPTIONS requests return correct preflight CORS headers."""
    resp = client.open(
        "/api/v1/predict",
        method="OPTIONS",
        headers={"Origin": "http://localhost:3000"}
    )
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") in ("http://localhost:3000", "*")
    assert "POST" in resp.headers.get("Access-Control-Allow-Methods", "")
    assert "Content-Type" in resp.headers.get("Access-Control-Allow-Headers", "")


def test_cors_get_endpoint_headers(client):
    """Verify that GET endpoints return Access-Control-Allow-Origin."""
    resp = client.get(
        "/api/v1/health",
        headers={"Origin": "http://localhost:3000"}
    )
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") in ("http://localhost:3000", "*")


def test_cors_predict_response_includes_sanitized_inputs(client, valid_farm_payload):
    """Verify that /api/v1/predict returns sanitized_inputs for frontend display."""
    resp = client.post(
        "/api/v1/predict",
        json=valid_farm_payload,
        headers={"Origin": "http://localhost:3000"}
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "sanitized_inputs" in data
    assert data["sanitized_inputs"]["N"] == 90
    assert resp.headers.get("Access-Control-Allow-Origin") in ("http://localhost:3000", "*")
