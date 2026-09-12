"""
Counterfactual Explanation Generator

For rejected loan applications, generates realistic counterfactual suggestions
showing what changes could potentially flip the decision. Uses SHAP values to
identify the most impactful features to change.

IMPORTANT: These are model-derived scenarios, NOT guaranteed approval criteria.
"""

import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Features that should NOT be suggested for change (immutable or protected)
IMMUTABLE_FEATURES = {
    "age", "gender", "race", "age_group", "marital_status",
    "education", "education_level",  # Education is slow to change
}

# Human-readable names for features
FEATURE_DISPLAY_NAMES = {
    "credit_score": "Credit Score",
    "fico_score": "FICO Score",
    "income": "Annual Income",
    "annual_income": "Annual Income",
    "monthly_income": "Monthly Income",
    "loan_amount": "Loan Amount",
    "requested_amount": "Requested Amount",
    "loan_amount_requested": "Loan Amount Requested",
    "dti": "Debt-to-Income Ratio",
    "dti_ratio": "Debt-to-Income Ratio",
    "monthly_debt": "Monthly Debt",
    "employment_years": "Employment Years",
    "employment_length": "Employment Length",
    "years_at_job": "Years at Current Job",
    "coapplicant_income": "Co-applicant Income",
    "loan_term": "Loan Term",
    "loan_term_years": "Loan Term (Years)",
    "down_payment_pct": "Down Payment Percentage",
    "property_value": "Property Value",
    "num_dependents": "Number of Dependents",
    "existing_mortgages": "Existing Mortgages",
    "credit_history_length": "Credit History Length",
    "num_credit_lines": "Number of Credit Lines",
    "interest_rate": "Interest Rate",
    "previous_defaults": "Previous Defaults",
}


