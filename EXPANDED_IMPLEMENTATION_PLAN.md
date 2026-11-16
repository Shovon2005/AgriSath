# Explainable AI-Driven Precision Agriculture: 55-Step Master Implementation Plan

**Project Title:** Explainable AI-Driven Intelligent Decision Support Framework for Precision Agriculture  
**Branch:** `sayan`

---

## Executive Architectural Summary
This master plan delivers an integrated, scientifically grounded decision-support system answering four core agronomic questions:
1. **What is the current condition of the soil?** (NPK analysis, pH, Electrical Conductivity [EC], Organic Carbon [OC], fertility classification [Low/Medium/High], numerical health score, and improvement suggestions)
2. **Which crop is most suitable for this soil and climate?** (Trained ML model, Top-3 crop recommendations, prediction confidences, multi-attribute suitability comparison, and selection reasoning)
3. **How much water does the crop need, and when should it be irrigated?** (Crop evapotranspiration $ET_c$, next irrigation time window, total farm water requirement in litres based on farm area, and suppression for expected rainfall)
4. **Which fertilizer should be used, and in what quantity?** (Deficiency/excess identification, Urea, DAP/SSP, and MOP dosages in kg/ha and total kg/bags for farm area, 3-split schedule, and organic alternatives)

Plus:
- **Module 5: Explainable AI (XAI)** (SHAP TreeExplainer feature importance, visual waterfall plot, directional positive/negative contributions, natural language explanation, and interactive What-If scenario analysis)
- **Module 6: Integrated Agricultural Dashboard** (Unified web interface, Open-Meteo live weather autofill, historical report storage in SQLite, and downloadable executive PDF report)

---

## The 55 Sequential Steps

### Phase 1: Core Schemas, Extended Parameters & Validation (Steps 1 – 7)
- [x] **Step 1**: Define extended domain parameters (`farm_area`, `farm_area_unit`, `electrical_conductivity`, `organic_carbon`, `location`, `season`, `expected_rainfall_24h`) in `agrisathi/core/schemas.py`.
- [x] **Step 2**: Add `Season` enum (`Kharif`, `Rabi`, `Zaid`, `Whole Year`) and bidirectional normalization helpers in `agrisathi/core/schemas.py`.
- [x] **Step 3**: Extend `agrisathi/core/validator.py` with boundary checks and safe fallbacks for new parameters, maintaining 100% backward compatibility for ML inference.
- [x] **Step 4**: Implement unit tests `tests/test_extended_schemas.py` for all new fields and validation rules.
- [x] **Step 5**: Run test suite and commit Phase 1 schema changes.
- [x] **Step 6**: Update `agrisathi/config.py` with Open-Meteo weather API endpoints and SQLite history database path.
- [x] **Step 7**: Commit configuration updates.

### Phase 2: Enhanced Module 1 — Soil Fertility & Nutrient Engine (Steps 8 – 14)
- [x] **Step 8**: Implement composite soil fertility classification (`Low`, `Medium`, `High`) based on N, P, K, and Organic Carbon in `agrisathi/advisory/soil.py`.
- [x] **Step 9**: Add Electrical Conductivity (EC) assessment and salinity hazard rating in `agrisathi/advisory/soil.py`.
- [x] **Step 10**: Implement Organic Carbon (OC) evaluation with automatic conversion to/from Organic Matter (`OM = 1.724 * OC`).
- [x] **Step 11**: Implement comprehensive nutrient deficiency and excess diagnosis for all macro-nutrients and physical soil parameters.
- [x] **Step 12**: Generate actionable soil improvement suggestions (liming, gypsum for salinity, green manure, composting).
- [x] **Step 13**: Write unit tests in `tests/test_soil_assessment.py` for Low/Medium/High fertility and EC/OC diagnostics.
- [x] **Step 14**: Run test suite and commit Phase 2 soil engine enhancements.

### Phase 3: Enhanced Module 2 — Crop Recommendation & Top-3 Suitability Comparison (Steps 15 – 21)
- [x] **Step 15**: Enhance `CropPredictor` in `agrisathi/ml/predictor.py` to structure Top 3 recommendations (Rank 1, 2, 3) with confidences.
- [x] **Step 16**: Enrich `data/crop_agronomic_profiles.json` with season compatibility, growth duration (days), and yield potential benchmarks.
- [x] **Step 17**: Implement `agrisathi/advisory/comparison.py` generating a multi-attribute Suitability Comparison Matrix for top-3 crops.
- [x] **Step 18**: Add Season filtering and Location agro-climatic alignment scoring in `agrisathi/advisory/comparison.py`.
- [x] **Step 19**: Integrate Top-3 comparison matrix into unified advisory orchestrator `agrisathi/advisory/engine.py`.
- [x] **Step 20**: Write unit tests in `tests/test_crop_comparison.py` verifying top-3 ranking and comparison attributes.
- [x] **Step 21**: Run test suite and commit Phase 3 crop recommendation enhancements.

