import os
import numpy as np
import pandas as pd

def generate_home_loan_dataset(num_samples: int = 3500, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)
    
    annual_income = np.random.uniform(25000, 300000, size=num_samples).round(2)
    monthly_debt = np.random.uniform(0, 5000, size=num_samples).round(2)
    
    # FICO score: correlate with income
    fico_base = 550 + (annual_income / 10000) * 5
    fico_score = np.random.normal(loc=fico_base, scale=50, size=num_samples)
    fico_score = np.clip(fico_score, 300, 850).astype(int)
    
    property_value = np.random.uniform(75000, 1200000, size=num_samples).round(2)
    
    # requested amount correlates with property value and down payment
    down_payment_pct = np.random.uniform(0.03, 0.25, size=num_samples).round(3)
    requested_amount = property_value * (1 - down_payment_pct)
    requested_amount = np.clip(requested_amount, 50000, 800000).round(2)
    
    employment_length = np.random.randint(0, 41, size=num_samples)
    
    loan_purpose = np.random.choice(['Purchase', 'Refinance', 'Home Improvement'], size=num_samples, p=[0.6, 0.3, 0.1])
    home_type = np.random.choice(['Single Family', 'Condo', 'Townhouse', 'Multi Family'], size=num_samples, p=[0.7, 0.15, 0.1, 0.05])
    marital_status = np.random.choice(['Single', 'Married', 'Divorced'], size=num_samples, p=[0.4, 0.45, 0.15])
    num_dependents = np.random.randint(0, 6, size=num_samples)
    education_level = np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], size=num_samples, p=[0.4, 0.4, 0.15, 0.05])
    loan_term_years = np.random.choice([15, 20, 30], size=num_samples, p=[0.2, 0.1, 0.7])
    existing_mortgages = np.random.randint(0, 4, size=num_samples)
    
    # Target label: Loan Approved
    # Drivers: fico_score, debt to income
    monthly_income = annual_income / 12
    dti = monthly_debt / monthly_income
    
    score = (
        (fico_score - 650) / 50.0
        - (dti - 0.36) * 5.0
        + np.log10(annual_income / 50000) * 1.2
        + (employment_length * 0.05)
        + down_payment_pct * 3.0
        - 1.5 # Intercept
    )
    
    noise = np.random.normal(0, 0.8, size=num_samples)
    final_score = score + noise
    
    prob = 1.0 / (1.0 + np.exp(-final_score))
    loan_approved = np.where(prob >= 0.5, 1, 0)
    
    df = pd.DataFrame({
        "application_id": [f"HL{i:05d}" for i in range(1, num_samples + 1)],
        "annual_income": annual_income,
        "monthly_debt": monthly_debt,
        "fico_score": fico_score,
        "requested_amount": requested_amount,
        "property_value": property_value,
        "employment_length": employment_length,
        "loan_purpose": loan_purpose,
        "home_type": home_type,
        "marital_status": marital_status,
        "num_dependents": num_dependents,
        "education_level": education_level,
        "loan_term_years": loan_term_years,
        "down_payment_pct": down_payment_pct,
        "existing_mortgages": existing_mortgages,
        "loan_approved": loan_approved
    })
    
    return df


