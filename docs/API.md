# API Reference — Explainable AI Loan Approval Prediction System

**Base URL:** `http://localhost:8000`  
**Authentication:** JWT Bearer Token (except `/auth/*` and `/health`)  
**Content-Type:** `application/json`

---

## Authentication Endpoints

### POST `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "message": "User registered successfully"
}
```

**Errors:** `400` — Username or email already exists.

---

### POST `/auth/login`

Authenticate and receive a JWT access token.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:** `401` — Invalid credentials.

---

## Prediction Endpoints

### POST `/predict`

Submit a loan application for approval prediction. **Requires authentication.**

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "age": 35,
  "income": 75000,
  "loan_amount": 25000,
  "credit_score": 720,
  "employment_length": 8,
  "debt_to_income": 0.32,
  "num_credit_lines": 5,
  "gender": "Male",
  "race": "White",
  "education": "Bachelor",
  "home_ownership": "Own",
  "loan_purpose": "Home Improvement"
}
```

**Response (200):**
```json
{
  "prediction_id": 42,
  "approval_status": "Approved",
  "approval_probability": 0.8734,
  "risk_score": 0.1266,
  "model_version": "logistic_regression_v1",
  "timestamp": "2026-07-18T12:30:00Z"
}
```

**Errors:** `422` — Validation error (missing/invalid fields).

---

### GET `/explain/{id}`

Retrieve SHAP and LIME explanations for a specific prediction. **Requires authentication.**

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:** `id` — The prediction ID (integer).

**Response (200):**
```json
{
  "prediction_id": 42,
  "shap_values": {
    "credit_score": 0.234,
    "income": 0.189,
    "debt_to_income": -0.156,
    "loan_amount": -0.098,
    "age": 0.067
  },
  "shap_base_value": 0.52,
  "lime_explanation": {
    "features": [
      {"feature": "credit_score > 700", "weight": 0.28},
      {"feature": "income > 60000", "weight": 0.21},
      {"feature": "debt_to_income <= 0.35", "weight": 0.15}
    ],
    "intercept": 0.48,
    "score": 0.87,
    "local_prediction": 0.8734
  },
  "top_positive_features": ["credit_score", "income", "age"],
  "top_negative_features": ["debt_to_income", "loan_amount"]
}
```

**Errors:** `404` — Prediction not found.

---

## Analytics & History Endpoints

### GET `/analytics`

Retrieve aggregated prediction statistics. **Requires authentication.**

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "total_predictions": 1250,
  "approval_rate": 0.682,
  "average_probability": 0.6543,
  "predictions_today": 47,
  "model_version": "logistic_regression_v1",
  "fairness_summary": {
    "demographic_parity_difference": 0.042,
    "equalized_odds_difference": 0.038
  }
}
```

---

### GET `/history`

Retrieve the authenticated user's prediction history. **Requires authentication.**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `per_page` | int | 20 | Results per page |
| `sort_by` | string | `timestamp` | Sort field |
| `order` | string | `desc` | Sort order (`asc` / `desc`) |

**Response (200):**
```json
{
  "predictions": [
    {
      "id": 42,
      "approval_status": "Approved",
      "approval_probability": 0.8734,
      "timestamp": "2026-07-18T12:30:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 20
}
```

---

## Model & System Endpoints

### GET `/model/metadata`

Retrieve information about the currently loaded model. **Requires authentication.**

**Response (200):**
```json
{
  "model_name": "Logistic Regression",
  "model_version": "logistic_regression_v1",
  "roc_auc": 0.9121,
  "accuracy": 0.8934,
  "training_date": "2026-07-18",
  "features_count": 15,
  "training_samples": 8000
}
```

---

### GET `/health`

System health check endpoint. **No authentication required.**

**Response (200):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true,
  "uptime_seconds": 3600,
  "version": "1.0.0"
}
```

---

## Error Response Format

All error responses follow a consistent structure:

```json
{
  "detail": "Human-readable error description",
  "status_code": 422,
  "error_type": "ValidationError"
}
```

## Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request |
| `401` | Unauthorized |
| `404` | Not Found |
| `422` | Validation Error |
| `500` | Internal Server Error |

---

> **Interactive docs:** Visit `http://localhost:8000/docs` for Swagger UI.  
> **See also:** [SETUP.md](./SETUP.md) · [DATABASE.md](./DATABASE.md)
