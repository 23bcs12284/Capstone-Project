# Roadmap — Explainable AI Loan Approval Prediction System

## Overview

This document outlines the seven development phases of the project. All phases have been
**successfully completed** as of 2026-07-18.

---

## Phase 1: Project Foundation ✅

**Objective:** Establish the project skeleton, tooling, and development environment.

- [x] Initialize repository structure with `src/`, `data/`, `models/`, `docs/`, `tests/`
- [x] Create `requirements.txt` with all dependencies
- [x] Configure `pyproject.toml` and linting tools
- [x] Set up virtual environment with Python 3.12+
- [x] Write initial `README.md` and documentation templates
- [x] Configure Docker and Docker Compose manifests

## Phase 2: Data Engineering ✅

**Objective:** Build the data generation and preprocessing pipeline.

- [x] Design synthetic loan dataset schema (15+ features)
- [x] Implement configurable dataset generator with realistic distributions
- [x] Build data validation module with schema enforcement
- [x] Implement missing-value imputation (median/mode strategies)
- [x] Add outlier detection and clipping logic
- [x] Create one-hot encoding and standard scaling transformers
- [x] Generate train/test split with stratification

## Phase 3: Model Development ✅

**Objective:** Train, tune, and evaluate multiple classification models.

- [x] Implement Logistic Regression baseline
- [x] Train XGBoost classifier with hyperparameter grid
- [x] Train LightGBM classifier with hyperparameter grid
- [x] Train CatBoost classifier with hyperparameter grid
- [x] Perform GridSearchCV with stratified 5-fold cross-validation
- [x] Evaluate all models on accuracy, precision, recall, F1, ROC AUC
- [x] Select best model (Logistic Regression — ROC AUC 0.9121)
- [x] Serialize best model and preprocessing pipeline with Joblib

## Phase 4: Explainability Integration ✅

**Objective:** Add SHAP and LIME explanation capabilities.

- [x] Implement dynamic SHAP explainer (auto-selects TreeExplainer or KernelExplainer)
- [x] Generate SHAP global feature importance rankings
- [x] Generate SHAP local (per-instance) explanations
- [x] Implement LIME tabular explainer for individual predictions
- [x] Create SHAP waterfall and summary plot generators
- [x] Store explanations in structured format for persistence

## Phase 5: Fairness Auditing ✅

**Objective:** Detect and report model bias across sensitive attributes.

- [x] Build custom fairness auditor module
- [x] Compute demographic parity difference per group
- [x] Compute equalized odds difference per group
- [x] Generate group-level performance breakdowns
- [x] Implement configurable fairness thresholds with pass/fail reporting
- [x] Integrate fairness reports into the API and dashboard

## Phase 6: Backend & Persistence ✅

**Objective:** Build the FastAPI backend, database layer, and authentication.

- [x] Define SQLAlchemy ORM models for all 6 tables
- [x] Implement database session management with dependency injection
- [x] Build JWT authentication with registration and login endpoints
- [x] Create `/predict` endpoint with input validation
- [x] Create `/explain/{id}` endpoint for SHAP/LIME retrieval
- [x] Create `/analytics` and `/history` endpoints
- [x] Create `/model/metadata` and `/health` endpoints
- [x] Add comprehensive error handling and input sanitization

## Phase 7: Dashboard & Deployment ✅

**Objective:** Deliver the Streamlit dashboard and containerized deployment.

- [x] Build multi-page Streamlit application
- [x] Implement interactive loan application prediction form
- [x] Add SHAP visualization panels (waterfall, bar, summary)
- [x] Add fairness audit display with metric gauges
- [x] Implement prediction history table with drill-down
- [x] Integrate dashboard with FastAPI backend via HTTP client
- [x] Finalize Docker Compose for multi-service orchestration
- [x] Write comprehensive project documentation

---

## Summary

| Phase | Title | Status |
|-------|-------|--------|
| 1 | Project Foundation | ✅ Complete |
| 2 | Data Engineering | ✅ Complete |
| 3 | Model Development | ✅ Complete |
| 4 | Explainability Integration | ✅ Complete |
| 5 | Fairness Auditing | ✅ Complete |
| 6 | Backend & Persistence | ✅ Complete |
| 7 | Dashboard & Deployment | ✅ Complete |

> **All 7 phases completed.** See [PROGRESS.md](./PROGRESS.md) for detailed status and metrics.