class CounterfactualExplainer:
    """
    Generates counterfactual explanations for rejected loan applications.
    
    Uses SHAP values to identify the features with the largest negative impact,
    then suggests realistic target values based on the distribution of approved
    applicants in the training data.
    """

    def __init__(
        self,
        training_data: pd.DataFrame,
        training_labels: pd.Series,
        feature_names: List[str],
        immutable_features: set = None,
    ):
        """
        Args:
            training_data: The preprocessed training features (before scaling).
            training_labels: The training target labels (0/1).
            feature_names: List of feature names matching training_data columns.
            immutable_features: Set of feature names that should not be suggested for change.
        """
        self.training_data = training_data
        self.training_labels = training_labels
        self.feature_names = feature_names
        self.immutable_features = immutable_features or IMMUTABLE_FEATURES

        # Pre-compute approved applicant statistics
        labels_arr = np.array(training_labels)
        approved_mask = (labels_arr == 1)
        self.approved_data = training_data[approved_mask]
        self.approved_stats = {}

        for col in feature_names:
            if col in training_data.columns:
                s = pd.to_numeric(self.approved_data[col], errors='coerce').dropna()
                if not s.empty:
                    self.approved_stats[col] = {
                        "median": float(s.median()),
                        "p25": float(s.quantile(0.25)),
                        "p75": float(s.quantile(0.75)),
                        "mean": float(s.mean()),
                        "min": float(s.min()),
                        "max": float(s.max()),
                    }

    def generate_counterfactual(
        self,
        instance_values: Dict[str, Any],
        shap_values: Dict[str, float],
        max_suggestions: int = 5,
    ) -> Dict[str, Any]:
        """
        Generate counterfactual suggestions for a rejected application.

        Args:
            instance_values: The original feature values of the applicant (pre-scaling).
            shap_values: Dict mapping feature_name -> SHAP value for this instance.
            max_suggestions: Maximum number of feature changes to suggest.

        Returns:
            Dict with suggestions and metadata.
        """
        # Identify features with the largest negative SHAP values
        # (features pushing the prediction toward rejection)
        negative_features = []
        for feat, shap_val in shap_values.items():
            if shap_val < 0 and feat not in self.immutable_features:
                negative_features.append((feat, shap_val))

        # Sort by most negative impact first
        negative_features.sort(key=lambda x: x[1])

        suggestions = []
        for feat, shap_val in negative_features[:max_suggestions]:
            current_value = instance_values.get(feat)
            if current_value is None:
                continue

            suggestion = self._generate_feature_suggestion(feat, current_value, shap_val)
            if suggestion:
                suggestions.append(suggestion)

        return {
            "decision": "REJECTED",
            "suggestions": suggestions,
            "disclaimer": (
                "These are model-derived scenarios based on feature importance analysis. "
                "They are NOT guaranteed approval criteria and should not be interpreted "
                "as financial advice. Actual lending decisions involve many factors beyond "
                "this model's scope."
            ),
            "num_suggestions": len(suggestions),
        }

    def _generate_feature_suggestion(
        self, feature: str, current_value: Any, shap_value: float
    ) -> Optional[Dict[str, Any]]:
        """Generate a single feature change suggestion."""
        display_name = FEATURE_DISPLAY_NAMES.get(feature, feature.replace("_", " ").title())

        if feature not in self.approved_stats:
            return None

        stats = self.approved_stats[feature]

        try:
            current_numeric = float(current_value)
        except (ValueError, TypeError):
            return None

        # Determine direction of change needed
        # If current value is below the approved median, suggest increasing
        # If above, suggest decreasing (for features like DTI, loan amount)
        suggested_value = None
        direction = None

        # Features where LOWER is better
        lower_is_better = {
            "dti", "dti_ratio", "monthly_debt", "loan_amount", "requested_amount",
            "loan_amount_requested", "interest_rate", "previous_defaults",
            "existing_mortgages", "num_dependents",
        }

        # Features where HIGHER is better
        higher_is_better = {
            "credit_score", "fico_score", "income", "annual_income", "monthly_income",
            "coapplicant_income", "employment_years", "employment_length",
            "years_at_job", "credit_history_length", "down_payment_pct",
            "property_value", "num_credit_lines",
        }

        if feature in lower_is_better:
            if current_numeric > stats["median"]:
                suggested_value = stats["p25"]  # Suggest 25th percentile of approved
                direction = "decrease"
            else:
                # Already below median, less impactful to change further
                suggested_value = stats["p25"]
                direction = "decrease"
        elif feature in higher_is_better:
            if current_numeric < stats["median"]:
                suggested_value = stats["p75"]  # Suggest 75th percentile of approved
                direction = "increase"
            else:
                suggested_value = stats["p75"]
                direction = "increase"
        else:
            # Unknown direction - use approved median
            if current_numeric < stats["median"]:
                suggested_value = stats["median"]
                direction = "increase"
            else:
                suggested_value = stats["median"]
                direction = "decrease"

        # Skip if the change is trivial (< 5% difference)
        if abs(current_numeric) > 0:
            pct_change = abs(suggested_value - current_numeric) / abs(current_numeric)
            if pct_change < 0.05:
                return None

        # Format values appropriately
        if feature in {"dti", "dti_ratio", "down_payment_pct"}:
            current_display = f"{current_numeric:.1%}"
            suggested_display = f"{suggested_value:.1%}"
        elif feature in {"credit_score", "fico_score"}:
            suggested_value = int(round(suggested_value))
            current_display = str(int(current_numeric))
            suggested_display = f"≥ {suggested_value}"
        elif feature in {"income", "annual_income", "monthly_income", "loan_amount",
                         "requested_amount", "loan_amount_requested", "coapplicant_income",
                         "monthly_debt", "property_value"}:
            current_display = f"${current_numeric:,.0f}"
            if direction == "decrease":
                suggested_display = f"≤ ${suggested_value:,.0f}"
            else:
                suggested_display = f"≥ ${suggested_value:,.0f}"
        elif feature in {"previous_defaults", "existing_mortgages", "num_dependents",
                         "num_credit_lines"}:
            suggested_value = int(round(suggested_value))
            current_display = str(int(current_numeric))
            suggested_display = f"≤ {suggested_value}" if direction == "decrease" else f"≥ {suggested_value}"
        else:
            current_display = f"{current_numeric:.2f}"
            if direction == "decrease":
                suggested_display = f"≤ {suggested_value:.2f}"
            else:
                suggested_display = f"≥ {suggested_value:.2f}"

        return {
            "feature": feature,
            "display_name": display_name,
            "current_value": current_numeric,
            "current_display": current_display,
            "suggested_value": suggested_value,
            "suggested_display": suggested_display,
            "direction": direction,
            "impact_score": abs(float(shap_value)),
            "impact_rank": "high" if abs(shap_value) > 0.1 else "medium",
        }
