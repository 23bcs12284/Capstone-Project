import pytest
import numpy as np
import pandas as pd
from models.classifiers import get_classifier_by_name

@pytest.fixture
def dummy_train_test_data():
    np.random.seed(42)
    # Generate 100 samples, 10 features
    X = pd.DataFrame(np.random.normal(size=(100, 10)), columns=[f"feat_{i}" for i in range(10)])
    y = pd.Series(np.random.choice([0, 1], size=100))
    return X, y

def test_classifiers_fit_predict(dummy_train_test_data):
    X, y = dummy_train_test_data
    
    # Test a representative sample of classifiers
    classifier_names = ["logistic_regression", "decision_tree", "random_forest", "xgboost", "lightgbm"]
    
    for name in classifier_names:
        clf = get_classifier_by_name(name)
        assert clf.is_fitted is False
        
        # Train
        clf.fit(X, y)
        assert clf.is_fitted is True
        assert clf.train_time > 0
        
        # Predict
        preds = clf.predict(X)
        assert len(preds) == 100
        assert np.isin(preds, [0, 1]).all()
        
        # Predict Proba
        probs = clf.predict_proba(X)
        assert probs.shape == (100, 2)
        assert (probs >= 0.0).all() and (probs <= 1.0).all()
