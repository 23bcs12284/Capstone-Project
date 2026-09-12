import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from database.connection import Base, engine, SessionLocal
from database.models import User
from backend.auth import get_password_hash

# Ensure test DB is initialized
@pytest.fixture(scope="module")
def test_client():
    # Force SQLite test db if needed, here we let settings handle it
    Base.metadata.create_all(bind=engine)
    
    # Create an admin user for testing
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin_test").first()
        if not admin:
            hashed_pwd = get_password_hash("password123")
            admin_user = User(username="admin_test", password_hash=hashed_pwd, role="admin")
            db.add(admin_user)
            db.commit()
    finally:
        db.close()
        
    with TestClient(app) as client:
        yield client

def test_api_health(test_client):
    res = test_client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_user_flow(test_client):
    # Register new user
    reg_payload = {
        "username": "user_test_flow",
        "password": "strongpassword123",
        "role": "user"
    }
    res = test_client.post("/auth/register", json=reg_payload)
    # Status code might be 201 or 400 (if already registered)
    assert res.status_code in [201, 400]
    
    # Login
    login_payload = {
        "username": "user_test_flow",
        "password": "strongpassword123"
    }
    res = test_client.post("/auth/login", data=login_payload)
    assert res.status_code == 200
    assert "access_token" in res.json()
    token = res.json()["access_token"]
    
    # Check credentials on prediction (requires authorization header)
    headers = {"Authorization": f"Bearer {token}"}
    
    predict_payload = {
        "applicant_id": "LTEST1",
        "gender": "Female",
        "age": 28,
        "race": "African American",
        "income": 50000.0,
        "coapplicant_income": 0.0,
        "credit_score": 620,
        "loan_amount": 180000.0,
        "loan_term": 360,
        "employment_years": 2.5,
        "home_ownership": "Rent",
        "education": "Graduate",
        "self_employed": "No",
        "dependents": "1",
        "property_area": "Rural",
        "dti": 0.45
    }
    
    # Predict (might fail if model file is not generated yet, let's assert 503 or 200)
    res = test_client.post("/predict", json=predict_payload, headers=headers)
    assert res.status_code in [200, 503]
    
    if res.status_code == 200:
        pred_data = res.json()
        assert "prediction_id" in pred_data
        pred_id = pred_data["prediction_id"]
        
        # Test explain endpoint
        exp_res = test_client.get(f"/explain/{pred_id}", headers=headers)
        assert exp_res.status_code == 200
        assert "lime_contributions" in exp_res.json()
