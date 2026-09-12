import os
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from lime.lime_tabular import LimeTabularExplainer
from typing import Any, List, Dict, Callable

logger = logging.getLogger(__name__)

class LimeExplainerManager:
    def __init__(
        self, 
        X_train: pd.DataFrame, 
        feature_names: List[str] = None,
        class_names: List[str] = None
    ):
        self.X_train = X_train
        self.feature_names = feature_names or X_train.columns.tolist()
        self.class_names = class_names or ["Denied", "Approved"]
        
        # Identify categorical columns (if they are one-hot encoded, they are binary 0/1)
        # Tabular explainer works on numpy arrays
        self.explainer = LimeTabularExplainer(
            training_data=X_train.values,
            feature_names=self.feature_names,
            class_names=self.class_names,
            mode="classification",
            random_state=42
        )

    def explain_instance(
        self, 
        instance_series: pd.Series, 
        predict_fn: Callable[[np.ndarray], np.ndarray]
    ) -> Any:
        """
        Explains a single prediction instance.
        
        Args:
            instance_series: The preprocessed single instance as a Pandas Series (shape: (num_features,))
            predict_fn: The model's predict_proba function that accepts a numpy array of shape (N, num_features)
        """
        # Explainer expects a single instance as a 1D numpy array
        exp = self.explainer.explain_instance(
            data_row=instance_series.values,
            predict_fn=predict_fn,
            num_features=10
        )
        return exp

    def plot_and_save_explanation(
        self, 
        instance_series: pd.Series, 
        predict_fn: Callable[[np.ndarray], np.ndarray], 
        save_path: str
    ) -> None:
        """
        Generates and saves the LIME local explanation plot.
        """
        exp = self.explain_instance(instance_series, predict_fn)
        
        # Save as matplotlib figure
        fig = exp.as_pyplot_figure()
        plt.title("LIME Local Prediction Explanation", fontsize=12, pad=15)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close(fig)

    def save_explanation_html(
        self, 
        instance_series: pd.Series, 
        predict_fn: Callable[[np.ndarray], np.ndarray], 
        save_path: str
    ) -> str:
        """
        Saves LIME explanation as an interactive HTML file.
        """
        exp = self.explain_instance(instance_series, predict_fn)
        exp.save_to_file(save_path)
        return save_path

    def get_contributions(
        self, 
        instance_series: pd.Series, 
        predict_fn: Callable[[np.ndarray], np.ndarray]
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of dicts showing each feature's contribution and name.
        """
        exp = self.explain_instance(instance_series, predict_fn)
        # list of tuples (feature_index, weight)
        list_contributions = exp.as_list()
        
        contributions = []
        for feat, weight in list_contributions:
            contributions.append({
                "feature_rule": feat,
                "weight": float(weight),
                "direction": "Positive (Supports Approval)" if weight > 0 else "Negative (Supports Denial)"
            })
        return contributions
