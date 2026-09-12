# 💳 Explainable AI Loan Approval Prediction & Decision Support System

> A production-ready, research-grade machine learning decision support system that predicts loan approvals, compares 9 ML classifiers across 3 distinct financial datasets, explains every prediction using SHAP, LIME, and counterfactual analysis, audits fairness across demographic groups, and delivers an interactive 10-page glassmorphism Single Page Application (SPA) dashboard.

---

## 🎯 Project Overview

This system demonstrates end-to-end machine learning engineering for financial credit risk, featuring:

- **9 Classification Algorithms** compared via cross-validated grid search (Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost, Support Vector Machine, Extra Trees)
- **Multi-Dataset Training Engine** — 3 datasets with distinct schemas (`General Loan Dataset`, `Home Loan Dataset`, `Personal Loan Dataset`)
- **Model Registry & Experiment Tracking** — Automatic model versioning, cross-validation logging, timing benchmarks, and best-model recommendations
- **Triple Explainability System** — SHAP (waterfall, beeswarm, feature directions), LIME local explanations, and Counterfactual Recommendations for rejected applicants
- **Model Calibration & Diagnostic Analysis** — Brier scores, calibration curves, ROC curves, Precision-Recall curves, and confusion matrix analytics
- **Fairness Auditing & Mitigation** — Demographic Parity, Equal Opportunity, and Average Odds metrics across Gender, Age Group, and Race
- **FastAPI REST Backend** — ~20 API endpoints serving datasets, models, evaluations, explainability, fairness, and prediction services
- **10-Page Modern SPA Dashboard** — Collapsible sidebar navigation, real-time Chart.js charts, interactive policy threshold sliders, and dark glassmorphism design system

---

## 🏗️ Architecture

```
Capstone_project/
├── config/              # Settings, dataset configs & hyperparameter grids
├── preprocessing/       # Multi-schema data cleaner & schema validator
├── feature_engineering/ # StandardScaler + OneHotEncoder FeatureTransformer
├── models/              # Classifier implementations & ModelRegistry
├── training/            # Trainer pipeline & JSON ExperimentTracker
├── evaluation/          # Metrics, calibration curves, ROC/PR data generators
├── explainability/      # SHAP, LIME, and Counterfactual explainers
├── fairness/            # Bias auditor & mitigation algorithms
├── database/            # SQLAlchemy ORM database models and audit logger
├── backend/             # FastAPI app, router, Pydantic schemas, JWT auth
├── dashboard/           # Single-Page Application (HTML, CSS, JS 10-page modules)
├── scripts/             # Synthetic dataset generator & pipeline orchestrator
├── artifacts/           # Model registry, experiment logs, evaluation JSONs
└── models_saved/        # Pickled models, scalers, and cleaner pipelines per dataset
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- macOS: `brew install libomp` (required for OpenMP XGBoost/LightGBM)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Multi-Dataset Suite & Train All Models

```bash
# Generate 3 distinct loan datasets
python3 scripts/generate_datasets.py

# Run end-to-end multi-dataset pipeline (trains 9 models x 3 datasets)
python3 scripts/run_pipeline.py
```

This will:
- Generate 3 synthetic financial datasets with realistic feature correlations
- Train and tune 9 ML models across all datasets
- Log all 27+ experiment runs into `artifacts/experiments/all_experiments.json`
- Register all models into `artifacts/model_registry.json`
- Compute and save evaluation curves, SHAP importance maps, and fairness audits

### 3. Launch Full-Stack Decision Support System

```bash
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser at: `http://localhost:8000` to access the full interactive decision platform!

API documentation is accessible at: `http://localhost:8000/docs`

---

## 📊 Dashboard Modules (10 Pages)

1. **🏠 Dashboard** — Executive KPI summary (Models, Datasets, Best Accuracy, Best ROC-AUC), top ROC-AUC model rankings, global feature importance chart, and recent experiments.
2. **🔮 Loan Prediction** — Dynamic prediction form adapting to the selected dataset's schema, policy decision threshold slider (0.1–0.9), probability gauge, risk level assessment (LOW/MEDIUM/HIGH), and positive/negative factor attribution.
3. **👤 Applicant Analysis** — Comprehensive applicant profile cards, SHAP waterfall impact visualization, decision explanation text, and counterfactual recourse steps.
4. **📊 Model Comparison** — Side-by-side performance table highlighting top metrics, ROC-AUC vs F1 bar charts, multi-model radar chart, training time benchmarks, and automated model recommendation.
5. **🧠 Explainability** — SHAP mean absolute value ranking, feature impact direction arrows (↑ increases approval / ↓ decreases approval), and model interpretability insights.
6. **📁 Datasets** — Multi-dataset cards, column schema details, approval rate breakdowns, missing value metrics, and interactive target distribution charts.
7. **🧪 Experiments** — Full experiment history table, dataset filters, total run counts, and accuracy/ROC-AUC trendlines over training runs.
8. **⚖ Fairness** — Protected group selection (Gender, Age Group), Demographic Parity Ratio, Equal Opportunity Difference, Average Odds Difference, group selection rates, and bias mitigation guidance.
9. **📈 Model Evaluation** — Interactive model evaluation diagnostic hub featuring Confusion Matrix heatmaps, ROC curves, Precision-Recall curves, and Calibration curves with Brier scores.
10. **⚙ Model Management** — Model registry viewer, hyperparameter inspection, active model tagging, file path tracking, and deployment action controls.

---

## 🔐 Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/datasets` | List all datasets with row count, feature count, approval rate |
| GET | `/api/datasets/{dataset_id}` | Detailed dataset schema and feature statistics |
| GET | `/api/models` | List all registered models across all datasets |
| GET | `/api/models/compare?dataset_id=X` | Side-by-side metric comparison table for a dataset |
| GET | `/api/models/recommend?dataset_id=X` | Best model recommendation engine |
| GET | `/api/evaluation/{dataset_id}/{model_name}/roc` | ROC curve data points |
| GET | `/api/evaluation/{dataset_id}/{model_name}/calibration` | Calibration curve & Brier score |
| GET | `/api/explainability/{dataset_id}/{model_name}/feature-importance` | Global SHAP feature importance |
| GET | `/api/fairness/{dataset_id}/{model_name}` | Fairness audit results for protected attributes |
| POST | `/api/predict` | Run loan prediction with SHAP factors & counterfactuals |

---

## 🛡️ Disclaimer

This application is designed as a decision-support, explainability research, and educational platform. It does not issue legally binding financial credit decisions.rce code

---

## 📄 License

This project is developed as a capstone research project.

---

## 👥 Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.
