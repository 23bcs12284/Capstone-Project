import pathlib

# Resolve paths relative to the project root
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()

DATASET_CONFIGS = {
    "loan_data": {
        "name": "General Loan Dataset",
        "path": "dataset/loan_data.csv",
        "target_column": "loan_status",
        "id_column": "applicant_id",
        "drop_columns": ["applicant_id", "age_group"],  # columns to drop before training
        "numeric_features": ["age", "income", "coapplicant_income", "credit_score", "loan_amount", "loan_term", "employment_years", "dti"],
        "categorical_features": ["gender", "race", "home_ownership", "education", "self_employed", "dependents", "property_area"],
        "protected_attributes": ["gender", "age_group", "race"],
        "description": "Synthetic general-purpose loan dataset with 5000 applications including demographic features for fairness analysis."
    },
    "home_loan_data": {
        "name": "Home Loan Dataset",
        "path": "dataset/home_loan_data.csv",
        "target_column": "loan_approved",
        "id_column": "application_id",
        "drop_columns": ["application_id"],
        "numeric_features": [
            "annual_income", "monthly_debt", "fico_score", "requested_amount", 
            "property_value", "employment_length", "loan_term_years", 
            "down_payment_pct", "existing_mortgages", "num_dependents"
        ],
        "categorical_features": [
            "loan_purpose", "home_type", "marital_status", "education_level"
        ],
        "protected_attributes": [],
        "description": "Synthetic home loan dataset focused on financial and property characteristics without protected demographic attributes."
    },
    "personal_loan_data": {
        "name": "Personal Loan Dataset",
        "path": "dataset/personal_loan_data.csv",
        "target_column": "loan_approved",
        "id_column": "app_id",
        "drop_columns": ["app_id"],
        "numeric_features": [
            "age", "monthly_income", "credit_history_length", "credit_score",
            "num_credit_lines", "loan_amount", "interest_rate", "years_at_job",
            "annual_income", "dti_ratio", "previous_defaults"
        ],
        "categorical_features": [
            "loan_purpose", "employment_status", "has_cosigner", "loan_grade"
        ],
        "protected_attributes": [],
        "description": "Synthetic personal loan dataset focused on individual financial metrics and credit history."
    }
}

def get_dataset_config(dataset_id: str) -> dict:
    """Returns the configuration for the specified dataset ID."""
    if dataset_id not in DATASET_CONFIGS:
        raise ValueError(f"Dataset ID '{dataset_id}' not found.")
    return DATASET_CONFIGS[dataset_id]

def get_all_dataset_ids() -> list:
    """Returns a list of all available dataset IDs."""
    return list(DATASET_CONFIGS.keys())

def get_dataset_path(dataset_id: str) -> str:
    """Returns the absolute path to the dataset file."""
    config = get_dataset_config(dataset_id)
    return str(PROJECT_ROOT / config["path"])
