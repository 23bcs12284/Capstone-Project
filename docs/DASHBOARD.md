# Streamlit Dashboard Documentation

## Overview

The Explainable AI Loan Approval Prediction System includes a comprehensive Streamlit dashboard with 5 tabs, custom CSS styling, and support for both connected (API-backed) and standalone (local model) modes.

---

## Dashboard Tabs

### Tab 1: Prediction Input

**Purpose:** Accept loan application details and display real-time approval predictions.

**Features:**
- Input form with 15 fields (8 numeric sliders, 7 categorical dropdowns)
- Real-time validation with error messages for out-of-range values
- Prediction confidence gauge (0-100%) with color-coded thresholds
- Decision output: "Approved" (green) or "Denied" (red) with probability score
- "Explain This Decision" button linking to Tab 2

### Tab 2: SHAP Explanations

**Purpose:** Display SHAP-based explanations for the most recent prediction.

**Features:**
- Waterfall plot showing top 15 feature contributions
- Force plot rendered as interactive HTML component
- Feature importance bar chart (global view)
- Toggle between local (single prediction) and global (all predictions) views
- Download SHAP explanation as PNG or HTML

### Tab 3: LIME Explanations

**Purpose:** Provide alternative LIME-based explanations for comparison with SHAP.

**Features:**
- LIME bar chart showing feature conditions and contribution weights
- Side-by-side comparison view with SHAP explanations
- Embedded interactive HTML explanation via `st.components.v1.html()`
- Prediction probability breakdown per class

### Tab 4: Fairness Analysis

**Purpose:** Display fairness metrics and bias analysis across protected attributes.

**Features:**
- Demographic Parity and Equal Opportunity metrics per group
- Interactive bar charts comparing approval rates across gender, age, race
- Before/after mitigation comparison tables
- Fairness threshold indicators (green: fair, yellow: marginal, red: biased)
- Downloadable fairness report (CSV + HTML)

### Tab 5: Model Performance

**Purpose:** Show model evaluation metrics and comparison results.

**Features:**
- Confusion matrix heatmap
- ROC curve with AUC annotation
- Precision-recall curve
- Metrics summary table (accuracy, precision, recall, F1, ROC AUC)
- Model comparison chart (all 7 models if available)

---

## Custom CSS Styling

The dashboard uses injected custom CSS for a polished, professional appearance:

```python
def inject_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Prediction result styling */
    .prediction-approved {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 12px;
        padding: 24px;
        color: white;
        font-size: 1.5rem;
        text-align: center;
    }
    .prediction-denied {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border-radius: 12px;
        padding: 24px;
        color: white;
        font-size: 1.5rem;
        text-align: center;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        color: white;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)
```

---

## Operating Modes

### Connected Mode (Default)

In connected mode, the dashboard communicates with the FastAPI backend for predictions and explanations:

```python
# config/dashboard_config.yaml
mode: connected
api:
  base_url: http://localhost:8000
  endpoints:
    predict: /api/v1/predict
    explain_shap: /api/v1/explain/shap
    explain_lime: /api/v1/explain/lime
    fairness: /api/v1/fairness/metrics
  timeout: 30
```

```python
import requests

def get_prediction_connected(input_data):
    response = requests.post(
        f"{API_BASE_URL}/api/v1/predict",
        json=input_data,
        timeout=30
    )
    return response.json()
```

### Standalone Mode

In standalone mode, the dashboard loads models and preprocessors directly, requiring no backend API:

```python
# config/dashboard_config.yaml
mode: standalone
model:
  path: models_saved/logistic_regression.pkl
  preprocessor_path: artifacts/preprocessor.pkl
  feature_names_path: artifacts/feature_names.json
```

```python
import joblib

def get_prediction_standalone(input_data):
    preprocessor = joblib.load('artifacts/preprocessor.pkl')
    model = joblib.load('models_saved/logistic_regression.pkl')
    
    X = preprocessor.transform(pd.DataFrame([input_data]))
    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0]
    
    return {
        'prediction': int(prediction),
        'probability': float(probability[1]),
        'label': 'Approved' if prediction == 1 else 'Denied'
    }
```

### Mode Selection

```python
# dashboard/app.py
import yaml

with open('config/dashboard_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

if config['mode'] == 'connected':
    from dashboard.api_client import get_prediction_connected as predict
else:
    from dashboard.local_model import get_prediction_standalone as predict
```

---

## Running the Dashboard

```bash
# Connected mode (requires API server running)
streamlit run dashboard/app.py -- --mode connected

# Standalone mode
streamlit run dashboard/app.py -- --mode standalone

# With custom port
streamlit run dashboard/app.py --server.port 8501
```

---

## Artifacts

- `dashboard/app.py` — Main dashboard entry point
- `dashboard/components/` — Reusable Streamlit components
- `dashboard/styles/custom.css` — External CSS (loaded dynamically)
- `config/dashboard_config.yaml` — Dashboard configuration

---

## References

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Components](https://docs.streamlit.io/library/components)
