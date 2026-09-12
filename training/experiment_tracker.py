import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXPERIMENTS_DIR = BASE_DIR / "artifacts" / "experiments"

class ExperimentTracker:
    def __init__(self):
        os.makedirs(EXPERIMENTS_DIR, exist_ok=True)
        self.experiments_file = EXPERIMENTS_DIR / "all_experiments.json"
        self.experiments = self._load_experiments()
    
    def _load_experiments(self) -> List[Dict[str, Any]]:
        try:
            if self.experiments_file.exists():
                with open(self.experiments_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading experiments: {e}")
        return []
    
    def _save_experiments(self):
        try:
            with open(self.experiments_file, 'w') as f:
                json.dump(self.experiments, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving experiments: {e}")
    
    def log_experiment(self, dataset_id: str, model_name: str, hyperparameters: dict, 
                       metrics: dict, cv_scores: list, training_time: float, 
                       prediction_time: float, model_file_path: str, 
                       features_used: list) -> dict:
        """Log or update an experiment result."""
        cv_mean = float(sum(cv_scores) / len(cv_scores)) if cv_scores else 0.0
        if len(cv_scores) > 1:
            cv_std = float((sum((s - cv_mean)**2 for s in cv_scores) / len(cv_scores))**0.5)
        else:
            cv_std = 0.0

        existing_idx = -1
        for idx, e in enumerate(self.experiments):
            if e.get('dataset_id') == dataset_id and e.get('model_name') == model_name:
                existing_idx = idx
                break

        exp_id = existing_idx + 1 if existing_idx != -1 else len(self.experiments) + 1

        experiment = {
            "experiment_id": exp_id,
            "dataset_id": dataset_id,
            "model_name": model_name,
            "hyperparameters": hyperparameters,
            "metrics": metrics,
            "cv_scores": [float(s) for s in cv_scores],
            "cv_mean": cv_mean,
            "cv_std": cv_std,
            "training_time": round(training_time, 4),
            "prediction_time": round(prediction_time, 6),
            "model_file_path": model_file_path,
            "features_used": features_used,
            "timestamp": datetime.now().isoformat(),
            "model_version": f"{model_name}_v{exp_id}"
        }

        if existing_idx != -1:
            self.experiments[existing_idx] = experiment
        else:
            self.experiments.append(experiment)

        self._save_experiments()
        return experiment
    
    def get_all_experiments(self) -> List[Dict]:
        unique = {}
        for e in self.experiments:
            key = (e.get('dataset_id'), e.get('model_name'))
            unique[key] = e
        return list(unique.values())
    
    def get_experiments_by_dataset(self, dataset_id: str) -> List[Dict]:
        unique = {}
        for e in self.experiments:
            if e.get('dataset_id') == dataset_id:
                unique[e.get('model_name')] = e
        return list(unique.values())
    
    def get_best_experiment(self, dataset_id: str, metric: str = 'roc_auc') -> Optional[Dict]:
        exps = self.get_experiments_by_dataset(dataset_id)
        if not exps:
            return None
        return max(exps, key=lambda e: e.get('metrics', {}).get(metric, 0))
    
    def get_experiments_comparison(self, dataset_id: str = None) -> List[Dict]:
        exps = self.experiments if dataset_id is None else self.get_experiments_by_dataset(dataset_id)
        return sorted(exps, key=lambda e: e.get('metrics', {}).get('roc_auc', 0), reverse=True)
