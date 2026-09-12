import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field(default="user")

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PredictRequest(BaseModel):
    dataset_id: str
    model_name: str
    threshold: float = 0.5
    features: Dict[str, Any]

class CounterfactualSuggestion(BaseModel):
    feature: str
    display_name: str
    current_value: float
    current_display: str
    suggested_value: float
    suggested_display: str
    direction: str
    impact_score: float
    impact_rank: str

class CounterfactualData(BaseModel):
    decision: str
    suggestions: List[CounterfactualSuggestion]
    disclaimer: str
    num_suggestions: int

class PredictResponse(BaseModel):
    prediction: int
    probability: float
    risk_level: str
    confidence: float
    positive_factors: List[Dict[str, Any]]
    negative_factors: List[Dict[str, Any]]
    counterfactual: Optional[CounterfactualData] = None
