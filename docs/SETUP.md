# Setup Guide — Explainable AI Loan Approval Prediction System

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.12 or higher |
| pip | Latest |
| Git | 2.30+ |
| Docker *(optional)* | 24.0+ |
| Docker Compose *(optional)* | 2.20+ |

---

## 1. Clone the Repository

```bash
git clone <repository-url>
cd Capstone_project
```

## 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

## 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Key Dependencies

| Package | Purpose |
|---------|---------|
| fastapi, uvicorn | REST API server |
| scikit-learn | ML pipeline and Logistic Regression |
| xgboost | XGBoost classifier |
| lightgbm | LightGBM classifier |
| catboost | CatBoost classifier |
| shap | SHAP explanations |
| lime | LIME explanations |
| fairlearn | Fairness metrics |
| plotly, matplotlib | Visualizations |
| streamlit | Dashboard UI |
| sqlalchemy | Database ORM |
| python-jose, passlib | JWT authentication |
| joblib | Model serialization |

---

## 4. Generate Synthetic Dataset

```bash
python -m src.data.generate_dataset
```

This creates the loan dataset in the `data/` directory with configurable parameters:

```bash
# Custom size and seed
python -m src.data.generate_dataset --samples 10000 --seed 42
```

**Output:** `data/loan_dataset.csv`

## 5. Run the ML Pipeline

```bash
python -m src.models.train_pipeline
```

This command executes the full pipeline:

1. Loads and validates the dataset
2. Applies preprocessing (imputation, clipping, encoding, scaling)
3. Splits data into train/test sets (80/20 stratified)
4. Trains all four models with GridSearchCV
5. Evaluates and compares model performance
6. Selects the best model by ROC AUC
7. Serializes the model and pipeline to `models/`

**Output:** `models/best_model.joblib`, `models/preprocessor.joblib`

## 6. Start the FastAPI Backend

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | API root |
| `http://localhost:8000/docs` | Swagger UI (interactive docs) |
| `http://localhost:8000/redoc` | ReDoc documentation |

## 7. Launch the Streamlit Dashboard

Open a **new terminal** (keep the API server running):

```bash
source venv/bin/activate
streamlit run src/dashboard/app.py --server.port 8501
```

The dashboard will be available at: `http://localhost:8501`

---

## 8. Docker Deployment (Optional)

### Build and Run All Services

```bash
docker-compose up --build
```

### Services

| Service | Port | URL |
|---------|------|-----|
| FastAPI Backend | 8000 | `http://localhost:8000` |
| Streamlit Dashboard | 8501 | `http://localhost:8501` |

### Stop Services

```bash
docker-compose down
```

### Rebuild After Changes

```bash
docker-compose up --build --force-recreate
```

---

## 9. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./loan_app.db` | Database connection string |
| `SECRET_KEY` | *(generated)* | JWT signing secret |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiry duration |
| `MODEL_PATH` | `models/best_model.joblib` | Path to serialized model |

Set environment variables in a `.env` file at the project root or export them directly:

```bash
export DATABASE_URL="sqlite:///./loan_app.db"
export SECRET_KEY="your-secret-key-here"
```

---

## 10. Verify Installation

```bash
# Check Python version
python --version

# Run health check (after starting the API)
curl http://localhost:8000/health

# Run tests
pytest tests/ -v
```

Expected health check response:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure virtual environment is activated and dependencies are installed |
| Port already in use | Change the port: `--port 8001` for API or `--server.port 8502` for Streamlit |
| Database errors | Delete `loan_app.db` and restart — tables are auto-created |
| Model not found | Run the ML pipeline first (Step 5) before starting the API |
| Docker build fails | Ensure Docker daemon is running and you have sufficient disk space |

---

> **See also:** [API.md](./API.md) · [DATABASE.md](./DATABASE.md) · [ML_PIPELINE.md](./ML_PIPELINE.md)
