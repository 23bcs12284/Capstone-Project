# Project Overview — Explainable AI Loan Approval Prediction System

## 1. Introduction

The **Explainable AI Loan Approval Prediction System** is an end-to-end machine learning
application that predicts loan approval outcomes while providing transparent, human-readable
explanations for every decision. The system is designed to bridge the gap between black-box
ML models and regulatory requirements for fairness and interpretability in financial services.

## 2. System Goals

| # | Goal | Description |
|---|------|-------------|
| 1 | **Predict Loan Approval** | Train and serve classification models that accurately predict whether a loan application will be approved or denied. |
| 2 | **Explain Predictions** | Generate per-prediction explanations using **SHAP** (SHapley Additive exPlanations) and **LIME** (Local Interpretable Model-agnostic Explanations). |
| 3 | **Audit Fairness** | Evaluate model outputs for demographic parity, equalized odds, and other fairness metrics using **Fairlearn**. |
| 4 | **Persist Data in SQL** | Store applications, predictions, explanations, and audit logs in a relational database via **SQLAlchemy**. |
| 5 | **Expose REST APIs** | Provide a secure **FastAPI** backend with JWT authentication, prediction, explanation, and analytics endpoints. |
| 6 | **Interactive Dashboard** | Deliver a rich **Streamlit** dashboard with real-time prediction, SHAP visualizations, and fairness reports. |

## 3. Key Features

- **Multi-model comparison** — Logistic Regression, XGBoost, LightGBM, CatBoost evaluated side-by-side.
- **Dynamic explainability** — SHAP and LIME explanations generated on-the-fly for any prediction.
- **Fairness auditing** — Automated bias detection across sensitive attributes (gender, race, age).
- **Prediction history** — Full audit trail of every prediction with associated explanations.
- **Role-based access** — JWT-secured endpoints with user registration and login.
- **Containerized deployment** — Docker and Docker Compose for reproducible environments.

## 4. Technology Stack

### Core & ML

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.12+ |
| ML Framework | scikit-learn | ≥ 1.4 |
| Gradient Boosting | XGBoost, LightGBM, CatBoost | Latest |
| Hyperparameter Tuning | GridSearchCV | scikit-learn built-in |

### Explainability & Fairness

| Component | Technology |
|-----------|------------|
| Global & Local Explanations | SHAP |
| Model-Agnostic Explanations | LIME |
| Fairness Metrics | Fairlearn |
| Visualization | Plotly, Matplotlib |

### Backend & Persistence

| Component | Technology |
|-----------|------------|
| REST API | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite (default) / PostgreSQL |
| Authentication | JWT (python-jose, passlib) |

### Frontend & Deployment

| Component | Technology |
|-----------|------------|
| Dashboard | Streamlit |
| Containerization | Docker, Docker Compose |
| Environment Management | venv / conda |

## 5. Project Structure (High-Level)

```
Capstone_project/
├── src/                    # Application source code
│   ├── data/               # Data generation & preprocessing
│   ├── models/             # Model training & evaluation
│   ├── explainability/     # SHAP & LIME modules
│   ├── fairness/           # Fairness auditing
│   ├── api/                # FastAPI backend
│   ├── dashboard/          # Streamlit frontend
│   └── database/           # SQLAlchemy models & session
├── data/                   # Raw and processed datasets
├── models/                 # Serialized model artifacts
├── docs/                   # Project documentation
├── tests/                  # Unit and integration tests
├── docker-compose.yml
└── requirements.txt
```

## 6. Target Audience

- **Data Scientists** seeking reproducible ML pipelines with built-in explainability.
- **ML Engineers** building production-grade prediction services.
- **Compliance Officers** requiring transparent, auditable AI decisions.
- **Students & Researchers** exploring XAI and fairness in financial ML.

## 7. License

This project is developed as a capstone project for academic purposes. All rights reserved.

---

> **Status:** ✅ All major milestones completed — see [PROGRESS.md](./PROGRESS.md) for details.
