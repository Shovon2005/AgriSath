"""
Web HTML View Blueprint for AgriSathi.
"""

import io
from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from agrisathi.core.validator import validate_farm_input
from agrisathi.core.exceptions import ValidationError
from agrisathi.ml.predictor import get_predictor
from agrisathi.advisory.engine import generate_full_advisory
from agrisathi.reports.pdf_generator import generate_pdf_advisory_report
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.views")
views_bp = Blueprint("views", __name__)

# Sample presets for 1-click testing
DEMO_PRESETS = {
    "rice": {
        "N": 90, "P": 42, "K": 43, "temperature": 21.0, "humidity": 82.0, "ph": 6.5,
        "rainfall": 202.0, "soil_moisture": 30.0, "soil_type": "Clay",
        "sunlight_exposure": 8.5, "wind_speed": 10.0, "co2_concentration": 435.0,
        "organic_matter": 3.2, "irrigation_frequency": 4, "crop_density": 12.0,
        "pest_pressure": 55.0, "fertilizer_usage": 180.0, "growth_stage": "Vegetative",
        "urban_area_proximity": 15.0, "water_source_type": "Canal", "frost_risk": 5.0,
        "water_usage_efficiency": 1.2
    },
    "chickpea": {
        "N": 40, "P": 60, "K": 80, "temperature": 18.0, "humidity": 25.0, "ph": 7.2,
        "rainfall": 40.0, "soil_moisture": 12.0, "soil_type": "Sandy",
        "sunlight_exposure": 10.0, "wind_speed": 5.0, "co2_concentration": 390.0,
        "organic_matter": 2.0, "irrigation_frequency": 1, "crop_density": 10.0,
        "pest_pressure": 15.0, "fertilizer_usage": 60.0, "growth_stage": "Seedling",
        "urban_area_proximity": 30.0, "water_source_type": "Groundwater", "frost_risk": 2.0,
        "water_usage_efficiency": 3.8
    },
    "cotton": {
        "N": 120, "P": 50, "K": 30, "temperature": 28.0, "humidity": 65.0, "ph": 7.5,
        "rainfall": 80.0, "soil_moisture": 22.0, "soil_type": "Clay",
        "sunlight_exposure": 9.0, "wind_speed": 4.0, "co2_concentration": 410.0,
        "organic_matter": 3.5, "irrigation_frequency": 2, "crop_density": 14.0,
        "pest_pressure": 45.0, "fertilizer_usage": 120.0, "growth_stage": "Vegetative",
        "urban_area_proximity": 20.0, "water_source_type": "Canal", "frost_risk": 0.0,
        "water_usage_efficiency": 2.2
    },
    "alert": {
        "N": 20, "P": 15, "K": 10, "temperature": 39.5, "humidity": 88.0, "ph": 4.5,
        "rainfall": 15.0, "soil_moisture": 9.0, "soil_type": "Sandy",
        "sunlight_exposure": 11.5, "wind_speed": 16.5, "co2_concentration": 420.0,
        "organic_matter": 0.9, "irrigation_frequency": 1, "crop_density": 8.0,
        "pest_pressure": 92.0, "fertilizer_usage": 50.0, "growth_stage": "Flowering",
        "urban_area_proximity": 3.0, "water_source_type": "Groundwater", "frost_risk": 75.0,
        "water_usage_efficiency": 1.0
    }
}


@views_bp.route("/")
def home():
    """Render farm parameter input form."""
    preset_key = request.args.get("demo", "").lower()
    demo_data = DEMO_PRESETS.get(preset_key, {})
    return render_template("index.html", demo_data=demo_data, active_preset=preset_key)


@views_bp.route("/predict", methods=["POST"])
def predict():
    """Process farm parameters and display AI recommendation and agronomic advisory."""
    raw_data = request.form.to_dict()

    try:
        sanitized = validate_farm_input(raw_data)
        predictor = get_predictor()
        prediction = predictor.predict(sanitized)
        advisory = generate_full_advisory(sanitized, prediction["recommended_crop"])

        return render_template(
            "result.html",
            crop=prediction["recommended_crop"].title(),
            confidence=prediction["confidence"],
            soil=advisory["soil"],
            irrigation=advisory["irrigation"],
            fertilizer=advisory["fertilizer"]["recommendations"],
            fertilizer_details=advisory["fertilizer"],
            risks=advisory["risks"]["risks"],
            risk_details=advisory["risks"],
            important_features=prediction["important_features"],
            probabilities=prediction["probabilities"],
            input_data=sanitized,
            crop_profile=advisory["crop_profile"],
        )

    except ValidationError as e:
        logger.warning("Validation failure on /predict: %s", e.details)
        return render_template(
            "index.html",
            error=e.message,
            error_details=e.details,
            form_data=raw_data,
            demo_data={},
            active_preset="",
        ), 422
    except Exception as e:
        logger.error("Error during prediction: %s", e, exc_info=True)
        return render_template("error.html", error_message=str(e)), 500


@views_bp.route("/download-report", methods=["POST"])
def download_report():
    """Generate and return PDF report from submitted farm data."""
    raw_data = request.form.to_dict()

    try:
        sanitized = validate_farm_input(raw_data)
        predictor = get_predictor()
        prediction = predictor.predict(sanitized)
        advisory = generate_full_advisory(sanitized, prediction["recommended_crop"])

        pdf_bytes = generate_pdf_advisory_report(prediction, advisory)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"AgriSathi_Advisory_{prediction['recommended_crop']}.pdf",
        )
    except Exception as e:
        logger.error("Download report failed: %s", e)
        return render_template("error.html", error_message=f"PDF generation error: {e}"), 500
