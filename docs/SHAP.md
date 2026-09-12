# SHAP Explainability Documentation

## Overview

SHAP (SHapley Additive exPlanations) is the primary explainability framework used in the Explainable AI Loan Approval Prediction System. It provides both global and local interpretability by computing Shapley values — a game-theoretic approach to quantify each feature's contribution to individual predictions.

---

## Dynamic Explainer Selection

The system uses a dynamic explainer factory that automatically selects the appropriate SHAP explainer based on the model type:

```python
import shap

def get_shap_explainer(model, X_background):
    """
    Dynamically select the optimal SHAP explainer based on model type.
    
    Args:
        model: Trained ML model
        X_background: Background dataset for explainer (typically 100-200 samples)
    
    Returns:
        shap.Explainer: Configured SHAP explainer instance
    """
    model_name = type(model).__name__
    
    if model_name in ['LogisticRegression', 'LinearSVC']:
        return shap.LinearExplainer(model, X_background)
    elif model_name in ['RandomForestClassifier', 'GradientBoostingClassifier']:
        return shap.TreeExplainer(model)
    elif model_name in ['XGBClassifier', 'CatBoostClassifier']:
        return shap.TreeExplainer(model)
    else:
        return shap.KernelExplainer(model.predict_proba, X_background)
```

### Explainer Types Used

| Model Type           | SHAP Explainer   | Speed     | Exact? |
|----------------------|------------------|-----------|--------|
| Logistic Regression  | LinearExplainer  | Very Fast | Yes    |
| Random Forest        | TreeExplainer    | Fast      | Yes    |
| Gradient Boosting    | TreeExplainer    | Fast      | Yes    |
| XGBoost              | TreeExplainer    | Fast      | Yes    |
| CatBoost             | TreeExplainer    | Fast      | Yes    |
| SVM / KNN            | KernelExplainer  | Slow      | Approx |

---

## SHAP Plots

### 1. Waterfall Plot

Shows how each feature pushes the prediction from the base value (average model output) to the final prediction for a single instance.

```python
shap_values = explainer(X_test_sample)

# Waterfall plot for a single prediction
shap.plots.waterfall(shap_values[0], max_display=15)
```

**Key Characteristics:**
- Displays feature contributions in descending order of absolute impact
- Red bars indicate features pushing toward positive class (approved)
- Blue bars indicate features pushing toward negative class (denied)
- Base value (E[f(x)]) shown at the left origin
- Final prediction value shown at the right

**Use Case:** Explaining individual loan decisions to applicants or auditors.

### 2. Beeswarm Plot

Provides a global overview of feature importance across all test instances, showing the distribution and direction of each feature's impact.

```python
shap.plots.beeswarm(shap_values, max_display=20)
```

**Key Characteristics:**
- Each dot represents a single prediction
- X-axis shows SHAP value (impact on model output)
- Color indicates feature value (red = high, blue = low)
- Features sorted by mean absolute SHAP value
- Reveals non-linear relationships and interaction effects

**Use Case:** Understanding which features matter most globally and how their values affect predictions.

### 3. Bar Plot

Displays mean absolute SHAP values for each feature, providing a clean summary of global feature importance.

```python
shap.plots.bar(shap_values, max_display=15)
```

**Key Characteristics:**
- Horizontal bar chart of mean |SHAP value| per feature
- Features ranked from most to least important
- Provides a clear, stakeholder-friendly importance ranking
- Can be grouped by feature categories

**Use Case:** Executive summaries and high-level model auditing.

### 4. Dependence Plot

Shows the relationship between a single feature's value and its SHAP value, revealing non-linear effects and interactions.

```python
shap.plots.scatter(shap_values[:, "credit_score"], color=shap_values[:, "debt_to_income_ratio"])
```

**Key Characteristics:**
- X-axis: feature value; Y-axis: SHAP value
- Color can represent an interacting feature (auto-detected or specified)
- Reveals thresholds, plateaus, and non-monotonic relationships
- Vertical dispersion indicates interaction effects

**Use Case:** Deep-dive analysis of how specific features (e.g., credit score) influence decisions.

### 5. Force Plot

Interactive visualization showing how features contribute to pushing a prediction from the base value.

```python
shap.plots.force(shap_values[0])

# Multi-instance force plot
shap.plots.force(shap_values[:100])
```

**Key Characteristics:**
- Red features push prediction higher (toward approval)
- Blue features push prediction lower (toward denial)
- Width of each feature bar indicates magnitude of contribution
- Interactive HTML output supports hover for details
- Multi-instance mode shows patterns across predictions

**Use Case:** Interactive dashboards and real-time prediction explanations.

---

## Implementation Details

### Background Data Sampling

```python
# Use K-means to select representative background samples
background = shap.kmeans(X_train, 100)
```

Using K-means clustering for background data selection ensures computational efficiency while maintaining explanation quality, especially for KernelExplainer.

### SHAP Values Storage

```python
import numpy as np

# Compute and cache SHAP values
shap_values = explainer(X_test)
np.save('artifacts/shap_values.npy', shap_values.values)
np.save('artifacts/shap_base_values.npy', shap_values.base_values)
```

### Top Features by Mean |SHAP Value|

| Rank | Feature                | Mean |SHAP Value| |
|------|------------------------|----------------------|
| 1    | credit_score           | 0.1823               |
| 2    | debt_to_income_ratio   | 0.1456               |
| 3    | income_loan_ratio      | 0.1287               |
| 4    | applicant_income       | 0.0934               |
| 5    | loan_amount            | 0.0878               |
| 6    | credit_risk_score      | 0.0812               |
| 7    | years_employed         | 0.0645               |
| 8    | total_income           | 0.0589               |

---

## Artifacts

- `artifacts/shap_values.npy` — Precomputed SHAP values for the test set
- `artifacts/shap_base_values.npy` — Base values for each prediction
- `reports/shap_waterfall.png` — Sample waterfall plot
- `reports/shap_beeswarm.png` — Global beeswarm plot
- `reports/shap_bar.png` — Global feature importance bar plot
- `reports/shap_dependence_credit_score.png` — Credit score dependence plot
- `reports/shap_force.html` — Interactive force plot

---

## References

- Lundberg, S.M. & Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions. NeurIPS.
- Lundberg, S.M. et al. (2020). From local explanations to global understanding with explainable AI for trees. Nature Machine Intelligence, 2, 56-67.
- [SHAP Documentation](https://shap.readthedocs.io/)
