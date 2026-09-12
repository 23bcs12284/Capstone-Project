import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import User, LoanApplication, Prediction, Explanation, ModelVersion, AuditLog
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseRepository:
    @staticmethod
    def create_user(db: Session, username: str, password_hash: str, role: str = "user") -> User:
        user = User(username=username, password_hash=password_hash, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_loan_application(db: Session, application_data: Dict[str, Any]) -> LoanApplication:
        app = LoanApplication(**application_data)
        db.add(app)
        db.commit()
        db.refresh(app)
        return app

    @staticmethod
    def create_prediction(
        db: Session, 
        loan_application_id: int, 
        predicted_status: int, 
        probability: float, 
        model_version: str
    ) -> Prediction:
        prediction = Prediction(
            loan_application_id=loan_application_id,
            predicted_status=predicted_status,
            probability=probability,
            model_version=model_version
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction

    @staticmethod
    def create_explanation(
        db: Session, 
        prediction_id: int, 
        shap_explanation: Optional[Dict[str, Any]] = None, 
        lime_explanation: Optional[List[Dict[str, Any]]] = None
    ) -> Explanation:
        explanation = Explanation(
            prediction_id=prediction_id,
            shap_explanation_json=json.dumps(shap_explanation) if shap_explanation else None,
            lime_explanation_json=json.dumps(lime_explanation) if lime_explanation else None
        )
        db.add(explanation)
        db.commit()
        db.refresh(explanation)
        return explanation

    @staticmethod
    def create_audit_log(db: Session, user_id: Optional[int], action: str, details: Optional[str] = None) -> AuditLog:
        log = AuditLog(user_id=user_id, action=action, details=details)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_predictions_history(db: Session, limit: int = 100) -> List[Prediction]:
        """
        Retrieves prediction history with application data joined.
        """
        return db.query(Prediction)\
                 .join(LoanApplication)\
                 .order_by(desc(Prediction.created_at))\
                 .limit(limit)\
                 .all()

    @staticmethod
    def get_prediction_by_id(db: Session, prediction_id: int) -> Optional[Prediction]:
        return db.query(Prediction).filter(Prediction.id == prediction_id).first()

    @staticmethod
    def create_model_version(
        db: Session, 
        version: str, 
        name: str, 
        metrics: Dict[str, float], 
        params: Dict[str, Any]
    ) -> ModelVersion:
        # Deactivate all other versions if this is active
        mv = ModelVersion(
            version=version,
            name=name,
            metrics_json=json.dumps(metrics),
            params_json=json.dumps(params),
            is_active=True
        )
        # Set all others inactive
        db.query(ModelVersion).update({ModelVersion.is_active: False})
        db.add(mv)
        db.commit()
        db.refresh(mv)
        return mv

    @staticmethod
    def get_active_model_version(db: Session) -> Optional[ModelVersion]:
        return db.query(ModelVersion).filter(ModelVersion.is_active == True).first()

    @staticmethod
    def get_all_model_versions(db: Session) -> List[ModelVersion]:
        return db.query(ModelVersion).order_by(desc(ModelVersion.created_at)).all()

    @staticmethod
    def get_audit_logs(db: Session, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit).all()
