"""
Model Calibration Analysis

Evaluates whether predicted probabilities are well-calibrated,
which is critical when the system presents approval probabilities to users.
"""

import numpy as np
from typing import Dict, List, Any
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss


def calculate_calibration_data(
    y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
) -> Dict[str, Any]:
    """
    Computes calibration curve data for assessing probability reliability.

    Args:
        y_true: Ground truth binary labels.
        y_prob: Predicted probabilities for the positive class.
        n_bins: Number of bins for the calibration curve.

    Returns:
        JSON-serializable dict with calibration data.
    """
    try:
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_true, y_prob, n_bins=n_bins, strategy="uniform"
        )

        brier = float(brier_score_loss(y_true, y_prob))

        # Probability distribution histogram
        hist_counts, hist_edges = np.histogram(y_prob, bins=20, range=(0, 1))

        return {
            "fraction_of_positives": [float(v) for v in fraction_of_positives],
            "mean_predicted_value": [float(v) for v in mean_predicted_value],
            "brier_score": brier,
            "n_bins": n_bins,
            "probability_histogram": {
                "counts": [int(c) for c in hist_counts],
                "bin_edges": [float(e) for e in hist_edges],
            },
            "calibration_quality": _assess_calibration_quality(brier),
        }
    except Exception as e:
        return {
            "error": str(e),
            "fraction_of_positives": [],
            "mean_predicted_value": [],
            "brier_score": None,
            "n_bins": n_bins,
            "probability_histogram": {"counts": [], "bin_edges": []},
            "calibration_quality": "unknown",
        }


def _assess_calibration_quality(brier_score: float) -> str:
    """
    Provides a human-readable assessment of calibration quality.
    """
    if brier_score < 0.05:
        return "excellent"
    elif brier_score < 0.10:
        return "good"
    elif brier_score < 0.20:
        return "moderate"
    elif brier_score < 0.30:
        return "poor"
    else:
        return "very_poor"


def get_calibration_summary(brier_score: float) -> str:
    """
    Returns a human-readable summary of the calibration assessment.
    """
    quality = _assess_calibration_quality(brier_score)
    summaries = {
        "excellent": (
            f"The model is excellently calibrated (Brier Score: {brier_score:.4f}). "
            "Predicted probabilities closely match actual approval rates."
        ),
        "good": (
            f"The model is well calibrated (Brier Score: {brier_score:.4f}). "
            "Predicted probabilities are generally reliable."
        ),
        "moderate": (
            f"The model has moderate calibration (Brier Score: {brier_score:.4f}). "
            "Predicted probabilities should be interpreted with some caution."
        ),
        "poor": (
            f"The model has poor calibration (Brier Score: {brier_score:.4f}). "
            "Predicted probabilities may not accurately reflect true approval likelihood."
        ),
        "very_poor": (
            f"The model is poorly calibrated (Brier Score: {brier_score:.4f}). "
            "Predicted probabilities are unreliable and should not be used for decision-making."
        ),
    }
    return summaries.get(quality, "Calibration assessment unavailable.")
