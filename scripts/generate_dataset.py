import os
import numpy as np
import pandas as pd

def generate_loan_dataset(num_samples: int = 5000, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)
    
    # 1. Generate demographic features (protected attributes)
    genders = np.random.choice(["Male", "Female"], size=num_samples, p=[0.55, 0.45])
    
    # Age distributed around 40 years old
    ages = np.random.normal(loc=41, scale=12, size=num_samples).astype(int)
    ages = np.clip(ages, 18, 75)
    
    # Map age to age groups
    age_groups = []
    for age in ages:
        if age < 30:
            age_groups.append("Young")
        elif age <= 55:
            age_groups.append("Middle-aged")
        else:
            age_groups.append("Senior")
            
    races = np.random.choice(
        ["Caucasian", "African American", "Asian", "Hispanic"], 
        size=num_samples, 
        p=[0.60, 0.15, 0.10, 0.15]
    )
    
    # 2. Generate financial features
    # Base income depends on demographic features to represent systemic economic disparity
    base_income_factor = np.ones(num_samples)
    base_income_factor[genders == "Female"] -= 0.15
    base_income_factor[races == "African American"] -= 0.20
    base_income_factor[races == "Hispanic"] -= 0.10
    
    # Base income between 30k and 150k
    income = np.random.lognormal(mean=10.8, sigma=0.4, size=num_samples) * base_income_factor
    income = np.clip(income, 20000, 250000).round(-2)
    
    # Coapplicant income (40% have one)
    has_coapplicant = np.random.choice([0, 1], size=num_samples, p=[0.6, 0.4])
    coapplicant_income = np.zeros(num_samples)
    coapplicant_income[has_coapplicant == 1] = np.random.lognormal(mean=10.0, sigma=0.5, size=has_coapplicant.sum()).round(-2)
    coapplicant_income = np.clip(coapplicant_income, 0, 100000)
    
    # FICO Credit Score: 300 to 850.
    # Higher credit score slightly correlated with age and income
    credit_score_base = 550 + 1.5 * (ages - 18) + (income / 10000) * 8
    credit_score = np.random.normal(loc=credit_score_base, scale=60)
    credit_score = np.clip(credit_score, 300, 850).astype(int)
    
    # Loan amount: depends on income (realistic ratio 2x to 5.25x income)
    loan_amount = (income * 1.5 + coapplicant_income * 0.8) * np.random.uniform(2.0, 3.5, size=num_samples)
    loan_amount = np.clip(loan_amount, 20000, 750000).round(-2)
    
    # Loan term (mostly 360 months, some 180, 120)
    loan_term = np.random.choice([120, 180, 360], size=num_samples, p=[0.1, 0.15, 0.75])
    
    # Employment history (years)
    employment_years = np.clip(np.random.exponential(scale=5, size=num_samples) + (ages - 18) * 0.15, 0, 40).round(1)
    
    # Home ownership, education, self-employed, dependents, property area
    home_ownership = np.random.choice(["Own", "Mortgage", "Rent"], size=num_samples, p=[0.15, 0.50, 0.35])
    education = np.random.choice(["Graduate", "Undergraduate"], size=num_samples, p=[0.75, 0.25])
    self_employed = np.random.choice(["No", "Yes"], size=num_samples, p=[0.88, 0.12])
    dependents = np.random.choice(["0", "1", "2", "3+"], size=num_samples, p=[0.55, 0.20, 0.15, 0.10])
    property_area = np.random.choice(["Urban", "Semiurban", "Rural"], size=num_samples, p=[0.30, 0.45, 0.25])
    
    # 3. Calculate Debt-to-Income (DTI) ratio
    monthly_income = (income + coapplicant_income) / 12.0
    # Estimate monthly loan payment (simple rate rule of 6% annual interest)
    r = 0.06 / 12.0
    monthly_payment = loan_amount * (r * (1 + r)**loan_term) / ((1 + r)**loan_term - 1)
    dti = (monthly_payment / monthly_income).round(3)
    
    # 4. Generate Target Label: Loan Status (1 for Approved, 0 for Denied)
    # Define a score based on credit score, DTI, and income
    # Primary drivers of loan approval in real-world credit risk
    score = (
        (credit_score - 660) / 75.0  # Credit score (FICO) weight
        - (dti - 0.36) * 6.0          # Debt-to-income weight
        + np.log10((income + coapplicant_income) / 60000) * 1.5  # Income weight
        + (employment_years * 0.04)   # Employment years weight
        + np.where(education == "Graduate", 0.3, 0.0)
        + 0.35                         # Baseline intercept adjust
    )
    
    # Map qualitative features to score modifiers
    home_ownership_modifiers = {"Own": 0.5, "Mortgage": 0.2, "Rent": -0.2}
    score += np.vectorize(home_ownership_modifiers.get)(home_ownership)
    
    # Inject systemic demographic bias to simulate historical real-world loan discrimination
    # (So fairness audits can detect it and mitigation algorithms can be evaluated)
    bias_genders = np.where(genders == "Female", -0.35, 0.0)
    bias_races = np.where(races == "African American", -0.45, np.where(races == "Hispanic", -0.2, 0.0))
    bias_age = np.where(ages < 30, -0.3, 0.0)
    
    score += bias_genders + bias_races + bias_age
    
    # Add random noise to make prediction non-deterministic
    noise = np.random.normal(loc=0.0, scale=0.8, size=num_samples)
    final_score = score + noise
    
    # Standard Sigmoid mapping to probabilities
    prob = 1.0 / (1.0 + np.exp(-final_score))
    loan_status = np.where(prob >= 0.5, 1, 0)
    
    # Construct DataFrame
    df = pd.DataFrame({
        "applicant_id": [f"L{i:05d}" for i in range(1, num_samples + 1)],
        "gender": genders,
        "age": ages,
        "age_group": age_groups,
        "race": races,
        "income": income.astype(float),
        "coapplicant_income": coapplicant_income.astype(float),
        "credit_score": credit_score,
        "loan_amount": loan_amount.astype(float),
        "loan_term": loan_term,
        "employment_years": employment_years,
        "home_ownership": home_ownership,
        "education": education,
        "self_employed": self_employed,
        "dependents": dependents,
        "property_area": property_area,
        "dti": dti,
        "loan_status": loan_status
    })
    
    return df

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic loan dataset")
    parser.add_argument("--samples", type=int, default=5000, help="Number of loan applications to generate")
    parser.add_argument("--output", type=str, default="dataset/loan_data.csv", help="Output file path")
    args = parser.parse_args()
    
    print(f"Generating {args.samples} synthetic loan applications...")
    df = generate_loan_dataset(num_samples=args.samples)
    
    # Ensure parent folder exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Dataset successfully saved to: {args.output}")
    print(f"Positive approval rate: {df['loan_status'].mean():.2%}")
    print("Demographics distribution:")
    print(df['gender'].value_counts(normalize=True))
    print(df['race'].value_counts(normalize=True))