def generate_personal_loan_dataset(num_samples: int = 4000, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)
    
    age = np.random.randint(21, 71, size=num_samples)
    monthly_income = np.random.uniform(2000, 25000, size=num_samples).round(2)
    annual_income = monthly_income * 12
    
    credit_history_length = np.clip(np.random.normal(age - 21, 5), 0, 30).astype(int)
    
    credit_score_base = 600 + (age - 30) * 2 + (monthly_income / 1000) * 5
    credit_score = np.random.normal(credit_score_base, 50, size=num_samples)
    credit_score = np.clip(credit_score, 300, 850).astype(int)
    
    num_credit_lines = np.random.randint(0, 21, size=num_samples)
    loan_amount = np.random.uniform(1000, 50000, size=num_samples).round(2)
    
    # Interest rate inversely correlated with credit score
    base_rate = 30.0 - (credit_score - 300) / 550 * 25.0
    interest_rate = np.clip(base_rate + np.random.normal(0, 2, size=num_samples), 5.0, 30.0).round(2)
    
    loan_purpose = np.random.choice(['Debt Consolidation', 'Education', 'Medical', 'Home Improvement', 'Other'], size=num_samples, p=[0.4, 0.2, 0.15, 0.15, 0.1])
    employment_status = np.random.choice(['Employed', 'Self-Employed', 'Retired', 'Unemployed'], size=num_samples, p=[0.7, 0.15, 0.1, 0.05])
    
    years_at_job = np.clip(np.random.normal(10, 8, size=num_samples), 0, 30).round(1)
    # Set years_at_job to 0 for unemployed
    years_at_job[employment_status == 'Unemployed'] = 0.0
    
    dti_ratio = np.random.uniform(0.0, 1.0, size=num_samples).round(3)
    has_cosigner = np.random.choice(['Yes', 'No'], size=num_samples, p=[0.2, 0.8])
    previous_defaults = np.random.choice([0, 1, 2, 3], size=num_samples, p=[0.8, 0.15, 0.04, 0.01])
    
    # Loan grade A,B,C,D,E based roughly on credit score
    loan_grade_mapped = pd.cut(credit_score, bins=[0, 550, 650, 720, 780, 900], labels=['E', 'D', 'C', 'B', 'A'])
    loan_grade = np.array(loan_grade_mapped).astype(str)
    
    # Target
    score = (
        (credit_score - 650) / 40.0
        - (dti_ratio - 0.4) * 6.0
        + np.log10(monthly_income / 4000) * 1.5
        - (previous_defaults * 1.5)
        + np.where(employment_status == 'Employed', 0.5, 0)
        + np.where(has_cosigner == 'Yes', 0.5, 0)
        - 0.3
    )
    
    noise = np.random.normal(0, 0.8, size=num_samples)
    final_score = score + noise
    
    prob = 1.0 / (1.0 + np.exp(-final_score))
    loan_approved = np.where(prob >= 0.5, 1, 0)
    
    df = pd.DataFrame({
        "app_id": [f"PL{i:05d}" for i in range(1, num_samples + 1)],
        "age": age,
        "monthly_income": monthly_income,
        "credit_history_length": credit_history_length,
        "credit_score": credit_score,
        "num_credit_lines": num_credit_lines,
        "loan_amount": loan_amount,
        "interest_rate": interest_rate,
        "loan_purpose": loan_purpose,
        "employment_status": employment_status,
        "years_at_job": years_at_job,
        "annual_income": annual_income,
        "dti_ratio": dti_ratio,
        "has_cosigner": has_cosigner,
        "previous_defaults": previous_defaults,
        "loan_grade": loan_grade,
        "loan_approved": loan_approved
    })
    
    return df

if __name__ == '__main__':
    hl_df = generate_home_loan_dataset()
    hl_out = '/Users/prabhakarkumarjha/Desktop/Capstone_project/dataset/home_loan_data.csv'
    os.makedirs(os.path.dirname(hl_out), exist_ok=True)
    hl_df.to_csv(hl_out, index=False)
    print(f"Generated Home Loan Dataset to {hl_out}")
    print(f"Home Loan Approval Rate: {hl_df['loan_approved'].mean():.2%}")
    
    pl_df = generate_personal_loan_dataset()
    pl_out = '/Users/prabhakarkumarjha/Desktop/Capstone_project/dataset/personal_loan_data.csv'
    pl_df.to_csv(pl_out, index=False)
    print(f"Generated Personal Loan Dataset to {pl_out}")
    print(f"Personal Loan Approval Rate: {pl_df['loan_approved'].mean():.2%}")
