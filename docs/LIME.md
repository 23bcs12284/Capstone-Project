# LIME Explainability Documentation

## Overview

LIME (Local Interpretable Model-agnostic Explanations) is the secondary explainability framework used in the Explainable AI Loan Approval Prediction System. LIME provides local, instance-level explanations by fitting interpretable surrogate models around individual predictions. It complements SHAP by offering an alternative perspective on feature contributions.

---

## LimeTabularExplainer Setup

```python
from lime.lime_tabular import LimeTabularExplainer
import numpy as np

explainer = LimeTabularExplainer(
    training_data=X_train_transformed,
    feature_names=feature_names,           # List of 28 transformed feature names
    class_names=['Denied', 'Approved'],
    categorical_features=categorical_indices,
    mode='classification',
    discretize_continuous=True,
    random_state=42
)
```

### Configuration Parameters

| Parameter                | Value                    | Rationale                                          |
|--------------------------|--------------------------|----------------------------------------------------|
| `training_data`          | X_train (transformed)    | Background distribution for perturbation sampling  |
| `feature_names`          | 28 feature names         | Human-readable labels for explanations             |
| `class_names`            | ['Denied', 'Approved']   | Prediction class labels                            |
| `categorical_features`   | Indices of encoded cols  | Ensures proper perturbation of categorical features|
| `mode`                   | 'classification'         | Binary classification task                         |
| `discretize_continuous`  | True                     | Groups continuous features into bins for clarity    |
| `random_state`           | 42                       | Reproducible explanations                          |

---

## Generating Explanations

### Single Instance Explanation

```python
def explain_instance(model, instance, num_features=10):
    """
    Generate a LIME explanation for a single loan application.
    
    Args:
        model: Trained classifier with predict_proba method
        instance: Single sample (1D array of 28 features)
        num_features: Number of top features to display
    
    Returns:
        lime.explanation.Explanation: LIME explanation object
    """
    explanation = explainer.explain_instance(
        data_row=instance,
        predict_fn=model.predict_proba,
        num_features=num_features,
        num_samples=5000,
        top_labels=2
    )
    return explanation
```

### Parameters for Explanation Quality

| Parameter       | Default | Project Setting | Notes                                  |
|-----------------|---------|-----------------|----------------------------------------|
| `num_features`  | 10      | 10              | Top contributing features to show      |
| `num_samples`   | 5000    | 5000            | Perturbation samples for local model   |
| `top_labels`    | 1       | 2               | Explain both Denied and Approved       |

---

## Feature Contributions

LIME produces a list of feature-value pairs with associated contribution weights. Each weight indicates how much that feature's current value pushes the prediction toward or away from a particular class.

### Example Output

For a sample applicant (predicted: **Approved**, probability: 0.87):

| Rank | Feature Condition                     | Contribution | Direction |
|------|---------------------------------------|-------------|-----------|
| 1    | credit_score > 720                    | +0.2134     | Approved  |
| 2    | debt_to_income_ratio <= 0.30          | +0.1567     | Approved  |
| 3    | income_loan_ratio > 3.50              | +0.1289     | Approved  |
| 4    | years_employed > 5                    | +0.0934     | Approved  |
| 5    | applicant_income > 65000              | +0.0812     | Approved  |
| 6    | has_collateral = Yes                  | +0.0678     | Approved  |
| 7    | loan_amount <= 200000                 | +0.0534     | Approved  |
| 8    | education = Master                    | +0.0423     | Approved  |
| 9    | num_dependents <= 2                   | +0.0312     | Approved  |
| 10   | employment_type = Salaried            | +0.0267     | Approved  |

### Interpretation

- **Positive contributions** push toward the predicted class (Approved in this case)
- **Negative contributions** push against the predicted class
- **Magnitude** indicates strength of the feature's influence
- **Conditions** show the discretized feature ranges that LIME identified as important

---

## Output Formats

### HTML Output

LIME generates rich, interactive HTML reports that can be viewed in any web browser:

```python
# Save explanation as standalone HTML file
explanation.save_to_file('reports/lime_explanation_sample.html')

# Generate HTML string for embedding in dashboards
html_string = explanation.as_html()
```

**HTML Features:**
- Interactive bar chart showing feature contributions
- Prediction probabilities for each class
- Color-coded bars (green for positive, red for negative contributions)
- Hover tooltips with exact contribution values
- Embeddable in Streamlit dashboard via `st.components.v1.html()`

### Matplotlib Output

LIME also supports static matplotlib visualizations for reports and publications:

```python
import matplotlib.pyplot as plt

# Plot explanation as matplotlib figure
fig = explanation.as_pyplot_figure(label=1)
fig.set_size_inches(10, 6)
fig.tight_layout()
fig.savefig('reports/lime_explanation_plot.png', dpi=300, bbox_inches='tight')
plt.close(fig)
```

**Matplotlib Features:**
- Publication-quality static bar chart
- Configurable figure size and DPI
- Suitable for inclusion in research papers and PDF reports
- Can be batch-generated for multiple instances

### Batch Explanation Generation

```python
def generate_batch_explanations(model, X_samples, output_dir='reports/lime/'):
    """Generate LIME explanations for multiple samples."""
    os.makedirs(output_dir, exist_ok=True)
    
    for i, instance in enumerate(X_samples):
        explanation = explain_instance(model, instance)
        explanation.save_to_file(f'{output_dir}/lime_instance_{i}.html')
        
        fig = explanation.as_pyplot_figure(label=1)
        fig.savefig(f'{output_dir}/lime_instance_{i}.png', dpi=200)
        plt.close(fig)
```

---

## Integration with Dashboard

The Streamlit dashboard integrates LIME explanations in the "Individual Prediction" tab:

```python
import streamlit.components.v1 as components

# Display LIME explanation in Streamlit
explanation = explain_instance(model, user_input)
html_content = explanation.as_html()
components.html(html_content, height=600, scrolling=True)
```

---

## LIME vs SHAP Comparison

| Aspect              | LIME                           | SHAP                          |
|---------------------|--------------------------------|-------------------------------|
| Scope               | Local only                     | Local + Global                |
| Method              | Local surrogate model          | Shapley values                |
| Model-agnostic      | Yes                            | Depends on explainer          |
| Consistency         | May vary across runs           | Theoretically consistent      |
| Speed               | Moderate (5000 perturbations)  | Fast (tree) / Slow (kernel)   |
| Output              | Feature conditions + weights   | Feature values + SHAP values  |
| Visualization       | HTML + matplotlib              | Multiple plot types            |

---

## Artifacts

- `reports/lime_explanation_sample.html` — Sample HTML explanation
- `reports/lime_explanation_plot.png` — Sample matplotlib visualization
- `reports/lime/` — Directory of batch-generated explanations

---

## References

- Ribeiro, M.T. et al. (2016). "Why Should I Trust You?": Explaining the Predictions of Any Classifier. KDD '16.
- [LIME GitHub Repository](https://github.com/marcotcr/lime)
- [LIME Documentation](https://lime-ml.readthedocs.io/)
