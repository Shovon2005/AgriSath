"""
RESTful JSON API Blueprint for AgriSathi.
"""

import io
from flask import Blueprint, request, jsonify, send_file
from agrisathi import __version__
from agrisathi.core.validator import validate_farm_input
from agrisathi.core.exceptions import ValidationError, AgriSathiError
from agrisathi.ml.predictor import get_predictor
from agrisathi.ml.whatif import simulate_what_if
from agrisathi.advisory.profiles import (
    get_crop_profiles,
    update_crop_profile,
    get_agronomic_rules,
    update_agronomic_rules,
    reload_agronomic_rules,
)
from agrisathi.advisory.engine import generate_full_advisory
from agrisathi.reports.pdf_generator import generate_pdf_advisory_report
from agrisathi.utils.weather import (
    fetch_weather_data,
    get_regional_weather_baselines,
    update_weather_baselines,
    reload_weather_baselines,
)
from agrisathi.data.scenarios import (
    get_farm_scenarios,
    get_farm_scenario,
    save_farm_scenario,
    delete_farm_scenario,
)
from agrisathi.data.history import (
    save_prediction_record,
    get_recent_predictions,
    get_prediction_by_id,
)
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


@api_bp.route("/crops/<crop_name>", methods=["POST", "PUT"])
def update_crop(crop_name: str):
    """Dynamically update or register a crop agronomic profile."""
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Bad Request", "message": "Missing JSON body."}), 400

    updated = update_crop_profile(crop_name, payload)
    return jsonify({
        "status": "success",
        "crop": crop_name.lower(),
        "profile": updated,
    }), 200


@api_bp.route("/rules", methods=["GET"])
def list_rules():
    """Retrieve dynamic agronomic rules, conversion ratios, and thresholds."""
    rules = get_agronomic_rules()
    return jsonify({
        "status": "success",
        "rules": rules,
    }), 200


@api_bp.route("/rules", methods=["POST", "PUT"])
def update_rules():
    """Dynamically update agronomic rules and conversion factors."""
    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify({"error": "Bad Request", "message": "Missing or invalid JSON body."}), 400

    updated = update_agronomic_rules(payload)
    return jsonify({
        "status": "success",
        "message": "Dynamic agronomic rules updated successfully.",
        "rules": updated,
    }), 200


@api_bp.route("/rules/reload", methods=["POST"])
def reload_rules():
    """Reload dynamic agronomic rules from configuration storage."""
    rules = reload_agronomic_rules()
    return jsonify({
        "status": "success",
        "message": "Dynamic agronomic rules reloaded successfully.",
        "rules": rules,
    }), 200


@api_bp.route("/scenarios", methods=["GET"])
def list_scenarios():
    """List all dynamic farm scenarios and simulation presets."""
    scenarios = get_farm_scenarios()
    return jsonify({
        "status": "success",
        "count": len(scenarios),
        "scenarios": scenarios,
    }), 200


@api_bp.route("/scenarios/<key>", methods=["GET"])
def get_scenario(key: str):
    """Retrieve single farm scenario by key."""
    sc = get_farm_scenario(key)
    if not sc:
        return jsonify({
            "error": "Scenario Not Found",
            "message": f"Scenario '{key}' not found."
        }), 404
    return jsonify({
        "status": "success",
        "scenario": sc,
    }), 200


@api_bp.route("/scenarios", methods=["POST"])
def add_or_update_scenario():
    """Dynamically save a new or modified farm scenario preset."""
    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict) or "key" not in payload:
        return jsonify({"error": "Bad Request", "message": "Missing 'key' or payload."}), 400

    try:
        saved = save_farm_scenario(payload["key"], payload)
        return jsonify({
            "status": "success",
            "scenario": saved,
        }), 201
    except ValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "message": e.message,
            "details": e.details,
        }), 422


