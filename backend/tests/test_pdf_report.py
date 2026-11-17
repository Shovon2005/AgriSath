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


def test_generate_pdf_with_nulls_and_empty_payloads():
    # Completely empty dicts
    pdf_empty = generate_pdf_advisory_report({}, {})
    assert isinstance(pdf_empty, bytes)
    assert pdf_empty.startswith(b"%PDF-")

    # Dicts populated with None
    null_pred = {
        "recommended_crop": None,
        "confidence": None,
        "probabilities": None,
        "important_features": None,
    }
    null_adv = {
        "soil": {"issues": None, "score": None, "status": None},
        "fertilizer": {"recommendations": None, "commercial_fertilizers": None},
        "irrigation": {"recommended_actions": None},
        "risks": {"risks": None},
        "crop_profile": None,
    }
    pdf_nulls = generate_pdf_advisory_report(null_pred, null_adv)
    assert isinstance(pdf_nulls, bytes)
    assert pdf_nulls.startswith(b"%PDF-")


def test_generate_pdf_single_page_layout(valid_farm_payload):
    import re
    sanitized = validate_farm_input(valid_farm_payload)
    predictor = get_predictor()
    prediction = predictor.predict(sanitized)
    advisory = generate_full_advisory(sanitized, prediction["recommended_crop"])

    pdf_bytes = generate_pdf_advisory_report(prediction, advisory)
    pages = len(re.findall(rb'/Type\s*/Page\b', pdf_bytes))
    assert pages == 1


def test_generate_pdf_xml_escaping():
    """Ensure unescaped XML/HTML entities like unclosed tags, <, >, & don't crash ReportLab."""
    malformed_pred = {
        "recommended_crop": "rice <br> & wheat",
        "confidence": 85.5,
        "probabilities": [
            {"crop": "rice <b unclosed", "percentage": 85.5},
            {"crop": "wheat > bar", "percentage": 14.5},
        ],
        "important_features": [
            {"feature": "Soil pH < 5.0", "impact_percentage": "30%", "direction": "positive & high"},
            {"feature": "P & K > 100", "impact_percentage": 20.0, "direction": "negative"},
        ],
    }
    malformed_adv = {
        "soil": {
            "status": "Poor & Acidic",
            "soil_texture": "Loamy <bad>",
            "issues": [
                "Soil is strongly acidic (pH < 5.0) & toxic",
                "Organic matter < 1.0% <b>unclosed tag",
            ],
            "score": 45,
            "ph": 4.2,
            "organic_matter": 0.8,
        },
        "fertilizer": {
            "recommendations": [
                "Nitrogen deficit < 20 kg/ha & urgent",
                "Apply Urea > 50 kg/ha <i>unclosed",
            ],
            "commercial_fertilizers": {"urea_kg_ha": 65.2, "dap_kg_ha": 0, "mop_kg_ha": 0},
            "deficits": {"N": 30, "P": 0, "K": 0},
        },
        "irrigation": {
            "priority": "High & Urgent",
            "message": "Water stress < critical & temp > 35°C",
            "recommended_actions": [
                "Irrigate < 24h to avoid wilting",
                "Check EC < 2.0 & salinity",
            ],
            "soil_moisture": 10.5,
            "evapotranspiration_risk": "High & Extreme",
        },
        "risks": {
            "overall_risk_level": "Critical & Severe",
            "high_risk_count": 2,
            "risks": [
                "Frost hazard < 4°C & wind > 15 m/s",
                "Pest pressure > 70% <b>severe",
            ],
        },
        "crop_profile": {
            "display_name": "Rice (Oryza sativa) <grain>",
            "description": "High water-requiring cereal staple <br> thriving in heavy & clay soil.",
        },
    }

    pdf_bytes = generate_pdf_advisory_report(malformed_pred, malformed_adv)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")


def test_generate_pdf_string_percentage_parsing():
    """Verify string percentages like '87.4%' don't fail float conversion."""
    import base64, zlib
    pred = {
        "recommended_crop": "chickpea",
        "confidence": "87.4%",
        "probabilities": [
            {"crop": "chickpea", "percentage": "87.4%"},
            {"crop": "lentil", "percentage": "12.6%"},
        ],
        "important_features": [
            {"feature": "Rainfall", "impact_percentage": "35.2%", "direction": "positive"},
        ],
    }
    adv = {
        "soil": {"status": "Good", "issues": ["Healthy"]},
        "fertilizer": {"recommendations": ["Sufficient"]},
        "irrigation": {"priority": "Low", "message": "Adequate"},
        "risks": {"risks": ["Normal"]},
        "crop_profile": {"display_name": "Chickpea (Cicer arietinum)"},
    }
    pdf_bytes = generate_pdf_advisory_report(pred, adv)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")

    # Decompress ASCII85 + Flate stream to verify 87.4% was correctly parsed and embedded
    pos = pdf_bytes.find(b"stream\n") + 7
    end = pdf_bytes.find(b"~>endstream") + 2
    raw = pdf_bytes[pos:end]
    decomp = zlib.decompress(base64.a85decode(raw, adobe=True))
    assert b"87.4" in decomp


def test_generate_pdf_includes_crop_comparison_and_xai(valid_farm_payload):
    import base64, zlib
    sanitized = validate_farm_input(valid_farm_payload)
    predictor = get_predictor()
    pred = predictor.predict(sanitized)
    top_three = pred.get("top_three", [])
    adv = generate_full_advisory(sanitized, pred["recommended_crop"], top_crops=top_three)

    pdf_bytes = generate_pdf_advisory_report(pred, adv)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")

    pos = pdf_bytes.find(b"stream\n") + 7
    end = pdf_bytes.find(b"~>endstream") + 2
    raw = pdf_bytes[pos:end]
    decomp = zlib.decompress(base64.a85decode(raw, adobe=True))
    assert b"Top-3 Crop Recommendations" in decomp
    assert b"Explainable AI Feature Attribution" in decomp

