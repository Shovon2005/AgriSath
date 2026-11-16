"""
RESTful JSON API Blueprint for AgriSathi.
"""

import io
from flask import Blueprint, request, jsonify, send_file
from agrisathi import __version__
from agrisathi.core.validator import validate_farm_input
from agrisathi.core.exceptions import ValidationError, AgriSathiError
from agrisathi.ml.predictor import get_predictor
from agrisathi.advisory.profiles import get_crop_profiles
from agrisathi.advisory.engine import generate_full_advisory
from agrisathi.reports.pdf_generator import generate_pdf_advisory_report
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.api")
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        predictor = get_predictor()
        model_loaded = predictor.pipeline is not None
    except Exception:
        model_loaded = False

    status = "healthy" if model_loaded else "degraded"
    code = 200 if model_loaded else 503
    return jsonify({
        "status": status,
        "service": "AgriSathi Precision Agriculture API",
        "version": __version__,
        "model_loaded": model_loaded,
    }), code


@api_bp.route("/crops", methods=["GET"])
def list_crops():
    """List all supported crops and their agronomic profiles."""
    profiles = get_crop_profiles()
    return jsonify({
        "count": len(profiles),
        "crops": profiles,
    }), 200


@api_bp.route("/crops/<crop_name>", methods=["GET"])
def get_crop(crop_name: str):
    """Retrieve agronomic profile for a specific crop."""
    profiles = get_crop_profiles()
    key = crop_name.strip().lower()
    if key not in profiles:
        return jsonify({
            "error": "Crop Not Found",
            "message": f"No agronomic profile found for crop '{crop_name}'."
        }), 404
    return jsonify({
        "crop": key,
        "profile": profiles[key],
    }), 200


@api_bp.route("/predict", methods=["POST"])
def predict():
    """Execute prediction and agronomic advisory from JSON payload."""
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({
            "error": "Bad Request",
            "message": "Missing JSON body in POST request."
        }), 400

    try:
        sanitized = validate_farm_input(payload)
        predictor = get_predictor()
        prediction = predictor.predict(sanitized)
        advisory = generate_full_advisory(sanitized, prediction["recommended_crop"])

        return jsonify({
            "status": "success",
            "prediction": prediction,
            "advisory": advisory,
        }), 200

    except ValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "message": e.message,
            "details": e.details,
        }), 422
    except AgriSathiError as e:
        return jsonify({
            "error": "Processing Error",
            "message": e.message,
        }), 500
    except Exception as e:
        logger.error("API Prediction failed: %s", e, exc_info=True)
        return jsonify({
            "error": "Internal Error",
            "message": str(e),
        }), 500


@api_bp.route("/report", methods=["POST"])
def generate_report():
    """Generate and download PDF advisory report from JSON payload."""
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({
            "error": "Bad Request",
            "message": "Missing JSON body in POST request."
        }), 400

    try:
        sanitized = validate_farm_input(payload)
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

    except ValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "message": e.message,
            "details": e.details,
        }), 422
    except Exception as e:
        logger.error("API Report generation failed: %s", e)
        return jsonify({"error": "Report Generation Failed", "message": str(e)}), 500
