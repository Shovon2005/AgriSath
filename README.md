# AgriSathi | Precision Agriculture Intelligent Decision Support Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.x-green.svg)](https://flask.palletsprojects.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn%20%7C%20SHAP-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

AgriSathi is an explainable AI-driven decision support framework engineered for precision agriculture. It synthesizes real-time soil chemistry, atmospheric telemetry, and farm management practices to deliver accurate multi-crop recommendations, localized feature contributions (SHAP XAI), commercial fertilizer dosing schedules (Urea, DAP, MOP), smart irrigation timing, and multi-hazard environmental risk diagnostics.

---

## System Architecture

```text
                                 [ User / Client ]
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
                  Web UI (Flask)                RESTful JSON API
                  GET / , POST /predict         POST /api/v1/predict
                  POST /download-report         POST /api/v1/report
                         │                             │
                         └──────────────┬──────────────┘
                                        ▼
                          [ Core Input Validator ]
                           (22 Bounds & Categoricals)
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
               [ ML Inference Engine ]      [ Agronomic Advisory Engine ]
             • Random Forest Pipeline       • Soil Reaction & OM Health
             • Top-5 Class Probabilities    • Crop-Tailored NPK Deficits
             • Local SHAP TreeExplainer     • Evapotranspiration Irrigation
                                            • Multi-Hazard Risk Matrix
                         │                             │
                         └──────────────┬──────────────┘
                                        ▼
                           [ ReportLab PDF Generator ]
                             (Official Agronomic PDF)
```

---

## Key Features

1. **High-Precision Multi-Crop AI Model**:
   - Random Forest pipeline trained on multi-parameter agricultural data across 22 crops.
   - Standardized categorical encoding with string-level normalization (`Clay`, `Loamy`, `Sandy`).
   - Achieves 100% test split accuracy with calibrated confidence scoring.

2. **True Local Explainable AI (XAI)**:
   - Uses **SHAP `TreeExplainer`** to calculate exact instance-level feature attributions for each farmer's specific inputs (runs in <10ms).
   - Generates directional insights ("High rainfall +202mm strongly supported Rice").

3. **Expert Agronomic Advisory Engines**:
   - **Soil Health Assessment**: Evaluates soil pH, organic matter fraction, and macronutrient balance with corrective agricultural liming/gypsum recommendations.
   - **Fertilizer Dosage Calculator**: Computes target NPK deficits for the recommended crop and calculates commercial fertilizer amounts (kg/ha of Urea, DAP, and MOP) and application schedules.
   - **Smart Irrigation Advisory**: Dynamically evaluates soil moisture, temperature, humidity, rainfall, and crop phenological stage to establish irrigation urgency.
   - **Multi-Hazard Environmental Risk**: Detects frost damage susceptibility, pest outbreaks, heat stress, foliar fungal risks, and peri-urban interfaces.

4. **Professional PDF Advisory Reports**:
   - Generates publication-quality agronomic reports via ReportLab with executive summary, scorecard tables, commercial dosing schedules, and XAI feature contributions.

5. **RESTful JSON API & Modern Responsive Web UI**:
   - Endpoints for headless integrations (`/api/v1/health`, `/api/v1/crops`, `/api/v1/predict`, `/api/v1/report`).
   - 1-click farm demo presets on Web UI (Wetland Rice, Semi-Arid Chickpea, Commercial Cotton, Multi-Risk Alert).

---

## Directory Structure

