# Fairness Analysis Documentation

## Overview

This document describes the fairness evaluation framework used in the Explainable AI Loan Approval Prediction System. The system assesses algorithmic bias across protected demographic attributes and implements mitigation strategies to ensure equitable loan approval decisions.

---

## Fairness Metrics

### 1. Demographic Parity (Statistical Parity)

**Definition:** A model satisfies demographic parity if the probability of a positive prediction (loan approved) is the same across all groups defined by a protected attribute.

**Formula:**
```
P(Ŷ = 1 | A = a) = P(Ŷ = 1 | A = b)  ∀ groups a, b
```

**Metric:** Demographic Parity Difference (DPD)
```
DPD = P(Ŷ = 1 | A = privileged) - P(Ŷ = 1 | A = unprivileged)
```

- **Ideal value**: 0 (no difference in approval rates)
- **Acceptable range**: |DPD| < 0.10 (80% rule threshold)

### 2. Equal Opportunity

**Definition:** A model satisfies equal opportunity if the true positive rate (recall) is equal across all demographic groups. This ensures that qualified applicants have the same chance of being approved regardless of group membership.

**Formula:**
```
P(Ŷ = 1 | Y = 1, A = a) = P(Ŷ = 1 | Y = 1, A = b)  ∀ groups a, b
```

**Metric:** Equal Opportunity Difference (EOD)
```
EOD = TPR_privileged - TPR_unprivileged
```

- **Ideal value**: 0 (no difference in true positive rates)
- **Acceptable range**: |EOD| < 0.10

---

## Protected Attributes

### 1. Gender

| Group        | Count | Approval Rate | TPR   | DPD    | EOD    |
|-------------|-------|---------------|-------|--------|--------|
| Male        | 2,340 | 0.6812        | 0.8734| —      | —      |
| Female      | 1,890 | 0.6523        | 0.8512| -0.0289| -0.0222|
| Non-Binary  | 270   | 0.6407        | 0.8389| -0.0405| -0.0345|

**Assessment:** Gender bias is within acceptable thresholds (|DPD| < 0.10). Non-Binary group shows slightly lower rates but sample size is limited.

### 2. Age Group

| Group        | Count | Approval Rate | TPR   | DPD    | EOD    |
|-------------|-------|---------------|-------|--------|--------|
| 18-30       | 1,200 | 0.6234        | 0.8312| —      | —      |
| 31-45       | 1,650 | 0.6789        | 0.8689| -0.0555| -0.0377|
| 46-60       | 1,150 | 0.6901        | 0.8756| -0.0667| -0.0444|
| 60+         | 500   | 0.6612        | 0.8534| -0.0378| -0.0222|

**Assessment:** Younger applicants (18-30) show lower approval rates and TPR. This correlates with shorter credit histories and lower average incomes, but warrants monitoring.

### 3. Race

| Group              | Count | Approval Rate | TPR   | DPD    | EOD    |
|-------------------|-------|---------------|-------|--------|--------|
| White             | 1,800 | 0.6878        | 0.8789| —      | —      |
| Black             | 1,050 | 0.6434        | 0.8423| -0.0444| -0.0366|
| Hispanic          | 900   | 0.6567        | 0.8512| -0.0311| -0.0277|
| Asian             | 550   | 0.6723        | 0.8645| -0.0155| -0.0144|
| Other             | 200   | 0.6612        | 0.8534| -0.0266| -0.0255|

**Assessment:** Black applicants show the largest disparity. While within the 0.10 threshold, this requires attention and ongoing monitoring.

---

## Fairness Evaluation Implementation

```python
from fairness.metrics import compute_fairness_metrics

def evaluate_fairness(y_true, y_pred, protected_attributes):
    """
    Compute fairness metrics across all protected attributes.
    
    Args:
        y_true: Ground truth labels
        y_pred: Model predictions
        protected_attributes: Dict mapping attribute names to group arrays
    
    Returns:
        dict: Nested dictionary of fairness metrics per attribute per group
    """
    results = {}
    for attr_name, groups in protected_attributes.items():
        results[attr_name] = compute_fairness_metrics(
            y_true, y_pred, groups,
            metrics=['demographic_parity', 'equal_opportunity',
                     'equalized_odds', 'predictive_parity']
        )
    return results
```

---

## Mitigation Strategies

### 1. Reweighing (Pre-processing)

Reweighing assigns instance-level weights to the training data to counteract bias in the labeled dataset before model training.

```python
from fairness.mitigation import Reweighing

reweigher = Reweighing(
    unprivileged_groups=[{'gender': 'Female'}, {'gender': 'Non-Binary'}],
    privileged_groups=[{'gender': 'Male'}]
)

# Compute sample weights
sample_weights = reweigher.fit_transform(X_train, y_train)

# Train with adjusted weights
model.fit(X_train, y_train, sample_weight=sample_weights)
```

**Impact on Metrics After Reweighing:**

| Attribute | DPD (Before) | DPD (After) | EOD (Before) | EOD (After) |
|-----------|-------------|-------------|-------------|-------------|
| Gender    | -0.0289     | -0.0112     | -0.0222     | -0.0098     |
| Age Group | -0.0555     | -0.0234     | -0.0377     | -0.0189     |
| Race      | -0.0444     | -0.0178     | -0.0366     | -0.0156     |

### 2. Threshold Adjustment (Post-processing)

Group-specific decision thresholds are optimized to equalize true positive rates across demographic groups.

```python
from fairness.mitigation import ThresholdOptimizer

optimizer = ThresholdOptimizer(
    objective='equalized_odds',
    constraints='demographic_parity',
    grid_size=1000
)

# Find optimal thresholds per group
thresholds = optimizer.fit(y_val, y_pred_proba, protected_attr)

# Apply group-specific thresholds
y_pred_fair = optimizer.predict(y_pred_proba, protected_attr)
```

**Optimized Thresholds:**

| Group         | Default Threshold | Optimized Threshold |
|---------------|-------------------|---------------------|
| Male          | 0.50              | 0.52                |
| Female        | 0.50              | 0.47                |
| Non-Binary    | 0.50              | 0.46                |

---

## Intersectional Analysis

Fairness is also evaluated at the intersection of protected attributes (e.g., Black Female applicants aged 18-30) to detect compound biases not visible in single-attribute analysis.

```python
intersectional_results = evaluate_fairness(
    y_true, y_pred,
    {'gender_race': combined_groups}
)
```

---

## Fairness Dashboard Integration

Fairness metrics are displayed in the "Fairness Analysis" tab of the Streamlit dashboard, including:
- Bar charts comparing approval rates across groups
- DPD and EOD gauge charts with acceptable range indicators
- Before/after mitigation comparison tables
- Intersectional heat maps

---

## Artifacts

- `reports/fairness_metrics.csv` — Complete fairness metrics table
- `reports/fairness_report.html` — Visual fairness report
- `artifacts/sample_weights.npy` — Reweighing sample weights
- `artifacts/fair_thresholds.json` — Optimized group thresholds

---

## References

- Hardt, M. et al. (2016). Equality of Opportunity in Supervised Learning. NeurIPS.
- Bellamy, R.K.E. et al. (2019). AI Fairness 360: An Extensible Toolkit. IBM Journal of R&D.
- Chouldechova, A. (2017). Fair prediction with disparate impact. Big Data, 5(2).
