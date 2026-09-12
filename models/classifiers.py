import time
import logging
from typing import Any
from models.base_model import BaseClassifier

# Import Scikit-Learn Classifiers
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.svm import SVC

# Import Gradient Boosting Libraries
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

logger = logging.getLogger(__name__)

class LogisticRegressionModel(BaseClassifier):
    def __init__(self, **kwargs):
        super().__init__("Logistic Regression", LogisticRegression(max_iter=1000, **kwargs))

    def fit(self, X: Any, y: Any) -> "LogisticRegressionModel":
        start_time = time.time()
        logger.info("Training Logistic Regression model...")
        self.model.fit(X, y)
        self.train_time = time.time() - start_time
        self.is_fitted = True
        return self


class DecisionTreeModel(BaseClassifier):
    def __init__(self, **kwargs):
        super().__init__("Decision Tree", DecisionTreeClassifier(**kwargs))

    def fit(self, X: Any, y: Any) -> "DecisionTreeModel":
        start_time = time.time()
        logger.info("Training Decision Tree model...")
        self.model.fit(X, y)
        self.train_time = time.time() - start_time
        self.is_fitted = True
        return self


class RandomForestModel(BaseClassifier):
    def __init__(self, **kwargs):
        super().__init__("Random Forest", RandomForestClassifier(**kwargs))

    def fit(self, X: Any, y: Any) -> "RandomForestModel":
        start_time = time.time()
        logger.info("Training Random Forest model...")
        self.model.fit(X, y)
        self.train_time = time.time() - start_time
        self.is_fitted = True
        return self


class GradientBoostingModel(BaseClassifier):
    def __init__(self, **kwargs):
        super().__init__("Gradient Boosting", GradientBoostingClassifier(**kwargs))

    def fit(self, X: Any, y: Any) -> "GradientBoostingModel":
        start_time = time.time()
        logger.info("Training Gradient Boosting model...")
        self.model.fit(X, y)
        self.train_time = time.time() - start_time
        self.is_fitted = True
        return self


class XGBoostModel(BaseClassifier):
    def __init__(self, **kwargs):
        # standard classification default objective
        super().__init__("XGBoost", XGBClassifier(use_label_encoder=False, eval_metric="logloss", **kwargs))

    def fit(self, X: Any, y: Any) -> "XGBoostModel":
        start_time = time.time()
        logger.info("Training XGBoost model...")
        self.model.fit(X, y)
        self.train_time = time.time() - start_time
        self.is_fitted = True
        return self


class LightGBMModel(BaseClassifier):
    def __init__(self, **kwargs):
        # suppress LGBM warnings unless debug
        super().__init__("LightGBM", LGBMClassifier(verbose=-1, **kwargs))

    def fit(self, X: Any, y: Any) -> "LightGBMModel":
        start_time = time.time()
        logger.info("Training LightGBM model...")
        self.model.fit(X, y)
        self.train_time = time.time() - start_time
        self.is_fitted = True
        return self


class CatBoostModel(BaseClassifier):
    def __init__(self, **kwargs):
        # Set default verbose to 0 to prevent training logs cluttering console
        if 'verbose' not in kwargs:
            kwargs['verbose'] = 0
        super().__init__("CatBoost", CatBoostClassifier(**kwargs))

    def fit(self, X: Any, y: Any) -> "CatBoostModel":
        start_time = time.time()
        logger.info("Training CatBoost model...")
        self.model.fit(X, y)
        self.train_time = time.time() - start_time
        self.is_fitted = True
        return self

class SVMModel(BaseClassifier):
    def __init__(self, **kwargs):
        super().__init__("SVM", SVC(probability=True, **kwargs))

    def fit(self, X: Any, y: Any) -> "SVMModel":
        start_time = time.time()
        logger.info("Training SVM model...")
        self.model.fit(X, y)
        self.train_time = time.time() - start_time
        self.is_fitted = True
        return self

class ExtraTreesModel(BaseClassifier):
    def __init__(self, **kwargs):
        super().__init__("Extra Trees", ExtraTreesClassifier(**kwargs))

    def fit(self, X: Any, y: Any) -> "ExtraTreesModel":
        start_time = time.time()
        logger.info("Training Extra Trees model...")
        self.model.fit(X, y)
        self.train_time = time.time() - start_time
        self.is_fitted = True
        return self


def get_classifier_by_name(name: str, **kwargs) -> BaseClassifier:
    classifiers = {
        "logistic_regression": LogisticRegressionModel,
        "decision_tree": DecisionTreeModel,
        "random_forest": RandomForestModel,
        "gradient_boosting": GradientBoostingModel,
        "xgboost": XGBoostModel,
        "lightgbm": LightGBMModel,
        "catboost": CatBoostModel,
        "svm": SVMModel,
        "extra_trees": ExtraTreesModel
    }
    key = name.lower().replace(" ", "_")
    if key not in classifiers:
        raise ValueError(f"Classifier {name} is not supported. Choose from {list(classifiers.keys())}")
    return classifiers[key](**kwargs)
