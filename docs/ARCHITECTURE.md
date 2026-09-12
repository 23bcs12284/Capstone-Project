# Architecture — Explainable AI Loan Approval Prediction System

## 1. Overview

The system follows a **layered architecture** pattern, ensuring separation of concerns,
modularity, and independent testability of each layer. Data flows upward from ingestion
through prediction and explanation, ultimately reaching the end user via REST APIs or
the Streamlit dashboard.

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                     │
│              Streamlit Dashboard (UI)                   │
├─────────────────────────────────────────────────────────┤
│                      API LAYER                          │
│         FastAPI (REST Endpoints + JWT Auth)              │
├─────────────────────────────────────────────────────────┤
│                  PERSISTENCE LAYER                      │
│        SQLAlchemy ORM + SQLite / PostgreSQL              │
├──────────────────────┬──────────────────────────────────┤
│    FAIRNESS LAYER    │         XAI LAYER                │
│   Fairlearn Auditor  │   SHAP + LIME Explainers         │
├──────────────────────┴──────────────────────────────────┤
│                      ML LAYER                           │
│  LogReg · XGBoost · LightGBM · CatBoost · GridSearchCV  │
├─────────────────────────────────────────────────────────┤
│                     DATA LAYER                          │
│   Synthetic Generation · Validation · Preprocessing      │
└─────────────────────────────────────────────────────────┘
```

## 3. Layer Descriptions

### 3.1 Data Layer

| Responsibility | Details |
|----------------|---------|
| Dataset Generation | Synthetic loan dataset with configurable size and feature distributions |
| Validation | Schema validation, type checks, range enforcement via custom validators |
| Preprocessing | Missing-value imputation, outlier clipping, one-hot encoding, standard scaling |

### 3.2 ML Layer

| Responsibility | Details |
|----------------|---------|
| Model Training | Logistic Regression, XGBoost, LightGBM, CatBoost |
| Hyperparameter Tuning | GridSearchCV with stratified k-fold cross-validation |
| Evaluation | Accuracy, Precision, Recall, F1-Score, ROC AUC |
| Model Selection | Automated selection of the best model by ROC AUC score |
| Serialization | Joblib-based model persistence with versioned filenames |

### 3.3 XAI Layer (Explainability)

| Responsibility | Details |
|----------------|---------|
| SHAP Explanations | TreeExplainer / KernelExplainer based on model type; global and local feature importance |
| LIME Explanations | Tabular explainer for instance-level interpretable surrogate models |
| Visualization | SHAP summary plots, waterfall charts, force plots via Plotly and Matplotlib |

### 3.4 Fairness Layer

| Responsibility | Details |
|----------------|---------|
| Bias Detection | Demographic parity difference, equalized odds difference |
| Group Analysis | Performance breakdown by sensitive attributes (gender, race, age group) |
| Reporting | Structured fairness reports with pass/fail thresholds |

### 3.5 Persistence Layer

| Responsibility | Details |
|----------------|---------|
| ORM Models | SQLAlchemy declarative models for Users, Predictions, Explanations, etc. |
| Session Management | Scoped sessions with dependency injection in FastAPI |
| Migration Support | Schema creation via `Base.metadata.create_all()` |
| Database Backends | SQLite (default for development), PostgreSQL (production-ready) |

### 3.6 API Layer

| Responsibility | Details |
|----------------|---------|
| Authentication | JWT-based register/login with bcrypt password hashing |
| Prediction Endpoint | Accepts loan features, returns approval probability and decision |
| Explanation Endpoint | Returns SHAP/LIME explanations for a given prediction ID |
| Analytics & History | Aggregated statistics and per-user prediction history |
| Health Check | Liveness probe for monitoring and orchestration |

### 3.7 Presentation Layer

| Responsibility | Details |
|----------------|---------|
| Dashboard UI | Streamlit multi-page app with sidebar navigation |
| Prediction Form | Interactive input form for loan application features |
| Visualizations | SHAP waterfall plots, feature importance bar charts, fairness gauges |
| History View | Tabular display of past predictions with drill-down explanations |

## 4. Data Flow

```
User Input ──► Streamlit / API ──► Preprocessing ──► Model Inference
                                                          │
                                      ┌───────────────────┤
                                      ▼                   ▼
                                SHAP / LIME         Fairness Audit
                                      │                   │
                                      ▼                   ▼
                                  Database ◄──────────────┘
                                      │
                                      ▼
                              Response to User
```

## 5. Design Principles

- **Separation of Concerns** — Each layer has a single, well-defined responsibility.
- **Dependency Inversion** — Upper layers depend on abstractions, not concrete implementations.
- **Stateless API** — The FastAPI layer is stateless; all state lives in the database.
- **Pluggable Models** — New ML algorithms can be added without modifying the API or UI layers.
- **Explainability by Default** — Every prediction automatically triggers explanation generation.

## 6. Deployment Topology

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Streamlit  │────►│   FastAPI    │────►│   SQLite /   │
│   (Port 8501)│     │  (Port 8000) │     │  PostgreSQL  │
└──────────────┘     └──────────────┘     └──────────────┘
        └── Docker Compose orchestrates all services ──┘
```

---

> **See also:** [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) · [DATABASE.md](./DATABASE.md) · [API.md](./API.md)
