.PHONY: setup setup-backend setup-frontend venv install test train run run-backend run-frontend dev clean lint frontend-lint frontend-typecheck frontend-build

PYTHON := .venv/bin/python
PIP := .venv/bin/pip
PYTEST := .venv/bin/pytest

setup: venv install setup-frontend

venv:
	uv venv .venv --python 3.10

install: setup-backend

setup-backend:
	uv pip install -r backend/requirements.txt -e backend

setup-frontend:
	cd frontend && npm install

run-backend:
	@echo "Starting AgriSathi Flask REST backend on http://127.0.0.1:5001..."
	$(PYTHON) backend/app.py

run-frontend:
	@echo "Starting AgriSathi Next.js frontend on http://localhost:3000..."
	cd frontend && npm run dev

run: run-backend

dev:
	@echo "=========================================================="
	@echo " AgriSathi Multi-Service Full-Stack Development Launcher  "
	@echo "=========================================================="
	@echo " Launch backend and frontend in separate terminals:"
	@echo "   Terminal 1 (Backend API):  make run-backend"
	@echo "   Terminal 2 (Next.js UI):   make run-frontend"
	@echo "=========================================================="
	$(PYTHON) backend/app.py

test:
	$(PYTEST) -v --tb=short backend/tests/

train:
	$(PYTHON) backend/train_model.py

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov build dist *.egg-info
	rm -rf backend/__pycache__ backend/.pytest_cache backend/*.egg-info
	rm -rf frontend/.next
	find . -type d -name "__pycache__" -exec rm -rf {} +

frontend-lint:
	cd frontend && npm run lint

frontend-typecheck:
	cd frontend && npx tsc --noEmit

frontend-build:
	cd frontend && npm run build

lint:
	$(PYTHON) -c "import ast, glob; [ast.parse(open(f).read(), filename=f) for f in glob.glob('backend/**/*.py', recursive=True) if '.venv' not in f]; print('All backend Python files passed syntax and AST validation.')"
	cd frontend && npm run lint
	cd frontend && npx tsc --noEmit
