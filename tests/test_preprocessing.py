import pytest
import pandas as pd
import numpy as np
from preprocessing.data_validator import validate_dataframe, validate_input_dict
from preprocessing.data_cleaner import DataCleaner
from feature_engineering.transformer import FeatureTransformer

@pytest.fixture
def sample_raw_data():
    return pd.DataFrame({
        "applicant_id": ["L00001", "L00002"],
        "gender": ["Male", "Female"],
        "age": [35, 22],
        "race": ["Caucasian", "African American"],
        "income": [60000.0, 45000.0],
        "coapplicant_income": [0.0, 2000.0],
        "credit_score": [710, 580],
        "loan_amount": [150000.0, 100000.0],
        "loan_term": [360, 180],
        "employment_years": [5.5, 1.2],
        "home_ownership": ["Mortgage", "Rent"],
        "education": ["Graduate", "Undergraduate"],
        "self_employed": ["No", "Yes"],
        "dependents": ["0", "1"],
        "property_area": ["Semiurban", "Rural"],
        "dti": [0.35, 0.42],
        "loan_status": [1, 0]
    })

def test_data_validation(sample_raw_data):
    # Valid dataframe
    is_valid, errors = validate_dataframe(sample_raw_data, is_training=True)
    assert is_valid is True
    assert len(errors) == 0

    # Invalid age
    invalid_df = sample_raw_data.copy()
    invalid_df.loc[0, "age"] = 15  # under 18
    is_valid, errors = validate_dataframe(invalid_df, is_training=True)
    assert is_valid is False
    assert any("Age values must be between 18 and 100" in e for e in errors)

def test_input_dict_validation():
    valid_dict = {
        "applicant_id": "L12345",
        "gender": "Male",
        "age": 30,
        "race": "Caucasian",
        "income": 50000.0,
        "coapplicant_income": 0.0,
        "credit_score": 700,
        "loan_amount": 100000.0,
        "loan_term": 360,
        "employment_years": 3.0,
        "home_ownership": "Own",
        "education": "Graduate",
        "self_employed": "No",
        "dependents": "0",
        "property_area": "Urban",
        "dti": 0.3
    }
    is_valid, errors = validate_input_dict(valid_dict)
    assert is_valid is True
    assert len(errors) == 0

    # Invalid categorical value
    invalid_dict = valid_dict.copy()
    invalid_dict["gender"] = "InvalidGender"
    is_valid, errors = validate_input_dict(invalid_dict)
    assert is_valid is False
    assert any("gender" in e for e in errors)

def test_data_cleaner(sample_raw_data):
    # Fit and transform
    cleaner = DataCleaner()
    cleaned_df = cleaner.fit_transform(sample_raw_data)
    
    assert cleaner.is_fitted is True
    assert cleaned_df.isnull().sum().sum() == 0
    assert (cleaned_df["income"] <= cleaner.clipping_thresholds["income"]).all()

def test_feature_transformer(sample_raw_data):
    # Clean first
    cleaner = DataCleaner()
    cleaned_df = cleaner.fit_transform(sample_raw_data)
    
    # Exclude non-feature columns
    X = cleaned_df.drop(columns=["applicant_id", "loan_status", "age_group"], errors="ignore")
    
    transformer = FeatureTransformer()
    X_trans = transformer.fit_transform(X)
    
    assert transformer.is_fitted is True
    assert "income" in X_trans.columns
    assert "gender_Male" in X_trans.columns
    assert "gender_Female" in X_trans.columns
    assert X_trans.isnull().sum().sum() == 0
