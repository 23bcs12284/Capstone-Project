import sys
import types
import os
import json
import pickle
import threading
import warnings
from typing import Dict, Any, List, Optional
from pathlib import Path
import sklearn._loss
import sklearn.ensemble

# Handle sklearn GradientBoosting _loss module & CyHalfBinomialLoss compatibility across versions
loss_mod = types.ModuleType('_loss')
for k, v in sklearn._loss.__dict__.items():
    setattr(loss_mod, k, v)
for k, v in sklearn.ensemble.__dict__.items():
    if not hasattr(loss_mod, k):
        setattr(loss_mod, k, v)
if hasattr(sklearn._loss, 'HalfBinomialLoss'):
    setattr(loss_mod, 'CyHalfBinomialLoss', sklearn._loss.HalfBinomialLoss)
sys.modules['_loss'] = loss_mod

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
REGISTRY_DIR = BASE_DIR / "artifacts"
REGISTRY_FILE = REGISTRY_DIR / "model_registry.json"

class ModelRegistry:
    def __init__(self):
        os.makedirs(REGISTRY_DIR, exist_ok=True)
        self.registry_file = REGISTRY_FILE
        self._lock = threading.Lock()
        self.models = self._load_registry()
    
    def _load_registry(self) -> List[Dict[str, Any]]:
        with self._lock:
            if self.registry_file.exists():
                try:
                    with open(self.registry_file, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Error loading registry: {e}")
            return []
            
    def _save_registry(self):
        with self._lock:
            try:
                with open(self.registry_file, 'w') as f:
                    json.dump(self.models, f, indent=2, default=str)
            except Exception as e:
                print(f"Error saving registry: {e}")
    
    def register_model(self, dataset_id: str, model_name: str, model_file_path: str, 
                       metrics: dict, hyperparameters: dict, features_used: list, 
                       scaler_path: str, cleaner_path: str) -> dict:
        """Register or update a trained model with its metadata."""
        existing_idx = -1
        for idx, m in enumerate(self.models):
            if m.get('dataset_id') == dataset_id and m.get('model_name') == model_name:
                existing_idx = idx
                break
                
        version_num = 1
        if existing_idx != -1:
            prev_ver = self.models[existing_idx].get('model_version', '')
            if '_v' in prev_ver:
                try:
                    version_num = int(prev_ver.split('_v')[-1]) + 1
                except ValueError:
                    version_num = 2
                    
        model_version = f"{model_name}_v{version_num}"
        
        model_entry = {
            "dataset_id": dataset_id,
            "model_name": model_name,
            "model_version": model_version,
            "model_file_path": model_file_path,
            "metrics": metrics,
            "hyperparameters": hyperparameters,
            "features_used": features_used,
            "scaler_path": scaler_path,
            "cleaner_path": cleaner_path,
            "status": "registered"
        }
        
        if existing_idx != -1:
            self.models[existing_idx] = model_entry
        else:
            self.models.append(model_entry)
            
        self._save_registry()
        return model_entry
    
    def get_model(self, dataset_id: str, model_name: str) -> Optional[dict]:
        """Get latest model metadata by dataset and name."""
        dataset_models = [m for m in self.models if m.get('dataset_id') == dataset_id and m.get('model_name') == model_name]
        if not dataset_models:
            return None
        return dataset_models[-1]
    
    def get_models_for_dataset(self, dataset_id: str) -> list:
        """Get unique latest models for a dataset."""
        unique = {}
        for m in self.models:
            if m.get('dataset_id') == dataset_id:
                unique[m.get('model_name')] = m
        return list(unique.values())
    
    def get_all_models(self) -> list:
        """Get unique latest registered models across all datasets."""
        unique = {}
        for m in self.models:
            key = (m.get('dataset_id'), m.get('model_name'))
            unique[key] = m
        return list(unique.values())
    
    def get_best_model(self, dataset_id: str, metric: str = 'roc_auc') -> Optional[dict]:
        """Get the best model for a dataset by a given metric."""
        dataset_models = self.get_models_for_dataset(dataset_id)
        if not dataset_models:
            return None
        return max(dataset_models, key=lambda m: m.get('metrics', {}).get(metric, 0))
    
    def get_recommendation(self, dataset_id: str) -> dict:
        """Generate a dynamic recommendation comparing models."""
        dataset_models = self.get_models_for_dataset(dataset_id)
        if not dataset_models:
            return {"recommendation": "No models available for this dataset."}
            
        best_roc_auc = max(dataset_models, key=lambda m: m.get('metrics', {}).get('roc_auc', 0))
        best_f1 = max(dataset_models, key=lambda m: m.get('metrics', {}).get('f1_score', 0))
        
        return {
            "best_roc_auc_model": best_roc_auc['model_name'],
            "best_f1_model": best_f1['model_name'],
            "recommendation": f"Model {best_roc_auc['model_name']} provides the best ROC-AUC. Model {best_f1['model_name']} provides the best F1 Score."
        }
    
    def load_model_object(self, dataset_id: str, model_name: str):
        """Load the actual sklearn model from disk."""
        meta = self.get_model(dataset_id, model_name)
        if not meta:
            raise ValueError(f"Model {model_name} for dataset {dataset_id} not found in registry.")
        with open(meta['model_file_path'], 'rb') as f:
            return pickle.load(f)
    
    def load_pipeline(self, dataset_id: str, model_name: str):
        """Load model + scaler + cleaner for prediction."""
        meta = self.get_model(dataset_id, model_name)
        if not meta:
            raise ValueError(f"Model {model_name} for dataset {dataset_id} not found in registry.")
        with open(meta['model_file_path'], 'rb') as f:
            model = pickle.load(f)
        with open(meta['scaler_path'], 'rb') as f:
            scaler = pickle.load(f)
        with open(meta['cleaner_path'], 'rb') as f:
            cleaner = pickle.load(f)
        return model, scaler, cleaner