@api_bp.route("/scenarios/<key>", methods=["DELETE"])
def remove_scenario(key: str):
    """Dynamically remove a farm scenario."""
    deleted = delete_farm_scenario(key)
    if not deleted:
        return jsonify({
            "error": "Not Found",
            "message": f"Scenario '{key}' not found or could not be deleted.",
        }), 404

    return jsonify({
        "status": "success",
        "message": f"Scenario '{key}' deleted successfully.",
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
        advisory = generate_full_advisory(
            sanitized,
            prediction["recommended_crop"],
            top_crops=prediction.get("top_three"),
        )
        record_id = save_prediction_record(sanitized, prediction, advisory)

        return jsonify({
            "status": "success",
            "prediction": prediction,
            "advisory": advisory,
            "record_id": record_id,
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


@api_bp.route("/what-if", methods=["POST"])
def what_if():
    """Execute interactive What-If simulation comparing baseline vs modified farm inputs."""
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({
            "error": "Bad Request",
            "message": "Missing JSON body in POST request."
        }), 400

    baseline = payload.get("baseline") or payload
    adjustments = payload.get("adjustments") or payload.get("modifications") or {}

    try:
        result = simulate_what_if(baseline, adjustments)
        return jsonify({
            "status": "success",
            "simulation": result,
        }), 200
    except ValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "message": e.message,
            "details": e.details,
        }), 422
    except Exception as e:
        logger.error("What-If simulation failed: %s", e, exc_info=True)
        return jsonify({"error": "Simulation Failed", "message": str(e)}), 500



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
        advisory = generate_full_advisory(
            sanitized,
            prediction["recommended_crop"],
            top_crops=prediction.get("top_three"),
        )

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
    except AgriSathiError as e:
        return jsonify({
            "error": "Processing Error",
            "message": e.message,
        }), 500
    except Exception as e:
        logger.error("API Report generation failed: %s", e)
        return jsonify({"error": "Report Generation Failed", "message": str(e)}), 500


@api_bp.route("/weather", methods=["GET"])
def get_weather():
    """Retrieve current weather and forecast for given location or coordinates."""
    location = request.args.get("location", "Local Farm")
    lat = request.args.get("lat") or request.args.get("latitude")
    lon = request.args.get("lon") or request.args.get("longitude")

    lat_val = float(lat) if lat is not None else None
    lon_val = float(lon) if lon is not None else None

    weather = fetch_weather_data(location=location, latitude=lat_val, longitude=lon_val)
    return jsonify({
        "status": "success",
        "weather": weather,
    }), 200


@api_bp.route("/weather/baselines", methods=["GET"])
def list_weather_baselines():
    """Retrieve dynamic regional weather baselines."""
    baselines = get_regional_weather_baselines()
    return jsonify({
        "status": "success",
        "count": len(baselines),
        "baselines": baselines,
    }), 200


@api_bp.route("/weather/baselines", methods=["POST", "PUT"])
def update_baselines():
    """Dynamically update or register regional agro-climatic weather baselines."""
    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify({"error": "Bad Request", "message": "Missing or invalid JSON body."}), 400

    updated = update_weather_baselines(payload)
    return jsonify({
        "status": "success",
        "message": "Regional weather baselines updated successfully.",
        "baselines": updated,
    }), 200


@api_bp.route("/weather/baselines/reload", methods=["POST"])
def reload_baselines():
    """Reload regional agro-climatic weather baselines from configuration storage."""
    baselines = reload_weather_baselines()
    return jsonify({
        "status": "success",
        "message": "Regional weather baselines reloaded successfully.",
        "baselines": baselines,
    }), 200


@api_bp.route("/history", methods=["GET"])
def list_history():
    """List historical prediction reports with optional crop filter."""
    limit = int(request.args.get("limit", 20))
    crop_filter = request.args.get("crop")
    records = get_recent_predictions(limit=limit, crop_filter=crop_filter)
    return jsonify({
        "status": "success",
        "count": len(records),
        "history": records,
    }), 200


@api_bp.route("/history/<int:record_id>", methods=["GET"])
def get_history_item(record_id: int):
    """Retrieve detailed historical assessment by ID."""
    rec = get_prediction_by_id(record_id)
    if not rec:
        return jsonify({
            "error": "Not Found",
            "message": f"Historical assessment record #{record_id} not found."
        }), 404
    return jsonify({
        "status": "success",
        "record": rec,
    }), 200

