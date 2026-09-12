# Research Notes

## Key Findings from the Explainable AI Loan Approval Prediction System

This document captures the most important discoveries, insights, and observations made during the development and evaluation of the project.

---

## Finding 1: Linear Models Outperform Ensembles on Well-Engineered Features

**Observation:** Logistic Regression achieved the highest ROC AUC (0.9121), surpassing ensemble models like XGBoost (0.9095) and Random Forest (0.9087).

**Analysis:** The 4 derived features (income_loan_ratio, total_income, log_loan_amount, credit_risk_score) effectively encode non-linear relationships that tree-based models would normally discover through splits. When features are carefully engineered, the added complexity of ensemble models provides diminishing returns while introducing overfitting risk on moderate-sized datasets.

**Implication:** Feature engineering quality can be more impactful than model complexity. This also benefits the explainability goal, as Logistic Regression provides native coefficient-based interpretability.

---

## Finding 2: Credit Score Dominates Feature Importance

**Observation:** Across SHAP, LIME, and native feature importance methods, `credit_score` consistently ranks as the #1 most influential feature, with a mean |SHAP value| of 0.1823 — approximately 25% higher than the second-ranked feature (`debt_to_income_ratio` at 0.1456).

**Analysis:** This aligns with domain knowledge: credit scores are designed to be predictive of repayment behavior. However, the dominance raises concerns about:
- Over-reliance on a single feature
- Potential bias encoded within credit scoring systems themselves
- Limited model utility beyond what a simple credit score threshold would provide

**Implication:** Future work should investigate model performance with credit score removed to assess the value of other features and reduce potential propagated bias.

---

## Finding 3: SHAP and LIME Agree on Top Features but Diverge on Ranks

**Observation:** SHAP and LIME both identify credit_score, debt_to_income_ratio, and income_loan_ratio as the top 3 features. However, feature rankings differ for features ranked 4-10, with a Spearman correlation of 0.78 between SHAP and LIME importance rankings.

**Analysis:** The divergence arises from fundamental methodological differences:
- SHAP uses Shapley values (exact game-theoretic attribution)
- LIME fits local linear models around perturbation samples
- LIME's discretization of continuous features can mask fine-grained relationships

**Implication:** Using both SHAP and LIME provides robustness to explainability claims. When rankings disagree, deeper investigation of the specific feature's relationship with the target is warranted.

---

## Finding 4: Demographic Disparities Are Subtle but Present

**Observation:** The model exhibits a Demographic Parity Difference of -0.0444 for race (Black vs. White) and -0.0289 for gender (Female vs. Male). All disparities fall within the commonly accepted 0.10 threshold but are non-zero.

**Analysis:** These disparities likely arise from:
- Correlation between protected attributes and legitimate features (e.g., income disparities correlated with race/gender)
- Historical bias in the training data reflecting systemic inequalities
- The proxy effect: seemingly neutral features like zip code or employment type may correlate with protected attributes

**Implication:** Even when meeting statistical thresholds, the presence of measurable disparities necessitates ongoing monitoring and transparent reporting. The reweighing mitigation reduced DPD by 50-60% without significant accuracy loss.

---

## Finding 5: Reweighing Is More Effective Than Threshold Adjustment

**Observation:** Pre-processing reweighing reduced DPD from -0.0444 to -0.0178 (60% reduction) with only 0.3% accuracy loss. Post-processing threshold adjustment achieved -0.0212 (52% reduction) but introduced prediction inconsistencies.

**Analysis:** Reweighing modifies the training process, allowing the model to learn debiased decision boundaries. Threshold adjustment applies group-specific cutoffs after training, which can feel arbitrary and harder to justify to regulators. Reweighing also generalizes better to unseen data distributions.

**Implication:** Pre-processing fairness interventions should be preferred when possible, as they modify the learned representation rather than applying post-hoc corrections.

---

## Finding 6: Derived Features Improve Both Performance and Interpretability

**Observation:** Adding 4 derived features improved ROC AUC by 0.018 (from 0.894 to 0.912) and made SHAP explanations more intuitive. `income_loan_ratio` is ranked 3rd globally and provides a more meaningful explanation than raw income or loan amount alone.

**Analysis:** Derived features that encode domain-relevant ratios and composite scores:
- Reduce the model's burden to discover these relationships
- Produce SHAP explanations that align with human financial reasoning
- Improve generalization by capturing scale-invariant relationships

**Implication:** Feature engineering should be guided by both statistical analysis and domain expertise. Features that make sense to human stakeholders improve both model quality and explainability.

---

## Finding 7: KNN Performs Poorly on High-Dimensional Encoded Data

**Observation:** K-Nearest Neighbors achieved the lowest ROC AUC (0.8812) among all 7 models, significantly underperforming even simple Logistic Regression.

**Analysis:** With 28 features after one-hot encoding, KNN suffers from the curse of dimensionality. Distance metrics become less meaningful in high-dimensional spaces, and the sparse categorical encoding creates misleading distances between points that differ only on categorical attributes.

**Implication:** KNN is unsuitable for datasets with extensive categorical encoding. If needed, dimensionality reduction (PCA) or feature selection should precede KNN application.

---

## Finding 8: The 80/20 Train-Test Split Maintains Class Balance

**Observation:** Stratified splitting preserved the original class distribution (52.3% Approved, 47.7% Denied) in both train and test sets. Cross-validation standard deviations remained below 0.02 for all models.

**Analysis:** Class balance reduces the need for aggressive resampling techniques (SMOTE, random oversampling) that can introduce synthetic artifacts. The `class_weight='balanced'` parameter in Logistic Regression further adjusts for any minor imbalance.

**Implication:** When working with reasonably balanced datasets, stratified splitting combined with class weighting is preferable to synthetic resampling.

---

## Methodology Notes

- All experiments used `random_state=42` for reproducibility
- Hyperparameter tuning used `GridSearchCV` with 5-fold stratified CV
- Statistical significance was not formally tested (future work item)
- Dataset size (~4,500 samples) limits conclusions about generalization to larger populations

---

## Open Questions

1. How would the model perform with external credit bureau data as additional features?
2. Can causal inference methods improve fairness beyond correlation-based mitigation?
3. What is the optimal trade-off between accuracy and fairness in this domain?
4. How do explanations change over time as the data distribution shifts?
