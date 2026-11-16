#!/usr/bin/env bash
set -e

echo "=== Setting up AgriSathi Local Environment ==="

if command -v uv &> /dev/null; then
    echo "Found uv. Creating virtual environment with Python 3.10..."
    uv venv .venv --python 3.10
    echo "Installing project requirements and development package..."
    uv pip install -r requirements.txt -e .
else
    echo "uv not found, using python3 venv..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt -e .
fi

echo "Verifying installation..."
.venv/bin/python -c "import agrisathi; import sklearn; import shap; import flask; import reportlab; print('AgriSathi environment ready!')"

echo "=== Setup Completed Successfully ==="
