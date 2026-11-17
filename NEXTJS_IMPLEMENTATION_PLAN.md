# Next.js Frontend Migration: 70-Step Master Implementation Plan

**Project:** AgriSathi — Precision Agriculture Intelligent Decision Support Platform  
**Target:** Modern Full-Stack Decoupled Architecture (Next.js 14+ TypeScript Frontend + Flask Python Backend API)  
**Branch:** `sayan`  

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                 Next.js Frontend (Port 3000)                │
│  • App Router (Next.js 14+, React 18/19, TypeScript)        │
│  • Tailwind CSS v3/v4 + Lucide Icons + Recharts XAI         │
│  • Client-Side Form State, 1-Click Presets & Live Weather   │
│  • Interactive What-If Simulator & Dynamic SHAP Visualizer  │
│  • Historical Archive with Instant Search & PDF Direct DL   │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON REST API / CORS
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Flask Backend API (Port 5001)               │
│  • /api/v1/health       - Health & Model Readiness          │
│  • /api/v1/predict      - RF Top-3 + Full Advisory Engine   │
│  • /api/v1/what-if      - Local SHAP Perturbation Engine    │
│  • /api/v1/weather      - Open-Meteo Live Telemetry Client  │
│  • /api/v1/scenarios    - Verified Agro-Climatic Presets    │
│  • /api/v1/history      - SQLite Prediction Audit Log       │
│  • /api/v1/report       - ReportLab Official Agronomic PDF  │
└─────────────────────────────────────────────────────────────┘
```

---

## 70-Step Master Execution Checklist

### Phase 1: Backend API Preparation & CORS Configuration (Steps 1 – 6)
- [x] **Step 1**: Add CORS headers and preflight `OPTIONS` handling in `agrisathi/web/app.py` for headless frontend support.
- [x] **Step 2**: Add `FLASK_CORS_ORIGINS` configuration in `agrisathi/config.py`.
- [ ] **Step 3**: Verify backend API JSON serialization for all endpoints (`/api/v1/predict`, `/api/v1/weather`, `/api/v1/history`, `/api/v1/what-if`).
- [ ] **Step 4**: Write unit tests for CORS and API response schemas in `tests/test_api_cors.py`.
- [ ] **Step 5**: Run pytest suite to ensure zero regressions across all 161 existing tests.
- [ ] **Step 6**: Commit Phase 1 backend updates to branch `sayan`.

### Phase 2: Next.js Project Scaffolding & Setup (Steps 7 – 12)
- [ ] **Step 7**: Initialize Next.js 14+ app with TypeScript and Tailwind CSS in directory `frontend/`.
- [ ] **Step 8**: Configure `frontend/next.config.js` with API proxy rewrites to Flask (`http://127.0.0.1:5001`).
- [ ] **Step 9**: Configure Tailwind theme with AgriSathi brand tokens (emerald, forest greens, neutral slates).
- [ ] **Step 10**: Install core dependencies (`lucide-react`, `clsx`, `tailwind-merge`, `recharts` for SHAP charts).
- [ ] **Step 11**: Add NPM scripts and Makefile targets (`make run-frontend`, `make dev`) for unified developer experience.
- [ ] **Step 12**: Commit Phase 2 project scaffolding to branch `sayan`.

### Phase 3: TypeScript Types & Domain Interfaces (Steps 13 – 18)
- [ ] **Step 13**: Create `frontend/src/types/schemas.ts` defining all 22 farm input parameters with units, bounds, and defaults.
- [ ] **Step 14**: Define TypeScript interfaces for ML predictions (`TopCrop`, `ProbabilityItem`, `FeatureImportanceItem`).
- [ ] **Step 15**: Define TypeScript interfaces for agronomic advisory (`SoilHealthResult`, `IrrigationResult`, `FertilizerResult`, `HazardRiskResult`).
- [ ] **Step 16**: Define TypeScript interfaces for What-If simulation payloads and response deltas.
- [ ] **Step 17**: Define TypeScript interfaces for historical records and weather telemetry payloads.
- [ ] **Step 18**: Commit Phase 3 TypeScript interfaces to branch `sayan`.

