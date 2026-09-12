from abc import ABC, abstractmethod
import time
import logging
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseClassifier(ABC):
    """
    Abstract base class for all machine learning models in the loan approval system.
    """
    def __init__(self, name: str, model_instance: Any):
        self.name = name
        self.model = model_instance
        self.train_time = 0.0
        self.is_fitted = False

    @abstractmethod
    def fit(self, X: Any, y: Any) -> "BaseClassifier":
        """
        Fits the model.
        """
        pass

    def predict(self, X: Any) -> Any:
        """
        Predicts binary labels.
        """
        if not self.is_fitted:
            raise ValueError(f"Model {self.name} is not fitted yet.")
        return self.model.predict(X)

    def predict_proba(self, X: Any) -> Any:
        """
        Predicts class probabilities.
        """
        if not self.is_fitted:
            raise ValueError(f"Model {self.name} is not fitted yet.")
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        else:
            # Handle cases where model does not natively have predict_proba
            raise NotImplementedError(f"Model {self.name} does not support probability predictions.")

    def get_params(self) -> Dict[str, Any]:
        """
        Returns parameters of the model.
        """
        return self.model.get_params()

    def set_params(self, **params) -> "BaseClassifier":
        """
        Sets parameters of the model.
        """
        self.model.set_params(**params)
        return self
