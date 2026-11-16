# AgriSathi (Kojita Precision Agriculture) - Master Restructuring & Implementation Plan

## Executive Overview
This implementation plan establishes a production-grade, modular, and scientifically rigorous architecture for the **AgriSathi (AgriAI / Kojita)** Precision Agriculture Decision Support Platform. 

The original codebase had several critical gaps:
1. Flat, unmodularized script structure with global state and hardcoded paths.
2. Silent data-type mismatch: `Crop_recommendationV2.csv` stored categorical variables as integers `[1, 2, 3]`, whereas the web form submitted string values (`Loamy`, `Seedling`, etc.), causing `OneHotEncoder` to ignore all user categorical selections.
3. Missing Explainable AI (XAI): `shap` was listed in requirements but not used; explanations were static global Random Forest feature importances rather than local instance-level contributions.
4. Oversimplified advisory logic: fertilizer and irrigation recommendations ignored crop-specific requirements (e.g. Rice requires high water while Chickpea requires low water; legume crops require low N but high P).
5. Unimplemented PDF report generation despite `reportlab` being in requirements.
6. Zero automated test suite, no REST API endpoints, no input validation, and no backward compatibility bridges.

This plan contains **67 discrete, sequential implementation steps** divided into **10 verified stages**. Every stage is validated with automated tests and committed to the current branch.

---

## Stage 1: Environment Setup, Repo Hygiene & Foundation (Steps 1 – 7)
- [x] **Step 1**: Create a clean, comprehensive `.gitignore` covering Python bytecode, virtual environments (`.venv`), OS metadata (`.DS_Store`), IDE settings, and test/build artifacts.
- [x] **Step 2**: Configure python dependency pinning in `requirements.txt` and project metadata in `pyproject.toml`.
- [x] **Step 3**: Implement dynamic path resolution and environment-driven configuration in `agrisathi/config.py`.
- [x] **Step 4**: Implement structured logging with timestamp and level control in `agrisathi/utils/logger.py`.
- [x] **Step 5**: Clean repository working tree, removing untracked `.DS_Store` and stale pycache artifacts.
- [x] **Step 6**: Provide automated developer tooling (`Makefile` and `setup.sh`) for rapid one-command setup.
- [x] **Step 7**: Verify virtual environment creation, package installations, and base configuration imports. **[Commit Stage 1]**

## Stage 2: Core Domain, Schemas, Validation & Exceptions (Steps 8 – 14)
- [x] **Step 8**: Create custom domain exceptions in `agrisathi/core/exceptions.py` (`ValidationError`, `ModelNotFoundError`, `AdvisoryCalculationError`).
- [x] **Step 9**: Define complete feature schema, units, ranges, and types for all 22 farm parameters in `agrisathi/core/schemas.py`.
- [x] **Step 10**: Define categorical enum mappings (`SoilType`, `GrowthStage`, `WaterSource`) supporting bidirectional conversion between UI strings and model encodings.
- [x] **Step 11**: Implement robust validation engine in `agrisathi/core/validator.py` with boundary checks, type coercion, and friendly error messages.
- [x] **Step 12**: Implement sanitized payload builder returning type-safe dictionaries for inference and advisory engines.
- [x] **Step 13**: Write unit test suite `tests/test_validator.py` verifying schema enforcement, missing inputs, and boundary values.
- [x] **Step 14**: Execute test suite and verify 100% pass rate. **[Commit Stage 2]**