### Phase 4: API Service Layer & HTTP Client (Steps 19 – 24)
- [ ] **Step 19**: Create modular HTTP client `frontend/src/lib/api.ts` with error handling, timeouts, and JSON parsing.
- [ ] **Step 20**: Implement `predictCrop(params)` service method in `frontend/src/lib/api.ts`.
- [ ] **Step 21**: Implement `fetchLiveWeather(location)` service method in `frontend/src/lib/api.ts`.
- [ ] **Step 22**: Implement `simulateWhatIf(baseline, perturbations)` service method in `frontend/src/lib/api.ts`.
- [ ] **Step 23**: Implement `fetchHistory()` and `fetchHistoryDetail(id)` service methods in `frontend/src/lib/api.ts`.
- [ ] **Step 24**: Commit Phase 4 API service layer to branch `sayan`.

### Phase 5: Reusable UI Component Library (Steps 25 – 32)
- [ ] **Step 25**: Create `frontend/src/components/ui/Button.tsx` supporting variants (`primary`, `outline`, `ghost`, `danger`) and loading state.
- [ ] **Step 26**: Create `frontend/src/components/ui/InputWithUnit.tsx` supporting embedded right-side unit badges and error styling.
- [ ] **Step 27**: Create `frontend/src/components/ui/Select.tsx` with customized dropdown styling and focus states.
- [ ] **Step 28**: Create `frontend/src/components/ui/Card.tsx` with header, title, icon bubble, and body wrappers.
- [ ] **Step 29**: Create `frontend/src/components/ui/Badge.tsx` for status indicators (High, Medium, Low, Alerts).
- [ ] **Step 30**: Create `frontend/src/components/ui/ProgressBar.tsx` for confidence meters and soil fertility scores.
- [ ] **Step 31**: Create `frontend/src/components/ui/Navbar.tsx` and `Footer.tsx` matching AgriSathi branding.
- [ ] **Step 32**: Commit Phase 5 UI component library to branch `sayan`.

### Phase 6: Farm Input Form — Section 1: Soil Parameters (Steps 33 – 38)
- [ ] **Step 33**: Create `frontend/src/components/form/SoilParametersSection.tsx` with 3x3 responsive grid.
- [ ] **Step 34**: Implement Nitrogen, Phosphorus, Potassium input fields with `mg/kg` units and client-side bounds check.
- [ ] **Step 35**: Implement Soil pH (`pH`), Soil Moisture (`%`), and Soil Type dropdown (`Loamy`, `Clay`, `Sandy`).
- [ ] **Step 36**: Implement Organic Carbon (`%`), Organic Matter (`%`), and Electrical Conductivity (`dS/m`).
- [ ] **Step 37**: Add automatic conversion helper between Organic Carbon (OC) and Organic Matter (OM = 1.724 * OC).
- [ ] **Step 38**: Commit Phase 6 Soil Parameters component to branch `sayan`.

### Phase 7: Farm Input Form — Section 2: Farm Scale & Location Context (Steps 39 – 43)
- [ ] **Step 39**: Create `frontend/src/components/form/FarmContextSection.tsx` with location input and season select.
- [ ] **Step 40**: Implement interactive Live Weather button with animated fetching state.
- [ ] **Step 41**: Add Live Telemetry Badge displaying synchronized temperature, humidity, rainfall, and forecast.
- [ ] **Step 42**: Implement Farm Area Size, Area Unit (`hectare`, `acre`), and Expected Rainfall inputs.
- [ ] **Step 43**: Commit Phase 7 Farm Context component to branch `sayan`.

