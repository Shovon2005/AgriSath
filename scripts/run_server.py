#!/usr/bin/env python3
"""
CLI script to launch AgriSathi development server.
"""

from agrisathi.config import Config
from agrisathi.web.app import create_app


def main():
    app = create_app()
    print(f"Starting AgriSathi on http://{Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)


if __name__ == "__main__":
    main()