## Stage 3: Agronomic Knowledge Base & Crop Profiling (Steps 15 – 21)
- [x] **Step 15**: Compile scientific agronomic profiles for all 22 crops (optimal pH, NPK requirements in kg/ha, water demand, temperature bounds, humidity tolerance, frost sensitivity).
- [x] **Step 16**: Structure knowledge base into JSON database at `data/crop_agronomic_profiles.json`.
- [x] **Step 17**: Implement profile loader and query service in `agrisathi/advisory/profiles.py`.
- [x] **Step 18**: Define soil textural properties (water holding capacity, drainage, nutrient retention) for Loamy, Clay, and Sandy soils.
- [x] **Step 19**: Define commercial fertilizer conversion constants (Urea: 46% N, DAP: 18% N + 46% P₂O₅, MOP: 60% K₂O).
- [x] **Step 20**: Implement unit tests in `tests/test_profiles.py` verifying all 22 crops load with valid agronomic parameters.
- [x] **Step 21**: Run profile verification tests and ensure dataset consistency. **[Commit Stage 3]**

## Stage 4: Robust ML Data Preprocessing & Training Pipeline (Steps 22 – 28)
- [x] **Step 22**: Implement robust dataset loader and validator in `agrisathi/ml/dataset.py`.
- [x] **Step 23**: Map categorical columns consistently using defined string labels so training and inference share identical feature definitions.
- [x] **Step 24**: Build scikit-learn preprocessing pipeline in `agrisathi/ml/pipeline.py` using `ColumnTransformer`, `OneHotEncoder(handle_unknown='ignore')`, and `RandomForestClassifier`.
- [x] **Step 25**: Implement training, hyperparameter configuration, and stratified train/test split in `agrisathi/ml/train.py`.
- [x] **Step 26**: Compute classification report, accuracy, precision, recall, and save metrics artifact (`model/metrics.json`).
- [x] **Step 27**: Save trained pipeline (`model/crop_model.pkl`) and feature specification (`model/feature_info.json`).
- [x] **Step 28**: Write unit tests `tests/test_ml_pipeline.py` verifying model loading, feature alignment, and prediction reproducibility. **[Commit Stage 4]**

## Stage 5: Inference Engine & Local Explainable AI (XAI) (Steps 29 – 35)
- [x] **Step 29**: Implement thread-safe singleton predictor in `agrisathi/ml/predictor.py`.
- [x] **Step 30**: Compute class prediction probabilities and extract top-5 ranked crops with percentage confidences.
- [x] **Step 31**: Implement local instance-level explainability in `agrisathi/ml/explain.py` using tree leaf path contributions (TreeExplainer / Tree local feature contributions).
- [x] **Step 32**: Translate internal model feature attributions into natural language explanations ("High soil moisture and rainfall favored Rice by +24%").
- [x] **Step 33**: Add fallback to global feature importance if rapid explanation mode is requested.
- [x] **Step 34**: Create unit tests `tests/test_predictor.py` and `tests/test_explain.py` testing edge-case inputs.
- [x] **Step 35**: Verify predictions, probability outputs, and XAI contributions across all crop classes. **[Commit Stage 5]**

## Stage 6: Expert Agronomic Advisory Engines (Steps 36 – 43)
- [x] **Step 36**: Implement Soil Health Assessment engine (`agrisathi/advisory/soil.py`) evaluating pH suitability, organic matter adequacy, and NPK balance.
- [x] **Step 37**: Implement Crop-Specific Fertilizer Recommendation engine (`agrisathi/advisory/fertilizer.py`) computing actual nutrient gaps and required commercial fertilizer dosages (Urea, DAP, MOP in kg/ha).
- [x] **Step 38**: Implement Smart Irrigation Advisory engine (`agrisathi/advisory/irrigation.py`) calculating water stress indices based on soil moisture, rainfall, temperature, crop growth stage, and water source.
- [x] **Step 39**: Implement Multi-Hazard Environmental Risk engine (`agrisathi/advisory/risk.py`) monitoring frost danger, pest outbreak probability, drought stress, and urban proximity factors.
- [x] **Step 40**: Build unified Advisory Orchestrator in `agrisathi/advisory/engine.py` consolidating all recommendations into a cohesive advisory report.
- [x] **Step 41**: Write unit tests in `tests/test_advisory.py`.
- [x] **Step 42**: Test extreme stress cases (drought, excessive moisture, severe acidity/alkalinity, high pest pressure).
- [x] **Step 43**: Verify advisory engine integration tests pass with 100% success. **[Commit Stage 6]**

