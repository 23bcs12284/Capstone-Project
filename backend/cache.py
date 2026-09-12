import os
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from config.dataset_config import get_all_dataset_ids, get_dataset_config, get_dataset_path

logger = logging.getLogger(__name__)

class DatasetCacheManager:
    """
    In-memory caching manager for dataset metadata, basic metrics, and detail calculations.
    Prevents repeated CSV disk reads and dynamic statistics computations on every HTTP request.
    """
    def __init__(self):
        self._summary_cache: Dict[str, Dict[str, Any]] = {}
        self._detail_cache: Dict[str, Dict[str, Any]] = {}
        self._file_mtimes: Dict[str, float] = {}

    def _is_cache_valid(self, dataset_id: str) -> bool:
        try:
            path = get_dataset_path(dataset_id)
            if not os.path.exists(path):
                return False
            current_mtime = os.path.getmtime(path)
            cached_mtime = self._file_mtimes.get(dataset_id)
            return cached_mtime == current_mtime
        except Exception:
            return False

    def get_dataset_summary(self, dataset_id: str) -> Dict[str, Any]:
        if self._is_cache_valid(dataset_id) and dataset_id in self._summary_cache:
            return self._summary_cache[dataset_id]

        config = get_dataset_config(dataset_id)
        path = get_dataset_path(dataset_id)
        rows, missing_values, approval_rate = 0, 0, 0.0

        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                rows = len(df)
                missing_values = int(df.isnull().sum().sum())
                if config["target_column"] in df.columns:
                    approval_rate = float(df[config["target_column"]].mean())
                self._file_mtimes[dataset_id] = os.path.getmtime(path)
            except Exception as e:
                logger.error(f"Error reading dataset {dataset_id}: {e}")

        summary = {
            "dataset_id": dataset_id,
            "name": config["name"],
            "rows": rows,
            "features": len(config["numeric_features"]) + len(config["categorical_features"]),
            "target": config["target_column"],
            "approval_rate": approval_rate,
            "missing_values": missing_values,
            "description": config.get("description", "")
        }
        self._summary_cache[dataset_id] = summary
        return summary

    def get_all_summaries(self) -> list:
        return [self.get_dataset_summary(d_id) for d_id in get_all_dataset_ids()]

    def get_dataset_detail(self, dataset_id: str) -> Dict[str, Any]:
        if self._is_cache_valid(dataset_id) and dataset_id in self._detail_cache:
            return self._detail_cache[dataset_id]

        config = get_dataset_config(dataset_id)
        path = get_dataset_path(dataset_id)
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dataset file for {dataset_id} not found at {path}")

        df = pd.read_csv(path)
        num_cols = config.get("numeric_features", [])
        cat_cols = config.get("categorical_features", [])

        # Numerical statistics
        num_stats = {}
        for col in num_cols:
            if col in df.columns:
                s = df[col].dropna()
                num_stats[col] = {
                    "mean": float(s.mean()),
                    "std": float(s.std()),
                    "min": float(s.min()),
                    "max": float(s.max()),
                    "median": float(s.median())
                }

        # Categorical distribution
        cat_stats = {}
        for col in cat_cols:
            if col in df.columns:
                cat_stats[col] = df[col].value_counts().to_dict()

        # Target distribution
        target_col = config.get("target_column")
        target_dist = df[target_col].value_counts().to_dict() if target_col in df.columns else {}

        # Correlation matrix for numeric features
        corr_matrix = {}
        existing_num_cols = [c for c in num_cols if c in df.columns]
        if existing_num_cols:
            corr_df = df[existing_num_cols].corr().fillna(0)
            corr_matrix = corr_df.to_dict()

        detail = {
            "summary": self.get_dataset_summary(dataset_id),
            "numeric_stats": num_stats,
            "categorical_stats": cat_stats,
            "target_distribution": target_dist,
            "correlation_matrix": corr_matrix,
            "columns": list(df.columns)
        }

        self._detail_cache[dataset_id] = detail
        return detail

dataset_cache = DatasetCacheManager()
