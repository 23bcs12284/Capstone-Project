import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List

REQUIRED_COLS = {
    "gender": str,
    "age": int,
    "race": str,
    "income": float,
    "coapplicant_income": float,
    "credit_score": int,
    "loan_amount": float,
    "loan_term": int,
    "employment_years": float,
    "home_ownership": str,
    "education": str,
    "self_employed": str,
    "dependents": str,
    "property_area": str,
    "dti": float
}

CATEGORICAL_VALUES = {
    "gender": ["Male", "Female"],
    "race": ["Caucasian", "African American", "Asian", "Hispanic"],
    "home_ownership": ["Own", "Mortgage", "Rent"],
    "education": ["Graduate", "Undergraduate"],
    "self_employed": ["Yes", "No"],
    "dependents": ["0", "1", "2", "3+"],
    "property_area": ["Urban", "Semiurban", "Rural"]
}

def validate_dataframe(df: pd.DataFrame, is_training: bool = True) -> Tuple[bool, List[str]]:
    """
    Validates a pandas DataFrame against required columns, types, and categorical constraints.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    
    # Check columns
    for col, expected_type in REQUIRED_COLS.items():
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
            continue
            
        # Basic type checking (or coercion check)
        if df[col].isnull().all():
            errors.append(f"Column {col} is completely null.")
            
    if is_training and "loan_status" not in df.columns:
        errors.append("Missing target label 'loan_status' for training.")
        
    # Check categorical values
    for col, allowed_vals in CATEGORICAL_VALUES.items():
        if col in df.columns:
            invalid_vals = df[~df[col].isin(allowed_vals) & df[col].notnull()][col].unique()
            if len(invalid_vals) > 0:
                errors.append(f"Column '{col}' has invalid categorical values: {invalid_vals}. Allowed: {allowed_vals}")
                
    # Range validations
    if "age" in df.columns:
        if (df["age"] < 18).any() or (df["age"] > 100).any():
            errors.append("Age values must be between 18 and 100.")
            
    if "credit_score" in df.columns:
        if (df["credit_score"] < 300).any() or (df["credit_score"] > 850).any():
            errors.append("Credit score must be between 300 and 850.")
            
    if "dti" in df.columns:
        if (df["dti"] < 0).any():
            errors.append("DTI ratio cannot be negative.")
            
    for col in ["income", "coapplicant_income", "loan_amount", "employment_years"]:
        if col in df.columns:
            if (df[col] < 0).any():
                errors.append(f"Column '{col}' cannot contain negative values.")
                
    return len(errors) == 0, errors

def validate_input_dict(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates a single inference input payload dictionary.
    """
    errors = []
    
    # Check missing keys
    for col, expected_type in REQUIRED_COLS.items():
        if col not in data:
            errors.append(f"Missing input field: {col}")
            continue
            
        val = data[col]
        # Validate types
        if expected_type == int:
            try:
                int(val)
            except (ValueError, TypeError):
                errors.append(f"Field '{col}' must be an integer, got: {val}")
        elif expected_type == float:
            try:
                float(val)
            except (ValueError, TypeError):
                errors.append(f"Field '{col}' must be a float, got: {val}")
        elif expected_type == str:
            if not isinstance(val, str):
                errors.append(f"Field '{col}' must be a string, got: {val}")
                
    # Check categorical constraints
    for col, allowed_vals in CATEGORICAL_VALUES.items():
        if col in data and str(data[col]) not in allowed_vals:
            errors.append(f"Field '{col}' value '{data[col]}' is not in allowed list: {allowed_vals}")
            
    # Range checks
    if "age" in data:
        try:
            age = int(data["age"])
            if age < 18 or age > 100:
                errors.append("Age must be between 18 and 100.")
        except (ValueError, TypeError):
            pass
            
    if "credit_score" in data:
        try:
            score = int(data["credit_score"])
            if score < 300 or score > 850:
                errors.append("Credit score must be between 300 and 850.")
        except (ValueError, TypeError):
            pass
            
    for col in ["income", "coapplicant_income", "loan_amount", "employment_years", "dti"]:
        if col in data:
            try:
                val = float(data[col])
                if val < 0:
                    errors.append(f"Field '{col}' cannot be negative.")
            except (ValueError, TypeError):
                pass
                
    return len(errors) == 0, errors
