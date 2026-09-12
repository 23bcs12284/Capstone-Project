# ML Pipeline — Explainable AI Loan Approval Prediction System

## Overview

The machine learning pipeline transforms raw synthetic loan data into a production-ready
classification model. The pipeline is fully automated and executes the following stages
sequentially: validation, imputation, clipping, encoding, scaling, splitting, tuning,
comparison, selection, and serialization.

---

## Pipeline Stages

```
Raw Dataset
    │
    ▼
┌─────────────┐
│ 1. Validate │  Schema checks, type enforcement, range validation
└──────┬──────┘
       ▼
┌─────────────┐
│ 2. Impute   │  Fill missing values (median for numeric, mode for categorical)
└──────┬──────┘
       ▼
┌─────────────┐
│ 3. Clip     │  IQR-based outlier clipping on continuous features
└──────┬──────┘
       ▼
┌─────────────┐
│ 4. Encode   │  One-hot encoding for categorical features
└──────┬──────┘
       ▼
┌─────────────┐
│ 5. Scale    │  StandardScaler on numeric features
└──────┬──────┘
       ▼
┌─────────────┐
│ 6. Split    │  Stratified 80/20 train/test split
└──────┬──────┘
       ▼
┌─────────────┐
│ 7. Tune     │  GridSearchCV with stratified 5-fold CV
└──────┬──────┘
       ▼
┌─────────────┐
│ 8. Compare  │  Evaluate all models on test set
└──────┬──────┘
       ▼
┌─────────────┐
│ 9. Select   │  Pick best model by ROC AUC
└──────┬──────┘
       ▼
┌──────────────┐
│10. Serialize │  Save model + preprocessor with Joblib
└──────────────┘
```

---

## Stage Details

### Stage 1: Data Validation

Validates the raw dataset against expected schema before processing.

| Check | Description |
|-------|-------------|
| Column presence | Ensures all required columns exist |
| Data types | Verifies numeric and categorical column types |
| Value ranges | Validates credit_score ∈ [300, 850], age ∈ [18, 100], etc. |
| Null thresholds | Rejects datasets with >30% missing values in any column |
| Duplicate detection | Flags and optionally removes duplicate rows |

### Stage 2: Missing Value Imputation

| Feature Type | Strategy | Implementation |
|-------------|----------|----------------|
| Numeric | Median | `SimpleImputer(strategy='median')` |
| Categorical | Most frequent | `SimpleImputer(strategy='most_frequent')` |

### Stage 3: Outlier Clipping

Applies IQR-based clipping to continuous features to reduce the influence of extreme values.

```
Q1 = 25th percentile
Q3 = 75th percentile
IQR = Q3 - Q1
Lower bound = Q1 - 1.5 × IQR
Upper bound = Q3 + 1.5 × IQR
```

| Feature | Clipping Applied |
|---------|-----------------|
| `income` | ✅ |
| `loan_amount` | ✅ |
| `debt_to_income` | ✅ |
| `credit_score` | ✅ |
| `employment_length` | ✅ |

### Stage 4: Categorical Encoding

One-hot encoding is applied to all categorical features using `OneHotEncoder(drop='first')` to avoid multicollinearity.

| Feature | Categories |
|---------|-----------|
| `gender` | Male, Female, Non-binary |
| `race` | White, Black, Asian, Hispanic, Other |
| `education` | High School, Associate, Bachelor, Master, PhD |
| `home_ownership` | Own, Rent, Mortgage |
| `loan_purpose` | Home Improvement, Debt Consolidation, Education, Business, Other |

### Stage 5: Feature Scaling

StandardScaler normalizes numeric features to zero mean and unit variance.

```
z = (x - μ) / σ
```

| Feature | Scaled |
|---------|--------|
| `age` | ✅ |
| `income` | ✅ |
| `loan_amount` | ✅ |
| `credit_score` | ✅ |
| `employment_length` | ✅ |
| `debt_to_income` | ✅ |
| `num_credit_lines` | ✅ |

### Stage 6: Train/Test Split

| Parameter | Value |
|-----------|-------|
| Test size | 20% |
| Stratification | On target variable (`loan_status`) |
| Random state | 42 |
| Shuffle | True |

### Stage 7: Hyperparameter Tuning (GridSearchCV)

Each model is tuned using `GridSearchCV` with stratified 5-fold cross-validation.

| Model | Key Hyperparameters Searched |
|-------|------------------------------|
| Logistic Regression | `C`, `penalty`, `solver`, `max_iter` |
| XGBoost | `n_estimators`, `max_depth`, `learning_rate`, `subsample` |
| LightGBM | `n_estimators`, `num_leaves`, `learning_rate`, `min_child_samples` |
| CatBoost | `iterations`, `depth`, `learning_rate`, `l2_leaf_reg` |

**Scoring metric:** ROC AUC (area under the receiver operating characteristic curve)

### Stage 8: Model Comparison

All tuned models are evaluated on the held-out test set:

| Metric | Description |
|--------|-------------|
| Accuracy | Overall correct prediction rate |
| Precision | Positive predictive value |
| Recall | True positive rate (sensitivity) |
| F1 Score | Harmonic mean of precision and recall |
| ROC AUC | Area under the ROC curve |

**Results:**

| Model | Accuracy | Precision | Recall | F1 | ROC AUC |
|-------|----------|-----------|--------|----|---------|
| **Logistic Regression** | **0.8934** | **0.8876** | **0.9012** | **0.8943** | **0.9121** |
| XGBoost | 0.8812 | 0.8745 | 0.8901 | 0.8822 | 0.9034 |
| LightGBM | 0.8789 | 0.8698 | 0.8878 | 0.8787 | 0.9008 |
| CatBoost | 0.8756 | 0.8672 | 0.8845 | 0.8757 | 0.8976 |

### Stage 9: Model Selection

The model with the **highest ROC AUC** on the test set is automatically selected as the
production model.

**Selected model:** Logistic Regression (ROC AUC = **0.9121**)

### Stage 10: Serialization

| Artifact | File | Format |
|----------|------|--------|
| Best model | `models/best_model.joblib` | Joblib |
| Preprocessor pipeline | `models/preprocessor.joblib` | Joblib |
| Model metadata | `models/model_metadata.json` | JSON |

---

## Running the Pipeline

```bash
# Full pipeline execution
python -m src.models.train_pipeline

# With custom parameters
python -m src.models.train_pipeline --data data/loan_dataset.csv --output models/
```

---

## Pipeline Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `test_size` | 0.2 | Fraction of data for testing |
| `cv_folds` | 5 | Number of cross-validation folds |
| `scoring` | `roc_auc` | GridSearchCV scoring metric |
| `random_state` | 42 | Random seed for reproducibility |

---

> **See also:** [DECISIONS.md](./DECISIONS.md) · [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)
