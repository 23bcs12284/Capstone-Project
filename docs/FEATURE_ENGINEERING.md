# Feature Engineering Documentation

## Overview

This document describes the feature engineering pipeline used in the Explainable AI Loan Approval Prediction System. The pipeline transforms 15 raw input features (8 numeric + 7 categorical) into 28 model-ready features using a combination of StandardScaler for numeric features and OneHotEncoder for categorical features.

---

## Raw Input Features

### Numeric Features (8)

| # | Feature Name           | Description                              | Range / Units        |
|---|------------------------|------------------------------------------|----------------------|
| 1 | `applicant_income`     | Monthly income of the primary applicant  | $1,000 – $100,000    |
| 2 | `coapplicant_income`   | Monthly income of the co-applicant       | $0 – $50,000         |
| 3 | `loan_amount`          | Requested loan amount                    | $10,000 – $700,000   |
| 4 | `loan_term`            | Loan repayment term                      | 12 – 480 months      |
| 5 | `credit_score`         | Applicant's credit score                 | 300 – 850            |
| 6 | `debt_to_income_ratio` | Ratio of monthly debt to monthly income  | 0.0 – 1.0            |
| 7 | `years_employed`       | Number of years at current employment    | 0 – 45 years         |
| 8 | `num_dependents`       | Number of financial dependents           | 0 – 10               |

### Categorical Features (7)

| # | Feature Name           | Description                    | Unique Values                                      |
|---|------------------------|--------------------------------|----------------------------------------------------|
| 1 | `gender`               | Applicant gender               | Male, Female, Non-Binary                           |
| 2 | `marital_status`       | Marital status                 | Single, Married, Divorced, Widowed                 |
| 3 | `education`            | Highest education level        | High School, Bachelor, Master, PhD                 |
| 4 | `employment_type`      | Type of employment             | Salaried, Self-Employed, Freelancer                |
| 5 | `property_area`        | Area of the property           | Urban, Semi-Urban, Rural                           |
| 6 | `loan_purpose`         | Purpose of the loan            | Home, Education, Personal, Auto                    |
| 7 | `has_collateral`       | Whether collateral is provided | Yes, No                                            |

---

## Transformation Pipeline

### Step 1: Missing Value Imputation

```python
# Numeric features: median imputation
numeric_imputer = SimpleImputer(strategy='median')

# Categorical features: most frequent imputation
categorical_imputer = SimpleImputer(strategy='most_frequent')
```

Missing values are handled before scaling or encoding. Median imputation is preferred for numeric features to avoid sensitivity to outliers. Most-frequent imputation is used for categorical features to preserve the dominant class.

### Step 2: Numeric Scaling — StandardScaler

All 8 numeric features are standardized using `StandardScaler`:

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_numeric_scaled = scaler.fit_transform(X_numeric)
```

- **Formula**: `z = (x - μ) / σ`
- **Result**: 8 scaled numeric features with mean ≈ 0 and standard deviation ≈ 1
- **Rationale**: Ensures that features with different magnitudes (e.g., income vs. dependents) contribute equally during model training

### Step 3: Categorical Encoding — OneHotEncoder

All 7 categorical features are encoded using `OneHotEncoder`:

```python
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
X_categorical_encoded = encoder.fit_transform(X_categorical)
```

- **`drop='first'`**: Drops the first category per feature to avoid multicollinearity
- **`handle_unknown='ignore'`**: Unseen categories during inference produce all-zero rows

#### Encoded Feature Breakdown

| Original Feature   | Categories | Encoded Columns (drop='first') |
|--------------------|------------|-------------------------------|
| `gender`           | 3          | 2                             |
| `marital_status`   | 4          | 3                             |
| `education`        | 4          | 3                             |
| `employment_type`  | 3          | 2                             |
| `property_area`    | 3          | 2                             |
| `loan_purpose`     | 4          | 3                             |
| `has_collateral`   | 2          | 1                             |
| **Total**          | **23**     | **16**                        |

> **Note**: Not all categories may be present in every dataset split; `handle_unknown='ignore'` ensures robustness.

### Step 4: Combined Pipeline

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('encoder', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(transformers=[
    ('num', numeric_transformer, numeric_features),
    ('cat', categorical_transformer, categorical_features)
])
```

### Step 5: Derived Features (4 Engineered)

In addition to scaled and encoded features, four derived features are computed:

| # | Feature Name             | Formula                                    | Description                           |
|---|--------------------------|--------------------------------------------|---------------------------------------|
| 1 | `income_loan_ratio`      | `applicant_income / loan_amount`           | Capacity to repay relative to loan    |
| 2 | `total_income`           | `applicant_income + coapplicant_income`    | Combined household income             |
| 3 | `log_loan_amount`        | `log(loan_amount + 1)`                     | Log-transformed loan for normality    |
| 4 | `credit_risk_score`      | `credit_score * (1 - debt_to_income_ratio)`| Composite credit risk indicator       |

These derived features are also standardized via `StandardScaler` before model training.

---

## Final Transformed Feature Count

| Category                          | Count |
|-----------------------------------|-------|
| Scaled numeric features           | 8     |
| One-hot encoded categorical       | 16    |
| Derived engineered features       | 4     |
| **Total transformed features**    | **28**|

---

## Artifacts

- **Preprocessor**: Saved as `artifacts/preprocessor.pkl` via `joblib.dump()`
- **Feature Names**: Stored in `artifacts/feature_names.json` for SHAP/LIME compatibility
- **Scaler Statistics**: Mean and std values saved in `artifacts/scaler_stats.csv`

---

## Usage

```python
import joblib

preprocessor = joblib.load('artifacts/preprocessor.pkl')
X_transformed = preprocessor.transform(new_data)
# X_transformed.shape => (n_samples, 28)
```

---

## References

- [scikit-learn ColumnTransformer](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html)
- [StandardScaler Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)
- [OneHotEncoder Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html)
