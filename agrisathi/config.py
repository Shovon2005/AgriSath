"""
Configuration management for AgriSathi.
Resolves paths dynamically relative to project root.
"""

import os
from pathlib import Path


class Config:
    # Project root directory
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Data paths
    DATA_DIR = BASE_DIR / "data"
    DATASET_PATH = BASE_DIR / "Crop_recommendationV2.csv"
    CROP_PROFILES_PATH = DATA_DIR / "crop_agronomic_profiles.json"

    # Model paths
    MODEL_DIR = BASE_DIR / "model"
    MODEL_PATH = MODEL_DIR / "crop_model.pkl"
    FEATURE_INFO_PATH = MODEL_DIR / "feature_info.pkl"
    FEATURE_INFO_JSON_PATH = MODEL_DIR / "feature_info.json"
    MODEL_METRICS_PATH = MODEL_DIR / "metrics.json"

    # Web & App Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "agrisathi-secure-dev-key-2026")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    PORT = int(os.getenv("FLASK_PORT", "5001"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def ensure_directories(cls):
        """Ensure necessary runtime directories exist."""
        cls.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = False


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
