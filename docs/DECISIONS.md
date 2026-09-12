# Architectural Decisions — Explainable AI Loan Approval Prediction System

This document records the key architectural and design decisions made during the development
of the project, along with the rationale behind each choice.

---

## ADR-001: SQLite as Default Database

**Decision:** Use SQLite as the default database backend.

**Context:** The system requires a relational database for persisting users, predictions,
explanations, and audit logs. Options considered: SQLite, PostgreSQL, MySQL.

**Rationale:**
- Zero-configuration setup — no external database server required
- Single-file database simplifies development, testing, and portability
- SQLAlchemy ORM abstracts the database layer, making migration to PostgreSQL trivial
- Sufficient performance for the expected workload (thousands of predictions)

**Trade-offs:**
- Limited concurrent write throughput compared to PostgreSQL
- Not suitable for multi-instance horizontal scaling without migration

**Status:** ✅ Accepted

---

## ADR-002: Synthetic Dataset over Real-World Data

**Decision:** Generate a synthetic loan dataset instead of using publicly available datasets.

**Context:** The project needed a labeled loan dataset with diverse features including
sensitive attributes for fairness analysis.

**Rationale:**
- Full control over feature distributions, class balance, and dataset size
- Avoids privacy concerns and data licensing restrictions
- Enables testing of edge cases (missing values, outliers, class imbalance)
- Sensitive attributes (gender, race, age) can be explicitly included for fairness auditing
- Reproducible generation ensures consistent results across environments

**Trade-offs:**
- Synthetic distributions may not perfectly reflect real-world lending patterns
- Model performance metrics are indicative, not directly comparable to production benchmarks

**Status:** ✅ Accepted

---

## ADR-003: Logistic Regression as Best Model

**Decision:** Select Logistic Regression as the production model over gradient boosting alternatives.

**Context:** Four models were trained and evaluated — Logistic Regression, XGBoost, LightGBM,
and CatBoost. Selection was based on ROC AUC on the held-out test set.

**Rationale:**
- Achieved the highest ROC AUC (0.9121) among all candidates
- Inherently interpretable — coefficients map directly to feature importance
- Faster inference time, ideal for real-time API predictions
- Lower memory footprint compared to ensemble models
- Better alignment with explainability goals (SHAP values are exact, not approximated)

**Trade-offs:**
- May underperform on highly non-linear decision boundaries in production data
- Limited capacity to model complex feature interactions without manual engineering

**Status:** ✅ Accepted

---

## ADR-004: Dynamic SHAP Explainer Selection

**Decision:** Implement a dynamic SHAP explainer that auto-selects the appropriate backend.

**Context:** SHAP provides multiple explainer backends (TreeExplainer, LinearExplainer,
KernelExplainer) optimized for different model types.

**Rationale:**
- TreeExplainer is used for tree-based models (XGBoost, LightGBM, CatBoost) — exact and fast
- LinearExplainer is used for linear models (Logistic Regression) — exact coefficients
- KernelExplainer serves as a universal fallback for any model type
- Dynamic selection future-proofs the system for new model architectures
- Single interface abstracts the complexity from the API and dashboard layers

**Trade-offs:**
- KernelExplainer fallback is significantly slower for large datasets
- Requires runtime model-type inspection logic

**Status:** ✅ Accepted

---

## ADR-005: Custom Fairness Auditor over Fairlearn Directly

**Decision:** Build a custom fairness auditing module that wraps and extends Fairlearn.

**Context:** The system needs to compute fairness metrics, generate structured reports,
and integrate with both the API and dashboard.

**Rationale:**
- Custom wrapper enables consistent report format (JSON-serializable) across all layers
- Adds configurable pass/fail thresholds not natively provided by Fairlearn's API
- Enables group-level performance breakdowns alongside fairness metrics
- Simplifies integration with SQLAlchemy for persisting audit results
- Allows extension with custom metrics beyond Fairlearn's built-in set

**Trade-offs:**
- Additional code to maintain compared to using Fairlearn directly
- Must be kept in sync with Fairlearn API changes across versions

**Status:** ✅ Accepted

---

## ADR-006: Streamlit over React for Dashboard

**Decision:** Use Streamlit for the presentation layer instead of a React-based SPA.

**Context:** The project requires an interactive dashboard for predictions, explanations,
and fairness visualizations.

**Rationale:**
- Pure Python — no JavaScript/TypeScript toolchain required
- Rapid prototyping with built-in widgets, layouts, and charting
- Native support for Plotly and Matplotlib visualizations
- Seamless integration with the Python ML and XAI layers
- Lower development complexity for a capstone-scoped project
- Built-in session state management and caching

**Trade-offs:**
- Limited customization compared to React (no component-level control)
- Less suitable for complex multi-user concurrent interactions
- Tied to Streamlit's deployment model and rendering cycle

**Status:** ✅ Accepted

---

## Decision Summary

| ID | Decision | Key Driver |
|----|----------|-----------|
| ADR-001 | SQLite as default DB | Zero-config portability |
| ADR-002 | Synthetic dataset | Privacy, control, reproducibility |
| ADR-003 | Logistic Regression best model | Highest ROC AUC + interpretability |
| ADR-004 | Dynamic SHAP explainer | Future-proof multi-model support |
| ADR-005 | Custom fairness auditor | Structured reporting + extensibility |
| ADR-006 | Streamlit over React | Python-native rapid development |

---

> **See also:** [ARCHITECTURE.md](./ARCHITECTURE.md) · [ML_PIPELINE.md](./ML_PIPELINE.md)
