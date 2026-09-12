import os
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import recall_score, precision_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

class FairnessAuditor:
    def __init__(self, protected_attributes: List[str] = None):
        self.protected_attributes = protected_attributes or ["gender", "age_group", "race"]

    def audit(
        self, 
        df: pd.DataFrame, 
        y_true_col: str, 
        y_pred_col: str
    ) -> Dict[str, Any]:
        """
        Audits predictions for fairness over all protected attributes.
        
        Args:
            df: DataFrame containing the protected columns, y_true, and y_pred.
            y_true_col: Name of the ground truth column.
            y_pred_col: Name of the predicted labels column.
        """
        audit_results = {}
        y_true = df[y_true_col].astype(int)
        y_pred = df[y_pred_col].astype(int)
        
        for attr in self.protected_attributes:
            if attr not in df.columns:
                continue
                
            groups = df[attr].unique()
            group_metrics = {}
            
            # Global approval rate for reference
            overall_rate = float(y_pred.mean())
            
            for group in groups:
                mask = df[attr] == group
                sub_y_true = y_true[mask]
                sub_y_pred = y_pred[mask]
                
                if len(sub_y_true) == 0:
                    continue
                    
                selection_rate = float(sub_y_pred.mean())  # Approval Rate
                tpr = float(recall_score(sub_y_true, sub_y_pred, zero_division=0))  # True Positive Rate
                
                # False positive rate (FPR)
                fp = ((sub_y_pred == 1) & (sub_y_true == 0)).sum()
                tn = ((sub_y_pred == 0) & (sub_y_true == 0)).sum()
                fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
                
                group_metrics[group] = {
                    "sample_count": int(mask.sum()),
                    "selection_rate": selection_rate,
                    "true_positive_rate": tpr,
                    "false_positive_rate": fpr,
                    "accuracy": float((sub_y_pred == sub_y_true).mean())
                }
                
            # Compute fairness metrics
            selection_rates = [m["selection_rate"] for m in group_metrics.values()]
            tprs = [m["true_positive_rate"] for m in group_metrics.values()]
            
            demographic_parity_diff = float(max(selection_rates) - min(selection_rates))
            demographic_parity_ratio = float(min(selection_rates) / max(selection_rates)) if max(selection_rates) > 0 else 1.0
            
            equal_opportunity_diff = float(max(tprs) - min(tprs))
            
            # Recommendation generation based on standard rules
            recommendations = []
            if demographic_parity_ratio < 0.8:
                recommendations.append(
                    f"Significant bias detected against certain groups in '{attr}' (Demographic Parity Ratio is {demographic_parity_ratio:.2f} < 0.8 threshold). "
                    "Apply sample reweighing during preprocessing or adjust decision thresholds."
                )
            if equal_opportunity_diff > 0.1:
                recommendations.append(
                    f"Model shows unequal error rates across groups in '{attr}' (Equal Opportunity Difference is {equal_opportunity_diff:.2f} > 0.1). "
                    "Recommend post-processing threshold adjustments to equalize True Positive Rates."
                )
            if not recommendations:
                recommendations.append(f"Model meets standard fairness criteria for '{attr}'.")
                
            audit_results[attr] = {
                "overall_selection_rate": overall_rate,
                "group_metrics": group_metrics,
                "demographic_parity_difference": demographic_parity_diff,
                "demographic_parity_ratio": demographic_parity_ratio,
                "equal_opportunity_difference": equal_opportunity_diff,
                "recommendations": recommendations
            }
            
        return audit_results

    def plot_fairness_disparity(self, audit_results: Dict[str, Any], save_dir: str) -> List[str]:
        """
        Plots and saves comparison bar charts for selection rates across groups.
        """
        os.makedirs(save_dir, exist_ok=True)
        paths = []
        
        for attr, res in audit_results.items():
            groups = list(res["group_metrics"].keys())
            rates = [res["group_metrics"][g]["selection_rate"] for g in groups]
            tprs = [res["group_metrics"][g]["true_positive_rate"] for g in groups]
            
            df_plot = pd.DataFrame({
                "Group": groups + groups,
                "Rate": rates + tprs,
                "Metric Type": ["Selection (Approval) Rate"] * len(groups) + ["True Positive (Recall) Rate"] * len(groups)
            })
            
            plt.figure(figsize=(9, 5))
            sns.barplot(x="Group", y="Rate", hue="Metric Type", data=df_plot, palette="muted")
            plt.axhline(y=res["overall_selection_rate"], color="gray", linestyle="--", alpha=0.7, label="Overall Approval Rate")
            plt.ylim(0, 1.0)
            plt.title(f"Fairness Disparity Audit: {attr.capitalize()}")
            plt.ylabel("Rate Percentage")
            plt.xlabel(f"{attr.capitalize()} Groups")
            plt.legend(loc="upper right")
            plt.tight_layout()
            
            save_path = os.path.join(save_dir, f"fairness_audit_{attr}.png")
            plt.savefig(save_path, dpi=150)
            plt.close()
            paths.append(save_path)
            
        return paths
