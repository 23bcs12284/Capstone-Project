import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, roc_curve, precision_recall_curve,
    average_precision_score, brier_score_loss, auc
)
from sklearn.model_selection import learning_curve
from typing import Dict, Any, List, Tuple

def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, float]:
    """
    Computes classification evaluation metrics.
    """
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "sensitivity": float(recall_score(y_true, y_pred, zero_division=0)),
    }
    
    try:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    except ValueError:
        specificity = 0.0
    metrics["specificity"] = specificity
    
    if y_prob is not None:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
        metrics["pr_auc"] = float(average_precision_score(y_true, y_prob))
        metrics["brier_score"] = float(brier_score_loss(y_true, y_prob))
        
    return metrics

def calculate_calibration_data(y_true, y_prob, n_bins=10) -> dict:
    """Returns calibration curve data as JSON-serializable dict."""
    from sklearn.calibration import calibration_curve
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins)
    brier = float(brier_score_loss(y_true, y_prob))
    return {
        "fraction_of_positives": prob_true.tolist(),
        "mean_predicted_value": prob_pred.tolist(),
        "brier_score": brier
    }

def calculate_roc_data(y_true, y_prob) -> dict:
    """Returns ROC curve data points as JSON-serializable dict."""
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    auc_score = float(roc_auc_score(y_true, y_prob))
    return {
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "thresholds": thresholds.tolist(),
        "auc": auc_score
    }

def calculate_pr_data(y_true, y_prob) -> dict:
    """Returns PR curve data points as JSON-serializable dict."""
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    auc_score = float(auc(recall, precision))
    return {
        "precision": precision.tolist(),
        "recall": recall.tolist(),
        "thresholds": thresholds.tolist(),
        "auc": auc_score
    }

def calculate_confusion_matrix_data(y_true, y_pred) -> dict:
    """Returns confusion matrix as JSON-serializable dict."""
    cm = confusion_matrix(y_true, y_pred)
    return {
        "matrix": cm.tolist(),
        "labels": ["Denied", "Approved"]
    }

def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, save_path: str) -> None:
    """
    Generates and saves a Confusion Matrix plot.
    """
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["Denied", "Approved"], yticklabels=["Denied", "Approved"])
    plt.xlabel("Predicted Status")
    plt.ylabel("Actual Status")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_roc_curve(y_true: np.ndarray, y_prob: np.ndarray, save_path: str) -> None:
    """
    Generates and saves a ROC Curve plot.
    """
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    auc_score = roc_auc_score(y_true, y_prob)
    
    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC Curve (AUC = {auc_score:.4f})")
    plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate (FPR)")
    plt.ylabel("True Positive Rate (TPR)")
    plt.title("Receiver Operating Characteristic (ROC) Curve")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_precision_recall_curve(y_true: np.ndarray, y_prob: np.ndarray, save_path: str) -> None:
    """
    Generates and saves a Precision-Recall Curve.
    """
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    
    plt.figure(figsize=(7, 5))
    plt.plot(recall, precision, color="blue", lw=2, label="Precision-Recall Curve")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall (PR) Curve")
    plt.legend(loc="lower left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_learning_curve(estimator: Any, X: pd.DataFrame, y: pd.Series, save_path: str) -> None:
    """
    Generates and saves the Learning Curve.
    """
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=3, n_jobs=-1, 
        train_sizes=np.linspace(0.1, 1.0, 5), scoring="accuracy"
    )
    
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    
    plt.figure(figsize=(7, 5))
    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1, color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, "o-", color="r", label="Training Score")
    plt.plot(train_sizes, test_scores_mean, "o-", color="g", label="Cross-Validation Score")
    plt.xlabel("Training Examples")
    plt.ylabel("Accuracy Score")
    plt.title("Model Learning Curve")
    plt.legend(loc="best")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_feature_importance(model: Any, feature_names: List[str], save_path: str) -> None:
    """
    Plots the feature importances for models that support it.
    """
    importance = None
    if hasattr(model, "feature_importances_"):
        importance = model.feature_importances_
    elif hasattr(model, "coef_"):
        # For logistic regression
        importance = np.abs(model.coef_[0])
        
    if importance is None:
        return
        
    # Standardize or keep raw importances
    df_imp = pd.DataFrame({
        "feature": feature_names,
        "importance": importance
    }).sort_values("importance", ascending=False).head(15)
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x="importance", y="feature", data=df_imp, palette="viridis")
    plt.title("Top 15 Feature Importances / Coefficients")
    plt.xlabel("Importance / Coefficient Magnitude")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
