"""
Unit tests for PDF advisory report generator.
"""

from agrisathi.core.validator import validate_farm_input
from agrisathi.ml.predictor import get_predictor
from agrisathi.advisory.engine import generate_full_advisory
from agrisathi.reports.pdf_generator import generate_pdf_advisory_report


def test_generate_pdf_report(valid_farm_payload):
    sanitized = validate_farm_input(valid_farm_payload)
    predictor = get_predictor()
    prediction = predictor.predict(sanitized)
    advisory = generate_full_advisory(sanitized, prediction["recommended_crop"])

    pdf_bytes = generate_pdf_advisory_report(prediction, advisory)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # PDF magic byte signature
    assert pdf_bytes.startswith(b"%PDF-")


def test_generate_pdf_with_dataframes():
    import pandas as pd
    prediction = {
        "recommended_crop": "rice",
        "confidence": 92.5,
        "probabilities": pd.DataFrame([{"crop": "rice", "percentage": 92.5}]),
        "important_features": pd.DataFrame([
            {"feature": "Rainfall", "impact_percentage": 25.0, "direction": "positive"}
        ]),
    }
    advisory = {
        "soil": {"status": "Good", "issues": ["Healthy"]},
        "fertilizer": {"recommendations": ["Sufficient"]},
        "irrigation": {"priority": "Low", "message": "Optimal"},
        "risks": {"risks": ["Low risk"]},
        "crop_profile": {"display_name": "Rice (Oryza sativa)"},
    }
    pdf_bytes = generate_pdf_advisory_report(prediction, advisory)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
