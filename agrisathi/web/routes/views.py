"""
Web HTML View Blueprint for AgriSathi.
"""

import io
from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from agrisathi.core.schemas import FEATURE_NAMES, FEATURE_MAP
from agrisathi.core.exceptions import ValidationError
from agrisathi.advisory.engine import run_full_pipeline
from agrisathi.reports.pdf_generator import generate_pdf_advisory_report
from agrisathi.data.history import (
    save_prediction_record,
    get_recent_predictions,
    get_prediction_by_id,
)
from agrisathi.data.scenarios import (
    get_farm_scenarios,
    get_scenario_parameters_map,
)
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.views")
views_bp = Blueprint("views", __name__)

# Dynamic scenarios proxy
class _DynamicPresetsProxy(dict):
    """Dynamic dict proxy always querying fresh scenario parameter mappings."""
    def __getitem__(self, key):
        return get_scenario_parameters_map()[key]
    def get(self, key, default=None):
        return get_scenario_parameters_map().get(key, default)
    def items(self):
        return get_scenario_parameters_map().items()
    def keys(self):
        return get_scenario_parameters_map().keys()
    def values(self):
        return get_scenario_parameters_map().values()
    def __contains__(self, key):
        return key in get_scenario_parameters_map()
    def __len__(self):
        return len(get_scenario_parameters_map())

DEMO_PRESETS = _DynamicPresetsProxy()


@views_bp.route("/")
def home():
    """Render farm parameter input form with dynamic scenarios."""
    scenarios = get_farm_scenarios()
    preset_key = request.args.get("demo", "").lower()
    active_scenario = scenarios.get(preset_key)
    demo_data = active_scenario.get("parameters", {}) if active_scenario else {}
    return render_template(
        "index.html",
        demo_data=demo_data,
        active_preset=preset_key,
        scenarios=scenarios,
    )


@views_bp.route("/predict", methods=["GET", "POST"])
def predict():
    """Process farm parameters and display AI recommendation and agronomic advisory."""
    if request.method == "GET":
        return redirect(url_for("views.home"))

    raw_data = request.form.to_dict()

    try:
        sanitized, prediction, advisory = run_full_pipeline(raw_data)
        record_id = save_prediction_record(sanitized, prediction, advisory)

        # Clean display dictionary for Farm Input Summary
        display_inputs = {}
        for name in FEATURE_NAMES:
            spec = FEATURE_MAP[name]
            label_val = sanitized.get(f"{name}_label", sanitized.get(name))
            unit_str = f" {spec.unit}" if spec.unit else ""
            display_inputs[spec.display_name] = f"{label_val}{unit_str}"

        # Add extended parameter entries to summary
        display_inputs["Farm Location"] = sanitized.get("location", "Local Farm")
        display_inputs["Cropping Season"] = sanitized.get("season", "Whole Year")
        display_inputs["Farm Area"] = f"{sanitized.get('farm_area', 1.0)} {sanitized.get('farm_area_unit', 'hectare')}"
        display_inputs["Electrical Conductivity (EC)"] = f"{sanitized.get('electrical_conductivity', 0.6)} dS/m"
        display_inputs["Organic Carbon (OC)"] = f"{sanitized.get('organic_carbon', 0.75)} %"

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
            crop_comparison=advisory.get("crop_comparison", {}),
            waterfall=prediction.get("waterfall", {}),
            explanation_narrative=prediction.get("explanation_narrative", ""),
            important_features=prediction["important_features"],
            probabilities=prediction["probabilities"],
            top_three=prediction.get("top_three", []),
            record_id=record_id,
            input_data=sanitized,
            display_inputs=display_inputs,
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
            scenarios=get_farm_scenarios(),
        ), 422
    except Exception as e:
        logger.error("Error during prediction: %s", e, exc_info=True)
        return render_template("error.html", error_message=str(e)), 500


@views_bp.route("/download-report", methods=["GET", "POST"])
def download_report():
    """Generate and return PDF report from submitted farm data."""
    if request.method == "GET":
        return redirect(url_for("views.home"))

    raw_data = request.form.to_dict()

    try:
        _, prediction, advisory = run_full_pipeline(raw_data)
        pdf_bytes = generate_pdf_advisory_report(prediction, advisory)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"AgriSathi_Advisory_{prediction['recommended_crop']}.pdf",
        )
    except ValidationError as e:
        logger.warning("Validation failure on /download-report: %s", e.details)
        return render_template(
            "index.html",
            error=e.message,
            error_details=e.details,
            form_data=raw_data,
            demo_data={},
            active_preset="",
            scenarios=get_farm_scenarios(),
        ), 422
    except Exception as e:
        logger.error("Download report failed: %s", e)
        return render_template("error.html", error_message=f"PDF generation error: {e}"), 500


@views_bp.route("/history")
def history():
    """Display past farm recommendations and historical reports."""
    crop_filter = request.args.get("crop")
    records = get_recent_predictions(limit=50, crop_filter=crop_filter)
    return render_template("history.html", history=records, active_crop=crop_filter or "")


@views_bp.route("/history/<int:record_id>")
def history_detail(record_id: int):
    """View details of a specific historical prediction."""
    record = get_prediction_by_id(record_id)
    if not record:
        flash(f"Historical report #{record_id} not found.", "warning")
        return redirect(url_for("views.history"))
    return render_template("history.html", history=[record], active_crop="", selected_record=record)


@views_bp.route("/history/<int:record_id>/pdf")
def history_pdf(record_id: int):
    """Download PDF advisory report for a specific historical assessment."""
    record = get_prediction_by_id(record_id)
    if not record or not record.get("inputs"):
        flash(f"Historical record #{record_id} inputs could not be loaded for PDF export.", "warning")
        return redirect(url_for("views.history"))

    try:
        _, prediction, advisory = run_full_pipeline(record["inputs"], allow_defaults=True)
        pdf_bytes = generate_pdf_advisory_report(prediction, advisory)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"AgriSathi_Advisory_Report_{record_id}_{prediction['recommended_crop']}.pdf",
        )
    except Exception as e:
        logger.error("Failed to generate PDF for historical record %s: %s", record_id, e)
        flash(f"Failed to generate historical report PDF: {e}", "danger")
        return redirect(url_for("views.history_detail", record_id=record_id))

