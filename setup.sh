#!/usr/bin/env bash
set -e

echo "=== Setting up AgriSathi Decoupled Full-Stack Environment ==="

# 1. Backend Setup
echo "[1/2] Setting up Python backend..."
if command -v uv &> /dev/null; then
    echo "Found uv. Ensuring virtual environment with Python 3.10..."
    uv venv .venv --python 3.10
    echo "Installing backend requirements and editable package..."
    uv pip install -r backend/requirements.txt -e backend
else
    echo "uv not found, using python3 venv..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r backend/requirements.txt -e backend
fi

# 2. Frontend Setup
echo "[2/2] Setting up Next.js frontend dependencies..."
if command -v npm &> /dev/null; then
    (cd frontend && npm install)
else
    echo "Warning: npm not found on PATH. Please install Node.js (v18+) to run the Next.js frontend."
fi

echo "Verifying backend installation..."
.venv/bin/python -c "import agrisathi; import sklearn; import shap; import flask; import reportlab; print('✓ AgriSathi backend environment ready!')"

echo "=== AgriSathi Setup Completed Successfully ==="
echo "To run the application:"
echo "  1. Backend API:  make run-backend   (http://127.0.0.1:5001)"
echo "  2. Next.js UI:   make run-frontend  (http://localhost:3000)"
