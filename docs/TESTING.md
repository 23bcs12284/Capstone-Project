# Testing Documentation

## Overview

The Explainable AI Loan Approval Prediction System includes a comprehensive test suite with 4 test files covering preprocessing, model evaluation, fairness, and API endpoints. All tests use `pytest` with coverage reporting.

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures and test data
├── test_preprocessing.py       # Preprocessing pipeline tests
├── test_models.py              # Model training and evaluation tests
├── test_fairness.py            # Fairness metrics and mitigation tests
└── test_api.py                 # API endpoint integration tests
```

---

## Test File 1: `test_preprocessing.py`

**Scope:** Validates the feature engineering pipeline, including imputation, scaling, encoding, and derived features.

### Test Cases

| Test Name                           | Description                                                    |
|-------------------------------------|----------------------------------------------------------------|
| `test_numeric_imputation`           | Verifies median imputation fills missing numeric values        |
| `test_categorical_imputation`       | Verifies mode imputation fills missing categorical values      |
| `test_standard_scaler_output`       | Checks scaled features have mean ≈ 0, std ≈ 1                 |
| `test_onehot_encoder_shape`         | Confirms output has 16 encoded columns (drop='first')         |
| `test_unknown_category_handling`    | Ensures unseen categories produce all-zero columns             |
| `test_derived_features`             | Validates income_loan_ratio, total_income, log_loan_amount     |
| `test_pipeline_output_shape`        | Confirms final output shape is (n_samples, 28)                 |
| `test_preprocessor_persistence`     | Tests save/load round-trip with joblib                         |
| `test_no_data_leakage`             | Ensures scaler is fit only on training data                    |

### Example

```python
def test_pipeline_output_shape(preprocessor, sample_data):
    """Verify that the preprocessing pipeline produces 28 features."""
    X_transformed = preprocessor.transform(sample_data)
    assert X_transformed.shape[1] == 28, (
        f"Expected 28 features, got {X_transformed.shape[1]}"
    )
```

---

## Test File 2: `test_models.py`

**Scope:** Tests model training, prediction, evaluation metrics, and serialization.

### Test Cases

| Test Name                           | Description                                                   |
|-------------------------------------|---------------------------------------------------------------|
| `test_logistic_regression_trains`   | Verifies LogReg trains without errors                         |
| `test_random_forest_trains`         | Verifies RF trains without errors                             |
| `test_xgboost_trains`              | Verifies XGBoost trains without errors                        |
| `test_prediction_shape`            | Confirms predictions match number of test samples             |
| `test_prediction_probabilities`    | Validates probabilities sum to 1 and are in [0, 1]            |
| `test_accuracy_above_threshold`    | Asserts test accuracy >= 0.80 for all models                  |
| `test_roc_auc_above_threshold`     | Asserts ROC AUC >= 0.85 for the best model                   |
| `test_model_serialization`         | Tests joblib save/load produces identical predictions          |
| `test_cross_validation_stability`  | Checks CV std deviation < 0.02                                |

### Example

```python
def test_roc_auc_above_threshold(trained_model, X_test, y_test):
    """Verify best model achieves ROC AUC >= 0.85."""
    y_proba = trained_model.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_proba)
    assert roc_auc >= 0.85, f"ROC AUC {roc_auc:.4f} below threshold 0.85"
```

---

## Test File 3: `test_fairness.py`

**Scope:** Tests fairness metric computation and bias mitigation strategies.

### Test Cases

| Test Name                               | Description                                              |
|-----------------------------------------|----------------------------------------------------------|
| `test_demographic_parity_computation`   | Validates DPD calculation across gender groups            |
| `test_equal_opportunity_computation`    | Validates EOD calculation across gender groups            |
| `test_fairness_within_threshold`        | Asserts |DPD| < 0.10 for all protected attributes        |
| `test_reweighing_reduces_bias`          | Confirms reweighing lowers DPD for gender                 |
| `test_threshold_optimization`           | Validates group-specific thresholds improve EOD           |
| `test_intersectional_fairness`          | Tests fairness at intersection of gender × race          |
| `test_fairness_report_generation`       | Validates HTML report is generated without errors         |
| `test_sample_weights_valid`             | Ensures reweighing produces non-negative weights          |

### Example

```python
def test_fairness_within_threshold(y_pred, gender_groups):
    """Verify demographic parity difference is within acceptable range."""
    dpd = compute_demographic_parity_difference(y_pred, gender_groups)
    assert abs(dpd) < 0.10, (
        f"Demographic parity difference {dpd:.4f} exceeds threshold 0.10"
    )
```

---

## Test File 4: `test_api.py`

**Scope:** Integration tests for FastAPI endpoints using `TestClient`.

### Test Cases

| Test Name                               | Description                                              |
|-----------------------------------------|----------------------------------------------------------|
| `test_health_endpoint`                  | GET /health returns 200 with status "ok"                 |
| `test_predict_valid_input`              | POST /api/v1/predict returns prediction and probability  |
| `test_predict_invalid_input`            | POST with missing fields returns 422 validation error    |
| `test_predict_out_of_range`             | POST with out-of-range values returns meaningful error   |
| `test_explain_shap_endpoint`            | POST /api/v1/explain/shap returns SHAP values            |
| `test_explain_lime_endpoint`            | POST /api/v1/explain/lime returns LIME explanation        |
| `test_fairness_metrics_endpoint`        | GET /api/v1/fairness/metrics returns fairness data        |
| `test_batch_prediction`                 | POST /api/v1/predict/batch handles multiple inputs       |
| `test_rate_limiting`                    | Verifies rate limiting returns 429 on excessive requests  |
| `test_cors_headers`                     | Validates CORS headers in response                       |

### Example

```python
from fastapi.testclient import TestClient

def test_predict_valid_input(client, valid_payload):
    """Test prediction endpoint with valid loan application data."""
    response = client.post("/api/v1/predict", json=valid_payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert data["prediction"] in [0, 1]
    assert 0.0 <= data["probability"] <= 1.0
```

---

## Shared Fixtures (`conftest.py`)

```python
import pytest
import joblib
import pandas as pd
import numpy as np

@pytest.fixture
def sample_data():
    """Generate sample loan application data for testing."""
    return pd.DataFrame({
        'applicant_income': [50000, 75000, 30000],
        'coapplicant_income': [20000, 0, 15000],
        'loan_amount': [150000, 300000, 80000],
        # ... remaining features
    })

@pytest.fixture
def trained_model():
    """Load the trained logistic regression model."""
    return joblib.load('models_saved/logistic_regression.pkl')

@pytest.fixture
def preprocessor():
    """Load the fitted preprocessing pipeline."""
    return joblib.load('artifacts/preprocessor.pkl')
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=./ --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_preprocessing.py -v

# Run specific test
pytest tests/test_api.py::test_predict_valid_input -v

# Run with markers
pytest tests/ -v -m "not slow"
```

---

## Coverage Targets

| Module           | Target Coverage | Current Coverage |
|------------------|----------------|-----------------|
| preprocessing/   | ≥ 90%          | 92%             |
| models/          | ≥ 85%          | 88%             |
| fairness/        | ≥ 85%          | 87%             |
| api/             | ≥ 80%          | 84%             |
| **Overall**      | **≥ 85%**      | **88%**         |

---

## References

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
