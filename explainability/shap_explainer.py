import os
import shap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set backend to avoid UI thread issues
import matplotlib.pyplot as plt
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

class ShapExplainerManager:
    def __init__(self, model: Any, X_train: pd.DataFrame):
        self.model = model
        self.X_train = X_train
        self.explainer = self._init_explainer()

    def _init_explainer(self) -> Any:
        """
        Dynamically initializes the appropriate SHAP explainer.
        """
        model_type = type(self.model).__name__
        logger.info(f"Initializing SHAP explainer for model type: {model_type}")
        
        try:
            if "LogisticRegression" in model_type:
                return shap.LinearExplainer(self.model, self.X_train)
            elif any(tree_type in model_type for tree_type in ["XGB", "LGBM", "CatBoost", "RandomForest", "DecisionTree", "ExtraTrees", "GradientBoosting"]):
                try:
                    return shap.TreeExplainer(self.model)
                except Exception as te:
                    logger.warning(f"TreeExplainer without data failed: {te}. Retrying with background sample...")
                    return shap.TreeExplainer(self.model, data=self.X_train.sample(min(20, len(self.X_train)), random_state=42) if len(self.X_train) > 20 else self.X_train)
            else:
                background = shap.sample(self.X_train, min(10, len(self.X_train)))
                return shap.KernelExplainer(self.model.predict_proba, background)
        except Exception as e:
            logger.warning(f"SHAP initialization failed: {str(e)}. Falling back to fast Kernel SHAP...")
            background = shap.sample(self.X_train, min(10, len(self.X_train)))
            return shap.KernelExplainer(self.model.predict_proba, background)

    def explain_instance(self, instance_df: pd.DataFrame) -> shap.Explanation:
        """
        Calculates SHAP values for a single instance.
        """
        instance_df = instance_df[self.X_train.columns]
        
        try:
            shap_values = self.explainer(instance_df, check_additivity=False)
        except Exception:
            try:
                shap_values = self.explainer(instance_df)
            except Exception:
                background = shap.sample(self.X_train, min(20, len(self.X_train)))
                kernel = shap.KernelExplainer(self.model.predict_proba, background)
                shap_values = kernel(instance_df)
        
        if hasattr(shap_values, 'values') and len(shap_values.values.shape) == 3:
            shap_values = shap_values[:, :, 1]
            
        return shap_values

    def explain_dataset(self, X: pd.DataFrame) -> shap.Explanation:
        """
        Calculates SHAP values for a dataset.
        """
        X = X[self.X_train.columns]
        try:
            shap_values = self.explainer(X, check_additivity=False)
        except Exception:
            shap_values = self.explainer(X)
        if len(shap_values.values.shape) == 3:
            shap_values = shap_values[:, :, 1]
        return shap_values

    def plot_waterfall(self, instance_df: pd.DataFrame, save_path: str) -> None:
        """
        Generates and saves a SHAP waterfall plot for a single prediction.
        """
        explanation = self.explain_instance(instance_df)
        
        plt.figure(figsize=(10, 6))
        # shap.plots.waterfall takes a single row explanation object
        shap.plots.waterfall(explanation[0], show=False)
        plt.title("SHAP Local Prediction Explanation (Waterfall)", fontsize=14, pad=20)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()

    def plot_summary(self, X: pd.DataFrame, save_path: str) -> None:
        """
        Generates and saves a SHAP summary plot (Beeswarm).
        """
        explanation = self.explain_dataset(X)
        
        plt.figure(figsize=(10, 7))
        shap.plots.beeswarm(explanation, show=False, max_display=15)
        plt.title("SHAP Global Feature Importance (Beeswarm)", fontsize=14, pad=20)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()

    def plot_bar(self, X: pd.DataFrame, save_path: str) -> None:
        """
        Generates and saves a SHAP bar plot.
        """
        explanation = self.explain_dataset(X)
        
        plt.figure(figsize=(10, 7))
        shap.plots.bar(explanation, show=False, max_display=15)
        plt.title("SHAP Feature Importance (Bar Plot)", fontsize=14, pad=20)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()

    def plot_dependence(self, X: pd.DataFrame, feature: str, save_path: str) -> None:
        """
        Generates and saves a SHAP dependence plot for a specific feature.
        """
        # Get raw SHAP values array or Explanation object
        explanation = self.explain_dataset(X)
        
        plt.figure(figsize=(8, 6))
        # Find index of feature
        feature_idx = X.columns.get_loc(feature)
        
        shap.dependence_plot(
            feature_idx, 
            explanation.values, 
            X.values, 
            feature_names=X.columns.tolist(),
            show=False
        )
        plt.title(f"SHAP Dependence Plot for {feature}", fontsize=12, pad=15)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()

    def generate_force_html(self, instance_df: pd.DataFrame, save_path: str) -> str:
        """
        Generates an HTML force plot for a single instance.
        """
        explanation = self.explain_instance(instance_df)
        
        # Get base value and shap values for the instance
        base_value = explanation.base_values[0]
        shap_vals = explanation.values[0]
        instance_features = instance_df.iloc[0].values
        
        # Generate force plot html
        shap.initjs()
        plot = shap.force_plot(
            base_value, 
            shap_vals, 
            instance_features, 
            feature_names=self.X_train.columns.tolist(),
            matplotlib=False
        )
        
        # Save HTML snippet
        shap.save_html(save_path, plot)
        return save_path

    def get_feature_importance_dict(self, X: pd.DataFrame) -> Dict[str, Any]:
        """
        Returns global feature importance as a JSON-serializable dictionary.
        Computes mean absolute SHAP values for each feature.
        """
        explanation = self.explain_dataset(X)
        shap_vals = explanation.values  # shape: (n_samples, n_features)

        # Mean absolute SHAP values
        mean_abs_shap = np.abs(shap_vals).mean(axis=0)
        feature_names = self.X_train.columns.tolist()

        # Sort by importance
        sorted_indices = np.argsort(mean_abs_shap)[::-1]

        importance_list = []
        for idx in sorted_indices:
            importance_list.append({
                "feature": feature_names[idx],
                "importance": float(mean_abs_shap[idx]),
                "rank": int(np.where(sorted_indices == idx)[0][0]) + 1,
            })

        return {
            "features": importance_list,
            "total_features": len(feature_names),
            "method": "mean_absolute_shap",
        }

    def get_feature_directions(self, X: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyzes the correlation direction of each feature with SHAP values.
        Determines whether higher/lower feature values generally increase
        or decrease the approval probability.

        Returns a JSON-serializable dict with direction info for each feature.
        """
        explanation = self.explain_dataset(X)
        shap_vals = explanation.values
        feature_names = self.X_train.columns.tolist()

        directions = []
        for i, feat in enumerate(feature_names):
            feat_values = X.iloc[:, i].values if isinstance(X, pd.DataFrame) else X[:, i]
            shap_col = shap_vals[:, i]

            # Compute correlation between feature values and SHAP values
            if np.std(feat_values) > 0 and np.std(shap_col) > 0:
                correlation = float(np.corrcoef(feat_values, shap_col)[0, 1])
            else:
                correlation = 0.0

            mean_shap = float(np.mean(shap_col))
            mean_abs_shap = float(np.mean(np.abs(shap_col)))

            if correlation > 0.1:
                direction = "positive"
                description = "Higher values increase approval probability"
            elif correlation < -0.1:
                direction = "negative"
                description = "Higher values decrease approval probability"
            else:
                direction = "neutral"
                description = "No clear directional impact on approval"

            directions.append({
                "feature": feat,
                "direction": direction,
                "correlation": round(correlation, 4),
                "mean_shap": round(mean_shap, 6),
                "mean_abs_shap": round(mean_abs_shap, 6),
                "description": description,
            })

        # Sort by absolute importance
        directions.sort(key=lambda d: d["mean_abs_shap"], reverse=True)

        return {
            "directions": directions,
            "total_features": len(feature_names),
        }

    def get_individual_explanation_dict(
        self, instance_df: pd.DataFrame, feature_values: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Returns a structured individual prediction explanation as a JSON-serializable dict.
        Includes positive factors (supporting approval) and negative factors (supporting denial).

        Args:
            instance_df: Single-row DataFrame of transformed features.
            feature_values: Optional dict of original (pre-transformation) feature values
                           for human-readable display.
        """
        explanation = self.explain_instance(instance_df)
        shap_vals = explanation.values[0]
        base_value = float(explanation.base_values[0])
        feature_names = self.X_train.columns.tolist()

        positive_factors = []
        negative_factors = []

        for i, feat in enumerate(feature_names):
            sv = float(shap_vals[i])
            entry = {
                "feature": feat,
                "shap_value": round(sv, 6),
                "impact": abs(round(sv, 6)),
            }

            if feature_values and feat in feature_values:
                entry["value"] = feature_values[feat]

            if sv > 0.005:
                positive_factors.append(entry)
            elif sv < -0.005:
                negative_factors.append(entry)

        # Sort by absolute impact
        positive_factors.sort(key=lambda x: x["impact"], reverse=True)
        negative_factors.sort(key=lambda x: x["impact"], reverse=True)

        # Generate human-readable factor descriptions
        positive_descriptions = []
        for f in positive_factors[:5]:
            positive_descriptions.append(
                f"+ {f['feature'].replace('_', ' ').title()}"
            )

        negative_descriptions = []
        for f in negative_factors[:5]:
            negative_descriptions.append(
                f"- {f['feature'].replace('_', ' ').title()}"
            )

        return {
            "base_value": base_value,
            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
            "positive_descriptions": positive_descriptions,
            "negative_descriptions": negative_descriptions,
            "shap_values": {feat: round(float(shap_vals[i]), 6) for i, feat in enumerate(feature_names)},
            "total_positive_impact": round(float(sum(f["shap_value"] for f in positive_factors)), 6),
            "total_negative_impact": round(float(sum(f["shap_value"] for f in negative_factors)), 6),
        }

