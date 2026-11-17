"""
Flask Application Factory for AgriSathi.
"""

from flask import Flask, render_template, jsonify, request
from agrisathi.config import Config, config
from agrisathi.core.schemas import FEATURE_NAMES
from agrisathi.advisory.profiles import get_crop_profiles
from agrisathi.data.scenarios import get_farm_scenarios
from agrisathi.web.routes.views import views_bp
from agrisathi.web.routes.api import api_bp
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.web")
_FEATURE_COUNT = len(FEATURE_NAMES)


def create_app(config_name: str = "default") -> Flask:
    """Create and configure Flask application instance."""
    app_config = config.get(config_name, Config)

    template_dir = Config.BASE_DIR / "templates"
    static_dir = Config.BASE_DIR / "static"

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
    )

    app.config.from_object(app_config)

    # Register blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)

    # CORS handling for Next.js frontend
    allowed_origins = getattr(app_config, "CORS_ORIGINS", ["*"])

    def _get_origin():
        req_origin = request.headers.get("Origin")
        if not req_origin or "*" in allowed_origins:
            return req_origin or "*"
        return req_origin if req_origin in allowed_origins else allowed_origins[0]

    @app.before_request
    def handle_cors_preflight():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            origin = _get_origin()
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "86400"
            return response

    @app.after_request
    def add_cors_headers(response):
        origin = _get_origin()
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    @app.context_processor
    def inject_defaults():
        scenarios = get_farm_scenarios()
        try:
            crop_count = len(get_crop_profiles())
        except Exception:
            crop_count = 22

        return {
            "demo_data": {},
            "active_preset": "",
            "form_data": {},
            "scenarios": scenarios,
            "crop_count": crop_count,
            "feature_count": _FEATURE_COUNT,
        }

    # Custom Error Handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Bad Request", "message": getattr(error, "description", "Malformed request.")}), 400
        return render_template("error.html", error_message="Bad Request"), 400

    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not Found", "message": "The requested API endpoint does not exist."}), 404
        return render_template("404.html"), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Method Not Allowed", "message": "The HTTP method is not allowed for this endpoint."}), 405
        return render_template("error.html", error_message="Method Not Allowed"), 405

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Internal Server Error: %s", error)
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal Server Error", "message": "An unexpected server error occurred."}), 500
        return render_template("500.html"), 500

    @app.errorhandler(422)
    def unprocessable_entity_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Unprocessable Entity", "message": "Invalid request parameters."}), 422
        return render_template("error.html", error_message="Invalid request parameters."), 422

    logger.info("AgriSathi Flask application initialized successfully.")
    return app