## Stage 7: Professional PDF Agronomic Advisory Report Generator (Steps 44 – 49)
- [x] **Step 44**: Implement ReportLab document generator in `agrisathi/reports/pdf_generator.py` with custom styles, palettes, and page numbering.
- [x] **Step 45**: Build PDF header block, farm metadata summary, and primary crop recommendation hero banner.
- [x] **Step 46**: Render soil assessment scorecard and commercial fertilizer dosage schedule table (Urea/DAP/MOP).
- [x] **Step 47**: Render smart irrigation schedule, environmental risk warnings, and top-5 alternative crops probability chart.
- [x] **Step 48**: Render Explainable AI feature contribution breakdown and scientific disclaimer footer.
- [x] **Step 49**: Write unit test `tests/test_pdf_report.py` verifying valid PDF generation, non-empty byte buffer, and page structure. **[Commit Stage 7]**

## Stage 8: Modular Web Architecture, RESTful API & UI Enhancements (Steps 50 – 56)
- [x] **Step 50**: Implement Flask Application Factory in `agrisathi/web/app.py` with blueprint registration and configuration loading.
- [x] **Step 51**: Implement Web UI Blueprint in `agrisathi/web/routes/views.py` supporting `/`, `/predict`, `/download-report`, `/demo`, and `/health`.
- [x] **Step 52**: Implement RESTful API Blueprint in `agrisathi/web/routes/api.py` supporting `/api/v1/health`, `/api/v1/predict`, `/api/v1/crops`, `/api/v1/report`.
- [x] **Step 53**: Enhance input template `templates/index.html` with farm demo presets (Rice, Chickpea, Cotton, Alert scenario), input validation tooltips, and responsive layout.
- [x] **Step 54**: Enhance result template `templates/result.html` with direct PDF download button, fertilizer dosage breakdown, and interactive probability charts.
- [x] **Step 55**: Create error templates `templates/error.html`, `templates/404.html`, and `templates/500.html` with graceful recovery links.
- [x] **Step 56**: Verify web routes, form submissions, and API endpoints using automated Flask test client. **[Commit Stage 8]**

## Stage 9: Comprehensive Automated Test Suite (Steps 57 – 61)
- [x] **Step 57**: Configure pytest fixtures, mock payloads, and shared test resources in `tests/conftest.py`.
- [x] **Step 58**: Implement regression tests across all core modules and advisory calculators.
- [x] **Step 59**: Implement integration tests for ML prediction pipeline and XAI explanations.
- [x] **Step 60**: Implement web view and REST API contract tests verifying JSON responses and status codes.
- [x] **Step 61**: Run pytest across entire test suite, verifying >88% test coverage and 100% test pass rate. **[Commit Stage 9]**

## Stage 10: Backward Compatibility, CLI Tooling, Documentation & Final Verification (Steps 62 – 67)
- [x] **Step 62**: Implement backward-compatible root files (`app.py`, `train_model.py`, `recommendation.py`, `explain.py`) seamlessly bridging to the new modular package.
- [x] **Step 63**: Create CLI management scripts (`scripts/train.py`, `scripts/evaluate.py`, `scripts/generate_demo_report.py`, `scripts/run_server.py`).
- [x] **Step 64**: Write comprehensive `README.md` with architecture diagram, quickstart guide, API documentation, and agronomic formula references.
- [x] **Step 65**: Verify legacy executions (`python train_model.py`, `python -c "import recommendation, explain"`, `python app.py`) run cleanly and without errors.
- [x] **Step 66**: Execute end-to-end full system integration test (Web UI, API, PDF generation, model inference).
- [x] **Step 67**: Final git commit to branch `sayan`, verifying working tree is completely clean and operational.
