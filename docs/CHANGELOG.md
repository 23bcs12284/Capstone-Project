# Changelog — Explainable AI Loan Approval Prediction System

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.0.0] — 2026-07-18

### 🎉 Initial Release

This is the first production-ready release of the Explainable AI Loan Approval
Prediction System, encompassing all 7 development phases.

### Added

#### Data Engineering
- Synthetic loan dataset generator with configurable size and feature distributions
- Data validation module with schema enforcement and type checking
- Preprocessing pipeline: imputation, outlier clipping, one-hot encoding, standard scaling
- Stratified 80/20 train/test split utility

#### Model Development
- Logistic Regression classifier (selected as best model — ROC AUC 0.9121)
- XGBoost gradient boosting classifier
- LightGBM gradient boosting classifier
- CatBoost gradient boosting classifier
- GridSearchCV hyperparameter tuning with stratified 5-fold cross-validation
- Automated model comparison and selection by ROC AUC
- Joblib-based model serialization and versioning

#### Explainability
- Dynamic SHAP explainer with automatic backend selection (TreeExplainer / KernelExplainer)
- SHAP global feature importance analysis
- SHAP local per-prediction explanations (waterfall and force plots)
- LIME tabular explainer for instance-level interpretability
- Plotly and Matplotlib visualization generators

#### Fairness Auditing
- Custom fairness auditor module with pluggable metrics
- Demographic parity difference computation
- Equalized odds difference computation
- Group-level performance breakdowns by gender, race, and age
- Configurable fairness thresholds with structured pass/fail reporting

#### Backend & API
- FastAPI REST application with 8 endpoints
- JWT authentication (registration and login) with bcrypt password hashing
- `/predict` endpoint with input validation and preprocessing
- `/explain/{id}` endpoint for SHAP and LIME explanation retrieval
- `/analytics` endpoint for aggregated prediction statistics
- `/history` endpoint for user prediction history
- `/model/metadata` endpoint for active model information
- `/health` liveness probe endpoint

#### Persistence
- SQLAlchemy ORM with 6 tables: Users, LoanApplications, Predictions, Explanations, ModelVersions, AuditLogs
- Database session management with FastAPI dependency injection
- SQLite as default backend with PostgreSQL compatibility

#### Dashboard
- Streamlit multi-page application with sidebar navigation
- Interactive loan application prediction form
- SHAP waterfall, bar, and summary plot panels
- Fairness audit display with metric cards and charts
- Prediction history table with drill-down explanations

#### Infrastructure
- Docker and Docker Compose configuration for all services
- `requirements.txt` with pinned dependency versions
- Comprehensive documentation suite (11 files)

### Security
- Password hashing via bcrypt (passlib)
- JWT token-based API authentication
- Input sanitization on all endpoints

---

## Version History

| Version | Date | Summary |
|---------|------|---------|
| v1.0.0 | 2026-07-18 | Initial release — full system with ML, XAI, fairness, API, and dashboard |

---

> **Upcoming:** See [TODO.md](./TODO.md) for planned post-release improvements.
