# Database Schema — Explainable AI Loan Approval Prediction System

## Overview

The system uses **SQLAlchemy ORM** with **SQLite** as the default backend (PostgreSQL-compatible).
The schema consists of **6 tables** that store users, loan applications, predictions,
explanations, model versions, and audit logs.

---

## Entity-Relationship Diagram

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│    Users     │──1:N──│  LoanApplications │──1:1──│  Predictions │
└──────────────┘       └──────────────────┘       └──────┬───────┘
                                                         │ 1:1
                                                   ┌─────┴───────┐
                                                   │ Explanations │
                                                   └─────────────┘

┌──────────────────┐       ┌──────────────┐
│  ModelVersions   │       │  AuditLogs   │
└──────────────────┘       └──────────────┘
```

---

## Table Definitions

### 1. Users

Stores registered user accounts for API authentication.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique user identifier |
| `username` | String(50) | Unique, Not Null | Login username |
| `email` | String(120) | Unique, Not Null | User email address |
| `hashed_password` | String(255) | Not Null | Bcrypt-hashed password |
| `is_active` | Boolean | Default: True | Account active status |
| `created_at` | DateTime | Default: now() | Registration timestamp |
| `updated_at` | DateTime | Auto-update | Last modification timestamp |

### 2. LoanApplications

Stores the raw input features for each loan application submitted.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique application identifier |
| `user_id` | Integer | FK → Users.id, Not Null | Submitting user |
| `age` | Integer | Not Null | Applicant age |
| `income` | Float | Not Null | Annual income |
| `loan_amount` | Float | Not Null | Requested loan amount |
| `credit_score` | Integer | Not Null | Credit score (300–850) |
| `employment_length` | Integer | Not Null | Years of employment |
| `debt_to_income` | Float | Not Null | Debt-to-income ratio |
| `num_credit_lines` | Integer | Not Null | Number of open credit lines |
| `gender` | String(20) | Nullable | Applicant gender |
| `race` | String(50) | Nullable | Applicant race/ethnicity |
| `education` | String(50) | Not Null | Education level |
| `home_ownership` | String(30) | Not Null | Home ownership status |
| `loan_purpose` | String(50) | Not Null | Purpose of the loan |
| `created_at` | DateTime | Default: now() | Submission timestamp |

### 3. Predictions

Stores the model's prediction output for each loan application.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique prediction identifier |
| `application_id` | Integer | FK → LoanApplications.id, Unique | Linked application |
| `approval_status` | String(20) | Not Null | "Approved" or "Denied" |
| `approval_probability` | Float | Not Null | Probability of approval (0–1) |
| `risk_score` | Float | Not Null | Complement of approval probability |
| `model_version` | String(100) | Not Null | Model identifier used |
| `created_at` | DateTime | Default: now() | Prediction timestamp |

### 4. Explanations

Stores SHAP and LIME explanation data for each prediction.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique explanation identifier |
| `prediction_id` | Integer | FK → Predictions.id, Unique | Linked prediction |
| `shap_values` | Text (JSON) | Nullable | SHAP feature contributions |
| `shap_base_value` | Float | Nullable | SHAP expected value |
| `lime_explanation` | Text (JSON) | Nullable | LIME feature weights and intercept |
| `top_positive_features` | Text (JSON) | Nullable | Features pushing toward approval |
| `top_negative_features` | Text (JSON) | Nullable | Features pushing toward denial |
| `created_at` | DateTime | Default: now() | Explanation generation timestamp |

### 5. ModelVersions

Tracks trained model artifacts and their performance metrics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique version identifier |
| `model_name` | String(100) | Not Null | Algorithm name |
| `version_tag` | String(100) | Unique, Not Null | Version identifier string |
| `accuracy` | Float | Not Null | Test set accuracy |
| `precision_score` | Float | Not Null | Test set precision |
| `recall` | Float | Not Null | Test set recall |
| `f1_score` | Float | Not Null | Test set F1 score |
| `roc_auc` | Float | Not Null | Test set ROC AUC |
| `file_path` | String(255) | Not Null | Path to serialized model file |
| `is_active` | Boolean | Default: False | Currently deployed model flag |
| `trained_at` | DateTime | Default: now() | Training completion timestamp |

### 6. AuditLogs

Records system events for compliance and debugging.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique log identifier |
| `user_id` | Integer | FK → Users.id, Nullable | Acting user (null for system events) |
| `action` | String(100) | Not Null | Action performed |
| `resource_type` | String(50) | Nullable | Type of resource affected |
| `resource_id` | Integer | Nullable | ID of the affected resource |
| `details` | Text (JSON) | Nullable | Additional context / metadata |
| `ip_address` | String(45) | Nullable | Client IP address |
| `created_at` | DateTime | Default: now() | Event timestamp |

---

## Relationships

| Relationship | Type | Description |
|-------------|------|-------------|
| Users → LoanApplications | One-to-Many | A user can submit multiple loan applications |
| LoanApplications → Predictions | One-to-One | Each application has exactly one prediction |
| Predictions → Explanations | One-to-One | Each prediction has one explanation record |
| Users → AuditLogs | One-to-Many | User actions are logged for auditing |

## Indexes

| Table | Columns | Type | Purpose |
|-------|---------|------|---------|
| Users | `username` | Unique | Fast lookup during authentication |
| Users | `email` | Unique | Duplicate prevention |
| Predictions | `application_id` | Unique | One prediction per application |
| Explanations | `prediction_id` | Unique | One explanation per prediction |
| AuditLogs | `created_at` | Index | Efficient time-range queries |
| AuditLogs | `user_id` | Index | User activity lookups |

---

> **See also:** [API.md](./API.md) · [ARCHITECTURE.md](./ARCHITECTURE.md)
