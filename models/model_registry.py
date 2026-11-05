import sys
import types
import os
import json
import pickle
import threading
import logging
import warnings
from typing import Dict, Any, List, Optional
from pathlib import Path
import sklearn._loss
import sklearn.ensemble

logger = logging.getLogger(__name__)

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


def to_relative_path(path_str: Optional[str]) -> str:
    """
    Normalizes any path (local absolute, remote absolute, or relative)
    to a portable relative path based on 'models_saved' or 'artifacts'.
    E.g.:
      '/Users/.../models_saved/loan_data/logistic_regression.pkl' -> 'models_saved/loan_data/logistic_regression.pkl'
      '/app/models_saved/scaler_loan_data.pkl' -> 'models_saved/scaler_loan_data.pkl'
    """
    if not path_str:
        return ""
    norm = str(path_str).replace("\\", "/").strip()
    for root_dir in ["models_saved", "artifacts"]:
        if root_dir in norm:
            idx = norm.find(root_dir)
            return norm[idx:]
    return norm


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
                        data = json.load(f)
                    # Normalize in-memory paths to portable relative paths
                    for m in data:
                        if 'model_file_path' in m:
                            m['model_file_path'] = to_relative_path(m.get('model_file_path'))
                        if 'scaler_path' in m:
                            m['scaler_path'] = to_relative_path(m.get('scaler_path'))
                        if 'cleaner_path' in m:
                            m['cleaner_path'] = to_relative_path(m.get('cleaner_path'))
                    return data
                except Exception as e:
                    logger.error(f"Error loading registry: {e}")
            return []
            
    def _save_registry(self):
        with self._lock:
            try:
                with open(self.registry_file, 'w') as f:
                    json.dump(self.models, f, indent=2, default=str)
            except Exception as e:
                logger.error(f"Error saving registry: {e}")

    @staticmethod
    def resolve_path(raw_path: Optional[str], dataset_id: Optional[str] = None, fallback_filename: Optional[str] = None) -> Path:
        """
        Dynamically resolves a model, scaler, or cleaner path to an existing absolute Path
        on the current filesystem (local machine, Docker container /app, Render, Railway, etc.).
        """
        candidates: List[Path] = []
        
        rel = to_relative_path(raw_path)
        if rel:
            candidates.append((BASE_DIR / rel).resolve())
            
        if raw_path:
            p = Path(raw_path)
            if p.is_absolute():
                candidates.append(p.resolve())
            candidates.append((BASE_DIR / p).resolve())
            
        if dataset_id and fallback_filename:
            candidates.append((BASE_DIR / "models_saved" / dataset_id / fallback_filename).resolve())
            
        if fallback_filename:
            candidates.append((BASE_DIR / "models_saved" / fallback_filename).resolve())
            
        if raw_path:
            fname = Path(raw_path).name
            if dataset_id:
                candidates.append((BASE_DIR / "models_saved" / dataset_id / fname).resolve())
            candidates.append((BASE_DIR / "models_saved" / fname).resolve())
            
        # Deduplicate while preserving lookup priority
        seen = set()
        deduped_candidates = []
        for c in candidates:
            c_str = str(c)
            if c_str not in seen:
                seen.add(c_str)
                deduped_candidates.append(c)
                
        for cand in deduped_candidates:
            if cand.exists() and cand.is_file():
                return cand
                
        available_models = []
        models_dir = BASE_DIR / "models_saved"
        if models_dir.exists():
            available_models = [str(f.relative_to(BASE_DIR)) for f in models_dir.rglob("*.pkl")]
            
        err_msg = (
            f"Model artifact not found for path '{raw_path}'. "
            f"Attempted search locations:\n" + "\n".join(f"  - {str(c)}" for c in deduped_candidates) +
            f"\nAvailable files in {models_dir}:\n" +
            ("\n".join(f"  - {m}" for m in available_models) if available_models else "  (No .pkl files found)")
        )
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)
    
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
            "model_file_path": to_relative_path(model_file_path),
            "metrics": metrics,
            "hyperparameters": hyperparameters,
            "features_used": features_used,
            "scaler_path": to_relative_path(scaler_path),
            "cleaner_path": to_relative_path(cleaner_path),
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
        """Load the actual sklearn model from disk using dynamic path resolution."""
        meta = self.get_model(dataset_id, model_name)
        if not meta:
            raise ValueError(f"Model {model_name} for dataset {dataset_id} not found in registry.")
        model_path = self.resolve_path(
            meta.get('model_file_path', ''),
            dataset_id=dataset_id,
            fallback_filename=f"{model_name}.pkl"
        )
        logger.info(f"Loading model object for {model_name} ({dataset_id}) from: {model_path}")
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    
    def load_pipeline(self, dataset_id: str, model_name: str):
        """Load model + scaler + cleaner for prediction using dynamic path resolution."""
        meta = self.get_model(dataset_id, model_name)
        if not meta:
            raise ValueError(f"Model {model_name} for dataset {dataset_id} not found in registry.")
        model_path = self.resolve_path(
            meta.get('model_file_path', ''),
            dataset_id=dataset_id,
            fallback_filename=f"{model_name}.pkl"
        )
        scaler_path = self.resolve_path(
            meta.get('scaler_path', ''),
            dataset_id=dataset_id,
            fallback_filename=f"scaler_{dataset_id}.pkl"
        )
        cleaner_path = self.resolve_path(
            meta.get('cleaner_path', ''),
            dataset_id=dataset_id,
            fallback_filename=f"cleaner_{dataset_id}.pkl"
        )
        logger.info(
            f"Loading pipeline for {model_name} on {dataset_id}:\n"
            f"  - Model:   {model_path}\n"
            f"  - Scaler:  {scaler_path}\n"
            f"  - Cleaner: {cleaner_path}"
        )
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        with open(cleaner_path, 'rb') as f:
            cleaner = pickle.load(f)
        return model, scaler, cleaner
