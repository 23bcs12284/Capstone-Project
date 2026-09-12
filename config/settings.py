import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Define base directory
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # App General Settings
    APP_NAME: str = "Explainable AI Loan Approval System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Server Host & Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Paths
    DATASET_PATH: str = str(BASE_DIR / "dataset" / "loan_data.csv")
    MODEL_DIR: str = str(BASE_DIR / "models_saved")
    MODEL_PATH: str = str(BASE_DIR / "models_saved" / "best_model.pkl")
    SCALER_PATH: str = str(BASE_DIR / "models_saved" / "scaler.pkl")
    ENCODER_PATH: str = str(BASE_DIR / "models_saved" / "encoder.pkl")
    ARTIFACTS_DIR: str = str(BASE_DIR / "artifacts")
    
    # Database
    # Standard SQLite for local ease-of-use, postgresql fully supported
    DATABASE_URL: str = "sqlite:///./loan_approval.db"
    
    # Backend Security
    JWT_SECRET: str = "supersecretkeychangeinproduction1234567890"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Fairness Settings
    PROTECTED_ATTRIBUTES: list[str] = ["gender", "age_group", "race"]
    FAVORABLE_LABEL: int = 1  # 1 for Approved, 0 for Rejected
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.MODEL_DIR, exist_ok=True)
os.makedirs(settings.ARTIFACTS_DIR, exist_ok=True)
