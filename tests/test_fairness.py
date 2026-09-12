import pytest
import numpy as np
import pandas as pd
from fairness.auditor import FairnessAuditor
from fairness.mitigator import BiasMitigator

@pytest.fixture
def biased_dataset():
    # Construct a dataset with explicit gender bias in predictions
    # Male: 80% approval rate
    # Female: 40% approval rate
    np.random.seed(42)
    
    n_male = 100
    n_female = 100
    
    genders = ["Male"] * n_male + ["Female"] * n_female
    y_true = [1] * 70 + [0] * 30 + [1] * 50 + [0] * 50 # ground truth
    y_pred = [1] * 80 + [0] * 20 + [1] * 40 + [0] * 60 # predicted labels
    
    df = pd.DataFrame({
        "gender": genders,
        "loan_status": y_true,
        "predicted_status": y_pred
    })
    return df

def test_fairness_audit(biased_dataset):
    auditor = FairnessAuditor(protected_attributes=["gender"])
    audit_res = auditor.audit(biased_dataset, y_true_col="loan_status", y_pred_col="predicted_status")
    
    assert "gender" in audit_res
    gender_audit = audit_res["gender"]
    
    # Check selection rates
    group_metrics = gender_audit["group_metrics"]
    assert group_metrics["Male"]["selection_rate"] == 0.8
    assert group_metrics["Female"]["selection_rate"] == 0.4
    
    # Check parity ratios and differences
    assert gender_audit["demographic_parity_ratio"] == 0.5 # 0.4 / 0.8
    assert gender_audit["demographic_parity_difference"] == 0.4 # 0.8 - 0.4
    
    # Assert bias recommendations were generated
    assert len(gender_audit["recommendations"]) > 0
    assert any("Significant bias detected" in r for r in gender_audit["recommendations"])

def test_reweighing_weights(biased_dataset):
    # Apply reweighing mitigator
    weights = BiasMitigator.compute_reweighing_weights(
        biased_dataset, 
        protected_attribute="gender", 
        target_col="loan_status"
    )
    
    assert len(weights) == len(biased_dataset)
    assert (weights > 0).all()
    # Check that sum of weights equals N (approx due to floating points)
    assert pytest.approx(weights.sum(), rel=1e-5) == len(biased_dataset)
    
    # Weighted joint distributions of target and protected attributes should be independent
    # i.e. count(Male, Approved)*W should match expected marginals
    # Let's verify that reweighted group sizes scale correctly
    biased_dataset["w"] = weights
    grouped = biased_dataset.groupby(["gender", "loan_status"])["w"].sum()
    
    # For Male (100 samples) and Female (100 samples), 
    # and loan_status (120 approved, 80 denied in total),
    # in a perfectly independent distribution, we expect:
    # Male Approved: 100 * (120/200) = 60
    # Female Approved: 100 * (120/200) = 60
    assert pytest.approx(grouped[("Male", 1)], rel=1e-5) == 60.0
    assert pytest.approx(grouped[("Female", 1)], rel=1e-5) == 60.0

def test_threshold_calibration():
    # Generate mock probabilities where group B has lower scores
    np.random.seed(42)
    group_A_probs = np.random.uniform(0.3, 0.9, size=100)
    group_B_probs = np.random.uniform(0.1, 0.7, size=100)
    
    probs = np.concatenate([group_A_probs, group_B_probs])
    attrs = np.array(["A"] * 100 + ["B"] * 100)
    y_true = np.where(probs >= 0.5, 1, 0)
    
    thresholds = BiasMitigator.find_fair_thresholds(
        y_true, 
        probs, 
        attrs, 
        metric="demographic_parity"
    )
    
    assert "A" in thresholds
    assert "B" in thresholds
    
    # Group B has lower average scores, so its threshold should be calibrated lower to match the 55% target
    assert thresholds["B"] < thresholds["A"]
    
    # Apply thresholds
    y_pred = BiasMitigator.apply_fair_thresholds(probs, attrs, thresholds)
    assert len(y_pred) == 200
    assert np.isin(y_pred, [0, 1]).all()
