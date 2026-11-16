"""
AgriSathi - Precision Agriculture Decision Support Engine.
Backward-compatible root entrypoint launching modular Flask application.
"""

from agrisathi.config import Config
from agrisathi.web.app import create_app

app = create_app()

if __name__ == "__main__":
    print(f"Starting AgriSathi server on http://{Config.HOST}:{Config.PORT} (debug={Config.DEBUG})...")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
