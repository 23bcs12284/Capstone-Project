# Known Issues

## Overview

This document tracks known issues, warnings, and limitations in the Explainable AI Loan Approval Prediction System. **There are no known functional bugs at the time of writing.** All listed items are non-critical warnings or environment-specific behaviors.

---

## Warning 1: XGBoost Feature Name Validation

**Type:** Warning (non-functional)
**Severity:** Low
**Component:** Model Training / Prediction

### Description

XGBoost v1.7+ issues a `UserWarning` when feature names passed during prediction differ from those used during training. This occurs when the preprocessor generates feature names with characters that XGBoost sanitizes internally (e.g., brackets `[]` in one-hot encoded column names).

### Warning Message

```
UserWarning: Feature names stored in the model are different from the 
feature names in the input data. Feature names in the model:
['num__applicant_income', 'cat__gender_Female', ...]
Feature names in the input data:
['applicant_income', 'gender_Female', ...]
```

### Root Cause

The `ColumnTransformer` prefixes feature names with transformer names (e.g., `num__`, `cat__`), but when features are passed as a NumPy array (which has no column names), XGBoost may use its internally stored names, causing a mismatch.

### Workaround

```python
# Option 1: Pass DataFrame with correct names to XGBoost
feature_names = preprocessor.get_feature_names_out()
X_df = pd.DataFrame(X_transformed, columns=feature_names)
xgb_model.predict(X_df)

# Option 2: Suppress the warning
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='xgboost')
```

### Status: Acknowledged — does not affect predictions or model accuracy.

---

## Warning 2: scikit-learn Deprecation — `sparse_output`

**Type:** Deprecation Warning
**Severity:** Low
**Component:** Preprocessing

### Description

In scikit-learn v1.2+, the `sparse` parameter in `OneHotEncoder` was renamed to `sparse_output`. Using the old parameter name triggers a `FutureWarning`.

### Warning Message

```
FutureWarning: `sparse` was renamed to `sparse_output` in version 1.2 
and will be removed in version 1.4. `sparse_output` is ignored unless 
you leave `sparse` to its default value.
```

### Workaround

The codebase already uses `sparse_output=False`. This warning only appears if an older version of the code is run. Ensure `scikit-learn >= 1.2.0` is installed:

```bash
pip install scikit-learn>=1.2.0
```

### Status: Fixed in current codebase. Warning appears only with outdated code versions.

---

## Warning 3: scikit-learn Convergence Warning — Logistic Regression

**Type:** Convergence Warning
**Severity:** Low
**Component:** Model Training

### Description

On certain random seeds or data subsets during cross-validation, Logistic Regression may issue a `ConvergenceWarning` indicating that the solver did not fully converge within the default iteration limit.

### Warning Message

```
ConvergenceWarning: lbfgs failed to converge (status=1):
STOP: TOTAL NO. of ITERATIONS REACHED LIMIT.
Increase the number of iterations (max_iter) or scale the data.
```

### Workaround

The project sets `max_iter=1000` (default is 100), which resolves this warning in nearly all cases:

```python
LogisticRegression(max_iter=1000, solver='lbfgs')
```

### Status: Resolved. The warning should not appear with the current configuration.

---

## Warning 4: SHAP Additivity Check

**Type:** Warning
**Severity:** Low
**Component:** Explainability (SHAP)

### Description

SHAP's `TreeExplainer` may issue a warning about additivity checks failing when using certain model configurations. This occurs when SHAP values don't perfectly sum to the model output due to floating-point precision.

### Warning Message

```
ExplainerError: Additivity check failed in TreeExplainer! Please ensure 
the data matrix is the same data type as the training data.
```

### Workaround

```python
# Ensure data type consistency
X_background = X_train.astype(np.float64)
explainer = shap.TreeExplainer(model, X_background, check_additivity=False)
```

### Status: Mitigated by setting `check_additivity=False` where appropriate.

---

## Warning 5: CatBoost Verbose Output

**Type:** Informational
**Severity:** Very Low
**Component:** Model Training

### Description

CatBoost outputs verbose training progress by default, which clutters the console during automated training scripts.

### Workaround

```python
CatBoostClassifier(verbose=0)  # Suppress all output
# or
CatBoostClassifier(verbose=100)  # Print every 100 iterations
```

### Status: Resolved in current configuration with `verbose=0`.

---

## Limitations (Not Bugs)

### 1. Dataset Size

The training dataset contains approximately 4,500 samples. While sufficient for the models used, larger datasets could improve generalization and enable more robust fairness analysis, particularly for intersectional groups with small counts.

### 2. Static Model

The deployed model does not retrain automatically. Predictions may degrade over time as the underlying data distribution shifts (concept drift). A monitoring and retraining pipeline is planned for future iterations.

### 3. KernelExplainer Performance

When SHAP's `KernelExplainer` is used (for SVM/KNN), explanation generation takes 30-60 seconds per instance due to the perturbation-based approach. This affects dashboard responsiveness in standalone mode when non-tree models are selected.

### 4. Browser Compatibility for Force Plots

SHAP's interactive force plots require JavaScript and may not render correctly in:
- Streamlit's iframe sandboxing (use `unsafe_allow_html=True`)
- Older browsers (IE11 is not supported)
- PDF exports (use static waterfall plots instead)

---

## Reporting New Issues

If you encounter a new issue, please:

1. Check this document first to see if it's already known
2. Open an issue in the project repository with:
   - Clear description of the problem
   - Steps to reproduce
   - Python and package versions (`pip freeze > versions.txt`)
   - Full error traceback
   - Expected vs. actual behavior
