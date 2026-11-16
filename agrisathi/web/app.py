"""
Flask Application Factory for AgriSathi.
"""

from pathlib import Path
from flask import Flask, render_template, jsonify, request
from agrisathi.config import Config, config
from agrisathi.web.routes.views import views_bp
from agrisathi.web.routes.api import api_bp
from agrisathi.utils.logger import get_logger

logger = get_logger("agrisathi.web")


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

    @app.context_processor
    def inject_defaults():
        return {"demo_data": {}, "active_preset": "", "form_data": {}}

    # Custom Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not Found", "message": "The requested API endpoint does not exist."}), 404
        return render_template("404.html"), 404

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