### Phase 4: Enhanced Module 3 — Smart Irrigation Engine with Water Volume & Weather (Steps 22 – 28)
- [ ] **Step 22**: Implement daily crop water requirement ($ET_c = K_c \times ET_0$) in mm/day based on climate and growth stage in `agrisathi/advisory/irrigation.py`.
- [ ] **Step 23**: Implement irrigation requirement status determination (`Yes - Immediate`, `Yes - Within 48 Hours`, `No - Adequate`, `Warning - Saturated`).
- [ ] **Step 24**: Implement next irrigation timing recommendation window based on soil moisture depletion rate.
- [ ] **Step 25**: Implement farm-area water volume calculation in Litres ($10,000 \times \text{ha} \times \text{mm}$) and cubic meters.
- [ ] **Step 26**: Implement expected rainfall integration to suppress or postpone irrigation when rain is forecast.
- [ ] **Step 27**: Write unit tests in `tests/test_irrigation_engine.py` for ETc calculations, water volume in litres, and rainfall suppression.
- [ ] **Step 28**: Run test suite and commit Phase 4 irrigation engine enhancements.

### Phase 5: Enhanced Module 4 — AI-Based Fertilizer Engine with Farm Sizing & Organics (Steps 29 – 35)
- [ ] **Step 29**: Update `agrisathi/advisory/fertilizer.py` to compute both kg/ha AND total quantity (kg and 50-kg commercial bags) for specified farm size.
- [ ] **Step 30**: Implement dual phosphate source recommendation: DAP (18-46-0) and Single Super Phosphate SSP (0-16-0) options.
- [ ] **Step 31**: Implement organic alternative calculator: Farm Yard Manure (FYM), Vermicompost, Compost, and Biofertilizers (Rhizobium, Azotobacter, PSB).
- [ ] **Step 32**: Implement structured 3-stage application schedule (Basal at sowing, Vegetative top-dressing, Flowering/Panicle initiation).
- [ ] **Step 33**: Add warnings for nutrient excesses and antagonism risks (e.g., high N causing lodging, excess P blocking Zn/Fe).
- [ ] **Step 34**: Write unit tests in `tests/test_fertilizer_engine.py` for farm size scaling, 50kg bags, SSP alternatives, and organic doses.
- [ ] **Step 35**: Run test suite and commit Phase 5 fertilizer engine enhancements.

### Phase 6: Enhanced Module 5 — Explainable AI (SHAP Waterfall, Contributions & What-If) (Steps 36 – 42)
- [ ] **Step 36**: Implement SHAP Waterfall data generator in `agrisathi/ml/explain.py` calculating base value $E[f(x)]$, positive/negative steps, and final prediction value $f(x)$.
- [ ] **Step 37**: Implement SVG/HTML Waterfall Plot visualizer module that renders an interactive, responsive waterfall graph without external binary dependencies.
- [ ] **Step 38**: Implement natural-language explanation synthesis summarizing why the crop was selected in simple, farmer-friendly language.
- [ ] **Step 39**: Implement interactive What-If Analysis engine in `agrisathi/ml/whatif.py` allowing dynamic parameter sensitivity simulation.
- [ ] **Step 40**: Add What-If REST API endpoint `/api/v1/what-if` in `agrisathi/web/routes/api.py`.
- [ ] **Step 41**: Write unit tests in `tests/test_whatif_xai.py` testing SHAP waterfall values, natural language synthesis, and what-if simulations.
- [ ] **Step 42**: Run test suite and commit Phase 6 XAI enhancements.

### Phase 7: Real-Time Weather Integration & Historical Prediction Persistence (Steps 43 – 48)
- [ ] **Step 43**: Implement Weather API client in `agrisathi/utils/weather.py` using Open-Meteo (temperature, humidity, rainfall, 48h forecast with offline fallback).
- [ ] **Step 44**: Add API route `/api/v1/weather` for client-side location autofill in `agrisathi/web/routes/api.py`.
- [ ] **Step 45**: Implement lightweight historical predictions repository in `agrisathi/data/history.py` using SQLite database `data/history.db`.
- [ ] **Step 46**: Add `/history` and `/api/v1/history` endpoints for viewing, searching, and reloading past predictions.
- [ ] **Step 47**: Write unit tests in `tests/test_weather_and_history.py` testing weather fetching and history CRUD.
- [ ] **Step 48**: Run test suite and commit Phase 7 weather and persistence integration.

### Phase 8: Module 6 — Integrated Dashboard UI, PDF Report & System Verification (Steps 49 – 55)
- [ ] **Step 49**: Update `templates/index.html` with new inputs (EC, OC, Farm Area, Location, Season, Weather Autofill button).
- [ ] **Step 50**: Update `templates/result.html` to integrate all 6 modules: Soil Fertility (Low/Med/High), Top-3 Comparison Matrix, Water in Litres & Schedule, Fertilizer in Bags & Organics, SHAP Waterfall Plot, and What-If Analysis Simulator.
- [ ] **Step 51**: Create `templates/history.html` for viewing past farm reports and one-click reload.
- [ ] **Step 52**: Enhance PDF report generator in `agrisathi/reports/pdf_generator.py` to include EC, OC, fertility rating, farm area, water in litres, fertilizer bags, organic alternatives, top 3 comparison, and SHAP narrative.
- [ ] **Step 53**: Write end-to-end integration tests in `tests/test_full_integrated_system.py` verifying full pipeline from weather to PDF.
- [ ] **Step 54**: Run complete pytest suite across all tests, ensuring 100% pass rate.
- [ ] **Step 55**: Final git commit to branch `sayan`, verifying clean working tree, updated documentation, and zero regressions.
