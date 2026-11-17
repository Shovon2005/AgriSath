.PHONY: setup venv install test train run run-frontend frontend-install dev clean lint

PYTHON := .venv/bin/python
PIP := .venv/bin/pip
PYTEST := .venv/bin/pytest

setup: venv install frontend-install

venv:
	uv venv .venv --python 3.10

install:
	uv pip install -r requirements.txt -e .

frontend-install:
	cd frontend && npm install

run-frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting Next.js frontend (requires Flask backend running on port 5001)..."
	cd frontend && npm run dev

test:
	$(PYTEST) -v --tb=short tests/

train:
	$(PYTHON) -m agrisathi.ml.train

run:
	$(PYTHON) app.py

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
	$(PYTHON) -c "import ast, glob; [ast.parse(open(f).read(), filename=f) for f in glob.glob('**/*.py', recursive=True) if '.venv' not in f]; print('All Python files passed syntax and AST validation.')"
