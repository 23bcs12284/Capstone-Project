import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # admin, user
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")


class LoanApplication(Base):
    __tablename__ = "loan_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(String(50), index=True, nullable=False)
    gender = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False)
    age_group = Column(String(20), nullable=False)
    race = Column(String(50), nullable=False)
    income = Column(Float, nullable=False)
    coapplicant_income = Column(Float, nullable=False)
    credit_score = Column(Integer, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_term = Column(Integer, nullable=False)
    employment_years = Column(Float, nullable=False)
    home_ownership = Column(String(50), nullable=False)
    education = Column(String(50), nullable=False)
    self_employed = Column(String(20), nullable=False)
    dependents = Column(String(20), nullable=False)
    property_area = Column(String(50), nullable=False)
    dti = Column(Float, nullable=False)
    
    # Actual/Historical target if known, else Null
    status = Column(Integer, nullable=True)  # 1 approved, 0 denied, Null if pending review
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    prediction = relationship("Prediction", back_populates="loan_application", uselist=False)


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    predicted_status = Column(Integer, nullable=False)  # 1 approved, 0 denied
    probability = Column(Float, nullable=False)  # probability of approval
    model_version = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    loan_application = relationship("LoanApplication", back_populates="prediction")
    explanation = relationship("Explanation", back_populates="prediction", uselist=False)


class Explanation(Base):
    __tablename__ = "explanations"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    # Store LIME/SHAP local explanations as JSON strings for dashboard usage
    shap_explanation_json = Column(Text, nullable=True)
    lime_explanation_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    prediction = relationship("Prediction", back_populates="explanation")


class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    metrics_json = Column(Text, nullable=False)  # Store summary validation metrics
    params_json = Column(Text, nullable=False)   # Store hyperparams used
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable if action is system/anonymous
    action = Column(String(100), nullable=False)  # e.g., "prediction", "login", "mitigation_applied"
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
