import os
import time
import yaml
import pickle
import logging
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.model_selection import GridSearchCV
from config.settings import settings, BASE_DIR
from models.classifiers import get_classifier_by_name
from evaluation.metrics import calculate_metrics, plot_confusion_matrix, plot_roc_curve, plot_precision_recall_curve, plot_feature_importance, plot_learning_curve

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.hyperparams_grid = self._load_config()
        self.results: Dict[str, Dict[str, Any]] = {}
        self.best_model_name: str = ""
        self.best_model: Any = None
        self.best_metrics: Dict[str, float] = {}

    def _load_config(self) -> Dict[str, Any]:
        """Loads hyperparameters search grids from YAML."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found at {self.config_path}. Using empty grids.")
            return {}
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def train_and_compare(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series, 
        X_test: pd.DataFrame, 
        y_test: pd.Series,
        dataset_id: str,
        experiment_tracker=None,
        model_registry=None,
        scaler_path: str = "",
        cleaner_path: str = ""
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Runs GridSearchCV for all models in grid config and compares them.
        Returns a tuple of (summary_df, results_dict).
        """
        model_names = [
            "logistic_regression",
            "decision_tree",
            "random_forest",
            "gradient_boosting",
            "xgboost",
            "lightgbm",
            "catboost",
            "svm",
            "extra_trees"
        ]
        
        feature_names = X_train.columns.tolist()
        
        models_dir = os.path.join(str(BASE_DIR), "models_saved", dataset_id)
        os.makedirs(models_dir, exist_ok=True)
        
        for name in model_names:
            grid = self.hyperparams_grid.get(name, {})
            logger.info(f"Setting up GridSearchCV for {name} with grid: {grid}")
            
            try:
                # Instantiate classifier wrapper
                classifier_wrapper = get_classifier_by_name(name)
                estimator = classifier_wrapper.model
                
                # Perform grid search
                cv = GridSearchCV(
                    estimator=estimator,
                    param_grid=grid,
                    scoring="roc_auc",
                    cv=3,
                    n_jobs=-1,
                    verbose=0,
                    return_train_score=False
                )
                
                logger.info(f"Running GridSearchCV for {name}...")
                start_train_time = time.time()
                cv.fit(X_train, y_train)
                training_time = time.time() - start_train_time
                
                best_estimator = cv.best_estimator_
                best_params = cv.best_params_
                
                # Extract cross-validation scores
                cv_results = cv.cv_results_
                best_index = cv.best_index_
                # the splits could be named split0_test_score, split1_test_score, etc.
                cv_scores = []
                for i in range(cv.n_splits_):
                    key = f"split{i}_test_score"
                    if key in cv_results:
                        cv_scores.append(float(cv_results[key][best_index]))
                
                # Predict on test
                start_pred_time = time.time()
                y_pred = best_estimator.predict(X_test)
                # handle probabilities
                y_prob = None
                if hasattr(best_estimator, "predict_proba"):
                    y_prob = best_estimator.predict_proba(X_test)[:, 1]
                elif hasattr(best_estimator, "decision_function"):
                    y_prob = best_estimator.decision_function(X_test)
                prediction_time = time.time() - start_pred_time
                
                # Calculate metrics
                metrics = calculate_metrics(y_test.values, y_pred, y_prob)
                
                # Save model individually
                model_file_path = os.path.join(models_dir, f"{name}.pkl")
                with open(model_file_path, "wb") as f:
                    pickle.dump(best_estimator, f)
                
                # Log experiment
                if experiment_tracker:
                    experiment_tracker.log_experiment(
                        dataset_id=dataset_id,
                        model_name=name,
                        hyperparameters=best_params,
                        metrics=metrics,
                        cv_scores=cv_scores,
                        training_time=training_time,
                        prediction_time=prediction_time,
                        model_file_path=model_file_path,
                        features_used=feature_names
                    )
                
                # Register model
                if model_registry:
                    model_registry.register_model(
                        dataset_id=dataset_id,
                        model_name=name,
                        model_file_path=model_file_path,
                        metrics=metrics,
                        hyperparameters=best_params,
                        features_used=feature_names,
                        scaler_path=scaler_path,
                        cleaner_path=cleaner_path
                    )
                
                # Save results
                self.results[name] = {
                    "model": best_estimator,
                    "params": best_params,
                    "metrics": metrics,
                    "roc_auc": metrics.get("roc_auc", 0.0),
                    "f1_score": metrics.get("f1_score", 0.0),
                    "accuracy": metrics.get("accuracy", 0.0),
                    "cv_scores": cv_scores,
                    "training_time": training_time,
                    "prediction_time": prediction_time
                }
                
                logger.info(f"Model {name} finished. ROC AUC: {metrics.get('roc_auc', 0.0):.4f}")
                
            except Exception as e:
                logger.error(f"Error training {name}: {str(e)}", exc_info=True)
                
        # Compare and find best model (based on ROC AUC)
        if not self.results:
            raise ValueError("No models trained successfully.")
            
        best_name = max(self.results, key=lambda k: self.results[k]["roc_auc"])
        self.best_model_name = best_name
        self.best_model = self.results[best_name]["model"]
        self.best_metrics = self.results[best_name]["metrics"]
        
        logger.info(f"*** BEST MODEL DETECTED: {self.best_model_name} with ROC AUC: {self.best_metrics.get('roc_auc'):.4f} ***")
        
        # Compile a summary table
        summary_data = []
        for name, res in self.results.items():
            summary_data.append({
                "Model": name,
                "ROC AUC": res["metrics"].get("roc_auc", 0.0),
                "F1 Score": res["metrics"].get("f1_score", 0.0),
                "Accuracy": res["metrics"].get("accuracy", 0.0),
                "Precision": res["metrics"].get("precision", 0.0),
                "Recall": res["metrics"].get("recall", 0.0),
                "Best Params": str(res["params"])
            })
            
        summary_df = pd.DataFrame(summary_data).sort_values("ROC AUC", ascending=False)
        # Save summary report to artifacts
        summary_df.to_csv(os.path.join(settings.ARTIFACTS_DIR, f"model_comparison_{dataset_id}.csv"), index=False)
        
        # Generate diagnostic plots for the BEST model
        self.generate_best_model_plots(X_train, y_train, X_test, y_test, feature_names, dataset_id)
        
        return summary_df, self.results

    def generate_best_model_plots(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series, 
        X_test: pd.DataFrame, 
        y_test: pd.Series,
        feature_names: list[str],
        dataset_id: str
    ) -> None:
        """
        Generates and saves Confusion Matrix, ROC, PR, Learning Curves, and Feature Importance for the best model.
        """
        logger.info(f"Generating evaluation plots for the best model: {self.best_model_name}")
        y_pred = self.best_model.predict(X_test)
        
        y_prob = None
        if hasattr(self.best_model, "predict_proba"):
            y_prob = self.best_model.predict_proba(X_test)[:, 1]
        elif hasattr(self.best_model, "decision_function"):
            y_prob = self.best_model.decision_function(X_test)
        
        # Confusion Matrix
        plot_confusion_matrix(y_test.values, y_pred, os.path.join(settings.ARTIFACTS_DIR, f"best_confusion_matrix_{dataset_id}.png"))
        
        # ROC & PR Curves
        if y_prob is not None:
            plot_roc_curve(y_test.values, y_prob, os.path.join(settings.ARTIFACTS_DIR, f"best_roc_curve_{dataset_id}.png"))
            plot_precision_recall_curve(y_test.values, y_prob, os.path.join(settings.ARTIFACTS_DIR, f"best_pr_curve_{dataset_id}.png"))
            
        # Feature Importance
        plot_feature_importance(self.best_model, feature_names, os.path.join(settings.ARTIFACTS_DIR, f"best_feature_importance_{dataset_id}.png"))
        
        # Learning Curve
        try:
            plot_learning_curve(self.best_model, X_train, y_train, os.path.join(settings.ARTIFACTS_DIR, f"best_learning_curve_{dataset_id}.png"))
        except Exception as e:
            logger.warning(f"Could not generate learning curve: {str(e)}")

    def save_pipeline(self, transformer: Any, cleaner: Any, dataset_id: str = "") -> None:
        """
        Saves the best model and preprocessing pipeline components.
        """
        model_path = settings.MODEL_PATH if not dataset_id else os.path.join(settings.MODEL_DIR, f"best_model_{dataset_id}.pkl")
        scaler_path = settings.SCALER_PATH if not dataset_id else os.path.join(settings.MODEL_DIR, f"scaler_{dataset_id}.pkl")
        cleaner_path = settings.ENCODER_PATH if not dataset_id else os.path.join(settings.MODEL_DIR, f"cleaner_{dataset_id}.pkl")
        
        logger.info(f"Saving best model to {model_path}...")
        with open(model_path, "wb") as f:
            pickle.dump(self.best_model, f)
            
        logger.info(f"Saving feature transformer to {scaler_path}...")
        with open(scaler_path, "wb") as f:
            pickle.dump(transformer, f)
            
        logger.info(f"Saving data cleaner to {cleaner_path}...")
        with open(cleaner_path, "wb") as f:
            pickle.dump(cleaner, f)
            
        # Write metadata file about the best model
        metadata = {
            "model_name": self.best_model_name,
            "metrics": self.best_metrics,
            "params": self.results[self.best_model_name]["params"]
        }
        metadata_path = os.path.join(settings.MODEL_DIR, "model_metadata.yaml" if not dataset_id else f"model_metadata_{dataset_id}.yaml")
        with open(metadata_path, "w") as f:
            yaml.dump(metadata, f)
            
        logger.info("Pipeline artifacts saved successfully.")
