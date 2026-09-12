import os
import sys
import json
import logging
import pandas as pd
from sklearn.model_selection import train_test_split

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from config.dataset_config import DATASET_CONFIGS, get_dataset_path
from preprocessing.data_validator import validate_dataframe
from preprocessing.data_cleaner import DataCleaner
from feature_engineering.transformer import FeatureTransformer
from training.trainer import ModelTrainer
from training.experiment_tracker import ExperimentTracker
from models.model_registry import ModelRegistry
from explainability.shap_explainer import ShapExplainerManager
from fairness.auditor import FairnessAuditor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

def save_evaluations(results: dict, dataset_id: str, X_test=None, y_test=None):
    eval_dir = os.path.join(settings.ARTIFACTS_DIR, "evaluations", dataset_id)
    shap_dir = os.path.join(settings.ARTIFACTS_DIR, "shap", dataset_id)
    
    from evaluation.metrics import (
        calculate_confusion_matrix_data, calculate_roc_data,
        calculate_pr_data, calculate_calibration_data
    )
    
    for model_name, res in results.items():
        model_eval_dir = os.path.join(eval_dir, model_name)
        os.makedirs(model_eval_dir, exist_ok=True)
        
        # Save evaluation.json
        dump_data = {
            "metrics": res["metrics"],
            "cv_scores": res.get("cv_scores", []),
            "training_time": res.get("training_time", 0.0),
            "prediction_time": res.get("prediction_time", 0.0)
        }
        with open(os.path.join(model_eval_dir, "evaluation.json"), "w") as f:
            json.dump(dump_data, f, indent=2)
            
        model_obj = res.get("model")
        if model_obj is not None and X_test is not None and y_test is not None:
            try:
                y_pred = model_obj.predict(X_test)
                cm_data = calculate_confusion_matrix_data(y_test, y_pred)
                with open(os.path.join(model_eval_dir, "confusion_matrix.json"), "w") as f:
                    json.dump(cm_data, f, indent=2)
                    
                if hasattr(model_obj, "predict_proba"):
                    y_prob = model_obj.predict_proba(X_test)[:, 1]
                    roc_data = calculate_roc_data(y_test, y_prob)
                    with open(os.path.join(model_eval_dir, "roc.json"), "w") as f:
                        json.dump(roc_data, f, indent=2)
                        
                    pr_data = calculate_pr_data(y_test, y_prob)
                    with open(os.path.join(model_eval_dir, "pr.json"), "w") as f:
                        json.dump(pr_data, f, indent=2)
                        
                    cal_data = calculate_calibration_data(y_test, y_prob)
                    with open(os.path.join(model_eval_dir, "calibration.json"), "w") as f:
                        json.dump(cal_data, f, indent=2)
            except Exception as e:
                logger.warning(f"Error saving eval curves for {model_name}: {e}")
                
            # Pre-compute SHAP importance JSON
            try:
                model_shap_dir = os.path.join(shap_dir, model_name)
                os.makedirs(model_shap_dir, exist_ok=True)
                sample_test = X_test.sample(min(50, len(X_test)), random_state=42)
                shap_manager = ShapExplainerManager(model_obj, X_test.sample(min(30, len(X_test)), random_state=42))
                imp = shap_manager.get_feature_importance_dict(sample_test)
                dirs = shap_manager.get_feature_directions(sample_test)
                
                with open(os.path.join(model_shap_dir, "feature_importance.json"), "w") as f:
                    json.dump(imp, f, indent=2)
                with open(os.path.join(model_shap_dir, "feature_directions.json"), "w") as f:
                    json.dump(dirs, f, indent=2)
            except Exception as e:
                logger.warning(f"Error saving SHAP JSON for {model_name}: {e}")