```text
AgriSath/
├── Makefile                    # Unified developer commands (lint, test, build, dev)
├── setup.sh                    # Automated 1-command local environment setup script
├── pyproject.toml              # Python package metadata and tool configuration
├── requirements.txt            # Pinned Python requirements
├── Crop_recommendationV2.csv   # Agricultural training dataset (22 crops, 22 features)
├── app.py                      # Flask REST API server launcher (port 5001)
├── train_model.py              # Backward-compatible model training launcher
├── recommendation.py           # Backward-compatible advisory wrappers
├── explain.py                  # Backward-compatible XAI wrappers
├── agrisathi/                  # Core Python backend package
│   ├── config.py               # Environment configuration & dynamic path resolution
│   ├── core/                   # Domain schemas, exceptions, and validation
│   ├── advisory/               # Expert agronomic advisory engines (soil, NPK, water, risk)
│   ├── ml/                     # ML training, preprocessing, inference & SHAP XAI
│   ├── reports/                # ReportLab PDF advisory report generator
│   ├── utils/                  # Structured logging & Open-Meteo weather client
│   └── web/                    # Modular Flask Application Factory & Blueprints
├── frontend/                   # Decoupled Next.js 14 Frontend Application
│   ├── src/app/                # App Router pages (/, /history, /result)
│   ├── src/components/         # Reusable UI & form sections (presets, inputs, cards)
│   ├── src/components/xai/     # SHAP Waterfall chart & What-If simulator
│   ├── src/lib/                # Type-safe API client & utilities
│   └── src/types/              # TypeScript schemas & API response interfaces
├── data/                       # Dynamic agronomic profiles & rules
├── docs/plans/                 # Architecture & verified implementation plans
├── model/                      # Trained model artifacts & metrics
├── scripts/                    # CLI utilities (train, evaluate, generate report, run server)
├── static/                     # Legacy static assets
├── templates/                  # Legacy Jinja2 templates
└── tests/                      # 164 automated unit, integration, and route tests
```

---

## Quickstart & Local Setup

### Option 1: Using Makefile (Recommended)
```bash
make setup          # Creates .venv, installs Python dependencies and Next.js npm packages
make lint           # Runs Python AST validation + Next.js ESLint + TypeScript typecheck
make test           # Runs complete pytest suite (164 tests)
make run            # Launches Flask backend on http://127.0.0.1:5001
make run-frontend   # Launches Next.js frontend on http://localhost:3000
```

### Option 2: Automated Script
```bash
./setup.sh
```

### Option 3: Manual Execution
```bash
# 1. Backend (Terminal 1)
source .venv/bin/activate
python app.py

# 2. Frontend (Terminal 2)
cd frontend
npm run dev
```

- **Next.js Web UI:** [http://localhost:3000](http://localhost:3000)
- **Flask REST API:** [http://127.0.0.1:5001](http://127.0.0.1:5001)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies and editable package
pip install -r requirements.txt -e .

# Launch application
python app.py
```

Open your browser to: **http://127.0.0.1:5001**

---

## REST API Documentation

### 1. Health Check
```bash
curl -X GET http://127.0.0.1:5001/api/v1/health
```

### 2. Predict Crop & Generate Full Advisory
```bash
curl -X POST http://127.0.0.1:5001/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "N": 90, "P": 42, "K": 43, "temperature": 20.8, "humidity": 82.0, "ph": 6.5,
    "rainfall": 202.9, "soil_moisture": 29.4, "soil_type": "Clay",
    "sunlight_exposure": 8.6, "wind_speed": 10.1, "co2_concentration": 435.6,
    "organic_matter": 3.1, "irrigation_frequency": 4, "crop_density": 11.7,
    "pest_pressure": 57.6, "fertilizer_usage": 188.1, "growth_stage": "Vegetative",
    "urban_area_proximity": 2.7, "water_source_type": "Canal", "frost_risk": 5.0,
    "water_usage_efficiency": 1.2
  }'
```

### 3. Generate & Download PDF Advisory Report
```bash
curl -X POST http://127.0.0.1:5001/api/v1/report \
  -H "Content-Type: application/json" \
  -d '{ ...farm parameters... }' \
  --output advisory_report.pdf
```

---

## Running Automated Tests

Run the complete test suite with coverage report:
```bash
.venv/bin/pytest -v tests/
```

Verify test coverage:
```bash
.venv/bin/pytest --cov=agrisathi --cov-report=term-missing tests/
```

---

## License
MIT License. © 2026 AgriSathi Team.
