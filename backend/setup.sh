#!/usr/bin/env bash
set -e

echo "=== Setting up AgriSathi Python Backend ==="

if command -v uv &> /dev/null; then
    uv venv ../.venv --python 3.10
    uv pip install -r requirements.txt -e .
else
    python3 -m venv ../.venv
    source ../.venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt -e .
fi

echo "Backend installation verified."