def run_ml_pipeline():
    logger.info("Starting end-to-end Machine Learning Pipeline for multiple datasets...")
    
    experiment_tracker = ExperimentTracker()
    model_registry = ModelRegistry()
    
    # Loop over all datasets
    for dataset_id, config in DATASET_CONFIGS.items():
        logger.info(f"=== Processing Dataset: {dataset_id} ===")
        dataset_path = get_dataset_path(dataset_id)
        
        # 1. Load Dataset
        if not os.path.exists(dataset_path):
            logger.warning(f"Dataset not found at {dataset_path}. Skipping...")
            continue
            
        df = pd.read_csv(dataset_path)
        logger.info(f"Loaded dataset {dataset_id} with shape: {df.shape}")
        
        # 2. Data Validation (skip strict column checks for non-standard datasets)
        from preprocessing.data_validator import REQUIRED_COLS
        # Only validate against REQUIRED_COLS if dataset columns match the expected schema
        has_standard_cols = all(col in df.columns for col in REQUIRED_COLS.keys())
        if has_standard_cols:
            is_valid, validation_errors = validate_dataframe(df, is_training=True)
            if not is_valid:
                logger.error(f"DataFrame validation failed for {dataset_id}! Errors: {validation_errors}")
                continue
            logger.info("DataFrame validation completed successfully.")
        else:
            logger.info(f"Skipping strict validation for {dataset_id} (non-standard schema). Basic checks passed.")
        
        target_col = config.get("target_column")
        if target_col not in df.columns:
            logger.error(f"Target column {target_col} not found in {dataset_id}. Skipping...")
            continue
            
        # Stratified train-test split before cleaning to avoid data leakage
        X_raw = df.drop(columns=[target_col])
        y_raw = df[target_col]
        
        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            X_raw, y_raw, test_size=0.20, random_state=42, stratify=y_raw
        )
        logger.info(f"Split data into train size {X_train_raw.shape[0]} and test size {X_test_raw.shape[0]}.")
        
        # Combine back for cleaning
        df_train = X_train_raw.copy()
        df_train[target_col] = y_train
        
        df_test = X_test_raw.copy()
        df_test[target_col] = y_test
        
        # 3. Clean Data (Imputation and Outlier Clipping)
        # Fit on train only, transform both
        cleaner = DataCleaner()
        cleaner.fit(df_train)
        df_train_cleaned = cleaner.transform(df_train)
        df_test_cleaned = cleaner.transform(df_test)
        
        # Drop columns not for training (ID, protected attributes, target)
        drop_cols = config.get("drop_columns", []) + config.get("protected_attributes", []) + [target_col]
        
        X_train_clean = df_train_cleaned.drop(columns=drop_cols, errors="ignore")
        X_test_clean = df_test_cleaned.drop(columns=drop_cols, errors="ignore")
        
        # 4. Feature Engineering & Preprocessing (Standard Scaling & One Hot Encoding)
        transformer = FeatureTransformer(numeric_cols=config.get("numeric_features"), categorical_cols=config.get("categorical_features"))
        transformer.fit(X_train_clean)
        
        X_train_transformed = transformer.transform(X_train_clean)
        X_test_transformed = transformer.transform(X_test_clean)
        logger.info(f"Feature transformation completed. Transformed shape: {X_train_transformed.shape}")
        
        scaler_path = os.path.join(settings.MODEL_DIR, f"scaler_{dataset_id}.pkl")
        cleaner_path = os.path.join(settings.MODEL_DIR, f"cleaner_{dataset_id}.pkl")
        
        # 5. Model Training & Comparison
        trainer = ModelTrainer(config_path="config/config.yaml")
        comparison_summary, results = trainer.train_and_compare(
            X_train=X_train_transformed, 
            y_train=y_train, 
            X_test=X_test_transformed, 
            y_test=y_test,
            dataset_id=dataset_id,
            experiment_tracker=experiment_tracker,
            model_registry=model_registry,
            scaler_path=scaler_path,
            cleaner_path=cleaner_path
        )
        
        logger.info(f"--- Model Training Summary for {dataset_id} ---")
        logger.info("\n" + comparison_summary.to_string(index=False))
        
        trainer.save_pipeline(transformer, cleaner, dataset_id)
        save_evaluations(results, dataset_id, X_test_transformed, y_test)
        
        # 6. Global Interpretability (SHAP Summary and Bar Plots)
        logger.info("Running global explainability audits (SHAP)...")
        try:
            best_model = trainer.best_model
            shap_manager = ShapExplainerManager(best_model, X_train_transformed)
            
            summary_plot_path = os.path.join(settings.ARTIFACTS_DIR, f"shap_global_beeswarm_{dataset_id}.png")
            shap_manager.plot_summary(X_test_transformed, summary_plot_path)
            
            bar_plot_path = os.path.join(settings.ARTIFACTS_DIR, f"shap_global_bar_{dataset_id}.png")
            shap_manager.plot_bar(X_test_transformed, bar_plot_path)
            
            # Use first numeric feature as fallback if credit_score doesn't exist
            num_feats = config.get("numeric_features", [])
            dep_feat = "credit_score" if "credit_score" in X_test_transformed.columns else (num_feats[0] if num_feats else X_test_transformed.columns[0])
            dep_plot_path = os.path.join(settings.ARTIFACTS_DIR, f"shap_dependence_{dep_feat}_{dataset_id}.png")
            shap_manager.plot_dependence(X_test_transformed, dep_feat, dep_plot_path)
            
        except Exception as e:
            logger.error(f"Failed to generate SHAP plots for {dataset_id}: {str(e)}", exc_info=True)
            
        # 7. Model Bias & Fairness Audit (if protected attributes exist)
        protected_attrs = config.get("protected_attributes", [])
        if protected_attrs:
            logger.info(f"Running fairness audit for {dataset_id} on {protected_attrs}...")
            try:
                y_test_pred = trainer.best_model.predict(X_test_transformed)
                
                # We need raw data from test set for protected attributes
                test_sensitive_df = df_test[protected_attrs].copy()
                test_sensitive_df[target_col] = y_test
                test_sensitive_df["predicted_status"] = y_test_pred
                
                auditor = FairnessAuditor()
                audit_results = auditor.audit(
                    test_sensitive_df, 
                    y_true_col=target_col, 
                    y_pred_col="predicted_status"
                )
                
                fairness_json_path = os.path.join(settings.ARTIFACTS_DIR, f"fairness_audit_results_{dataset_id}.json")
                with open(fairness_json_path, "w") as f:
                    json.dump(audit_results, f, indent=2)
                
                # Render fairness disparity plots
                # Ensure the auditor uses the dataset_id in the filename if possible, otherwise move them
                plots_created = auditor.plot_fairness_disparity(audit_results, settings.ARTIFACTS_DIR)
                # Need to rename generated plots to include dataset_id
                for plot_file in plots_created:
                    base = os.path.basename(plot_file)
                    new_path = os.path.join(settings.ARTIFACTS_DIR, f"{dataset_id}_{base}")
                    if os.path.exists(plot_file):
                        os.rename(plot_file, new_path)
                
            except Exception as e:
                logger.error(f"Failed to execute fairness audit for {dataset_id}: {str(e)}", exc_info=True)
    
    # Final Summary
    logger.info("=== End of Pipeline ===")
    all_experiments = experiment_tracker.get_all_experiments()
    logger.info(f"Total experiments logged: {len(all_experiments)}")
    logger.info("ML Pipeline finished successfully.")

if __name__ == "__main__":
    run_ml_pipeline()
