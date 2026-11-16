"""
AgriSathi - Precision Agriculture Decision Support Engine.
Backward-compatible root entrypoint launching modular Flask application.
"""

import joblib
from agrisathi.config import Config
from agrisathi.core.schemas import FEATURE_NAMES, CATEGORICAL_FEATURES
from agrisathi.web.app import create_app

app = create_app()

# Backward-compatible exports
features = FEATURE_NAMES
categorical_features = CATEGORICAL_FEATURES
try:
    model = joblib.load(Config.MODEL_PATH) if Config.MODEL_PATH.exists() else None
except Exception:
    model = None

if __name__ == "__main__":
    print(f"Starting AgriSathi server on http://{Config.HOST}:{Config.PORT} (debug={Config.DEBUG})...")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
