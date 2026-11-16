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
