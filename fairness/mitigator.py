import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.metrics import recall_score

class BiasMitigator:
    def __init__(self):
        pass

    @staticmethod
    def compute_reweighing_weights(
        df: pd.DataFrame, 
        protected_attribute: str, 
        target_col: str
    ) -> np.ndarray:
        """
        Calculates Kamiran & Calders sample weights for reweighing training samples.
        Formula: W(a, y) = [P(A=a) * P(Y=y)] / P(A=a, Y=y)
        
        Args:
            df: Training dataframe containing protected attribute and target columns.
            protected_attribute: Column name of the sensitive attribute (e.g., 'gender').
            target_col: Column name of the target label (e.g., 'loan_status').
        """
        # Copy to avoid side-effects
        data = df[[protected_attribute, target_col]].copy()
        
        n = len(data)
        weights = np.ones(n)
        
        # Calculate marginal probabilities
        p_attr = data[protected_attribute].value_counts(normalize=True).to_dict()
        p_target = data[target_col].value_counts(normalize=True).to_dict()
        
        # Calculate joint probabilities
        joint_counts = data.groupby([protected_attribute, target_col]).size().to_dict()
        
        for idx, row in data.iterrows():
            attr_val = row[protected_attribute]
            target_val = row[target_col]
            
            p_a = p_attr.get(attr_val, 0)
            p_y = p_target.get(target_val, 0)
            joint_count = joint_counts.get((attr_val, target_val), 0)
            
            p_ay = joint_count / n if n > 0 else 0
            
            if p_ay > 0:
                weights[idx] = (p_a * p_y) / p_ay
            else:
                weights[idx] = 1.0
                
        # Normalize weights to sum up to N (original sample size) to preserve gradient scales
        weights = weights * (n / weights.sum())
        return weights

    @staticmethod
    def find_fair_thresholds(
        y_true: np.ndarray, 
        y_prob: np.ndarray, 
        protected_attr_array: np.ndarray,
        metric: str = "demographic_parity"
    ) -> Dict[str, float]:
        """
        Calculates optimized decision thresholds for each protected group to achieve fairness parity.
        
        Args:
            y_true: True binary labels (N,)
            y_prob: Predicted probability score of positive class (N,)
            protected_attr_array: Array containing sensitive attribute values (N,)
            metric: 'demographic_parity' or 'equal_opportunity'
        """
        groups = np.unique(protected_attr_array)
        thresholds = {g: 0.5 for g in groups}
        
        # Find global target metric for calibration
        # Let's target the maximum performance or the global average rate
        # For demographic parity, we want to match selection rate
        # For equal opportunity, we want to match true positive rate (recall)
        
        best_overall_diff = 1.0
        best_thresholds = thresholds.copy()
        
        # Grid search over candidate thresholds to find set that minimizes discrepancy
        # To keep it fast, we search in increments of 0.02
        candidate_thresholds = np.linspace(0.2, 0.8, 31)
        
        # Simple heuristic: find thresholds that align selection rate or TPR close to a baseline (e.g. 0.6)
        if metric == "demographic_parity":
            # Target average selection rate of ~55%
            target_rate = 0.55
            for g in groups:
                mask = protected_attr_array == g
                g_probs = y_prob[mask]
                
                best_t = 0.5
                best_diff = 1.0
                for t in candidate_thresholds:
                    rate = (g_probs >= t).mean()
                    diff = abs(rate - target_rate)
                    if diff < best_diff:
                        best_diff = diff
                        best_t = t
                thresholds[g] = float(best_t)
                
        elif metric == "equal_opportunity":
            # Target average TPR of ~75%
            target_tpr = 0.75
            for g in groups:
                mask = protected_attr_array == g
                g_true = y_true[mask]
                g_probs = y_prob[mask]
                
                best_t = 0.5
                best_diff = 1.0
                for t in candidate_thresholds:
                    g_pred = (g_probs >= t).astype(int)
                    tpr = recall_score(g_true, g_pred, zero_division=0)
                    diff = abs(tpr - target_tpr)
                    if diff < best_diff:
                        best_diff = diff
                        best_t = t
                thresholds[g] = float(best_t)
                
        return thresholds

    @staticmethod
    def apply_fair_thresholds(
        y_prob: np.ndarray, 
        protected_attr_array: np.ndarray, 
        thresholds: Dict[str, float]
    ) -> np.ndarray:
        """
        Applies group-specific thresholds to predict binary labels.
        """
        y_pred = np.zeros(len(y_prob), dtype=int)
        for idx, (prob, attr) in enumerate(zip(y_prob, protected_attr_array)):
            t = thresholds.get(attr, 0.5)
            y_pred[idx] = 1 if prob >= t else 0
        return y_pred