### Phase 8: Farm Input Form — Section 3: Environmental Conditions (Steps 44 – 48)
- [ ] **Step 44**: Create `frontend/src/components/form/EnvironmentalSection.tsx`.
- [ ] **Step 45**: Implement Temperature (`°C`), Humidity (`%`), and Rainfall (`mm`) inputs.
- [ ] **Step 46**: Implement Sunlight Exposure (`hours`), Wind Speed (`m/s`), and CO2 Concentration (`ppm`) inputs.
- [ ] **Step 47**: Implement Frost Risk (`%`) input and telemetry info callout card to maintain 3x3 grid symmetry.
- [ ] **Step 48**: Commit Phase 8 Environmental Conditions component to branch `sayan`.

### Phase 9: Farm Input Form — Section 4: Farm Management & Scenario Presets (Steps 49 – 54)
- [ ] **Step 49**: Create `frontend/src/components/form/FarmManagementSection.tsx` with 8 parameters and decision matrix card.
- [ ] **Step 50**: Implement Irrigation Frequency, Crop Density, Pest Pressure, and Fertilizer Usage inputs.
- [ ] **Step 51**: Implement Growth Stage and Water Source Type dropdowns, Urban Proximity, and Water Usage Efficiency.
- [ ] **Step 52**: Create `frontend/src/components/form/ScenarioPresetsBar.tsx` with 1-click presets and Auto-Fill Baseline.
- [ ] **Step 53**: Create `frontend/src/components/form/PredictActionBar.tsx` with security badges and animated submit button.
- [ ] **Step 54**: Commit Phase 9 Farm Management & Presets components to branch `sayan`.

### Phase 10: Home Page Integration & State Management (Steps 55 – 59)
- [ ] **Step 55**: Create `frontend/src/app/page.tsx` integrating presets bar, form sections, and form validation state.
- [ ] **Step 56**: Implement client-side validation logic with instant error clearing on user keystroke.
- [ ] **Step 57**: Implement form submission handler calling `api.predictCrop` and storing result in state / sessionStorage.
- [ ] **Step 58**: Add loading overlay with animated agronomic inference progress states.
- [ ] **Step 59**: Commit Phase 10 Home Page integration to branch `sayan`.

### Phase 11: Result Dashboard — Crop Recommendation & Top-3 Suitability (Steps 60 – 63)
- [ ] **Step 60**: Create `frontend/src/app/result/page.tsx` displaying Top Crop hero card, confidence score, and suitability.
- [ ] **Step 61**: Implement Top-3 Crop Suitability Comparison Matrix table with attribute badges.
- [ ] **Step 62**: Implement 4 Agronomic Advisory Cards: Soil Health, Smart Irrigation, Fertilizer Schedule, and Risk Matrix.
- [ ] **Step 63**: Commit Phase 11 Result Dashboard to branch `sayan`.

### Phase 12: Explainable AI (SHAP Waterfall) & What-If Simulator (Steps 64 – 66)
- [ ] **Step 64**: Create `frontend/src/components/xai/ShapWaterfallChart.tsx` using Recharts for directional feature attributions.
- [ ] **Step 65**: Create `frontend/src/components/xai/WhatIfSimulator.tsx` allowing interactive perturbation testing with real-time API feedback.
- [ ] **Step 66**: Commit Phase 12 XAI & What-If Simulator to branch `sayan`.

### Phase 13: History Archive Page & PDF Export (Steps 67 – 68)
- [ ] **Step 67**: Create `frontend/src/app/history/page.tsx` with live search, crop filter pills, and direct PDF download links.
- [ ] **Step 68**: Commit Phase 13 History Archive & PDF integration to branch `sayan`.

### Phase 14: End-to-End Verification, Build & Integration (Steps 69 – 70)
- [ ] **Step 69**: Run Next.js production build (`npm run build`) and verify TypeScript compilation and bundle health.
- [ ] **Step 70**: Run full backend pytest suite (161 tests) and commit complete Next.js frontend solution to branch `sayan`.
