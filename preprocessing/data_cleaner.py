import pandas as pd
import numpy as np
from typing import Dict, Any, List

class DataCleaner:
    def __init__(self, numeric_impute_strategy: str = "median", categorical_impute_strategy: str = "most_frequent", skip_columns: List[str] = None):
        self.numeric_impute_strategy = numeric_impute_strategy
        self.categorical_impute_strategy = categorical_impute_strategy
        self.skip_columns = set(skip_columns or ["applicant_id", "loan_status", "application_id", "app_id", "loan_approved"])
        self.numeric_defaults: Dict[str, float] = {}
        self.categorical_defaults: Dict[str, str] = {}
        self.clipping_thresholds: Dict[str, float] = {}
        self.is_fitted = False

    def fit(self, df: pd.DataFrame) -> "DataCleaner":
        """
        Learns columns' median values, modes, and outlier clipping thresholds (99th percentile) from the training set.
        """
        # Exclude ID and target label if present
        cols_to_fit = [c for c in df.columns if c not in self.skip_columns]
        
        for col in cols_to_fit:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Learn imputation default
                if self.numeric_impute_strategy == "median":
                    self.numeric_defaults[col] = float(df[col].median())
                else:
                    self.numeric_defaults[col] = float(df[col].mean())
                
                # Learn clipping default (99th percentile)
                self.clipping_thresholds[col] = float(df[col].quantile(0.99))
            else:
                # Learn imputation default
                self.categorical_defaults[col] = str(df[col].mode().iloc[0])
                
        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies learned imputations and outlier clipping to the input dataframe.
        """
        if not self.is_fitted:
            raise ValueError("DataCleaner must be fitted on training data before transforming.")
            
        df_clean = df.copy()
        
        # Apply imputation and clipping
        for col in df_clean.columns:
            if col in self.skip_columns:
                continue
                
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                # Fill missing
                fill_val = self.numeric_defaults.get(col, 0.0)
                df_clean[col] = df_clean[col].fillna(fill_val)
                
                # Clip outliers (at the high end, and floor at 0 for numeric variables that shouldn't be negative)
                clip_val = self.clipping_thresholds.get(col)
                if clip_val is not None:
                    # Clip values above 99th percentile
                    df_clean[col] = np.clip(df_clean[col], 0.0, clip_val)
            else:
                # Fill missing
                fill_val = self.categorical_defaults.get(col, "Unknown")
                df_clean[col] = df_clean[col].fillna(fill_val)
                df_clean[col] = df_clean[col].astype(str)
                
        return df_clean

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)
        
    def transform_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms a single dictionary prediction payload.
        """
        if not self.is_fitted:
            raise ValueError("DataCleaner must be fitted on training data first.")
            
        cleaned = data.copy()
        
        # Ensure all numeric and categorical columns fitted during training are present
        for col, default_val in self.numeric_defaults.items():
            if col not in cleaned or cleaned[col] is None or cleaned[col] == "":
                cleaned[col] = default_val

        for col, default_val in self.categorical_defaults.items():
            if col not in cleaned or cleaned[col] is None or cleaned[col] == "":
                cleaned[col] = default_val

        for col, val in list(cleaned.items()):
            if col in self.skip_columns:
                continue
                
            # If value is None, fill with default
            if val is None or val == "":
                if col in self.numeric_defaults:
                    cleaned[col] = self.numeric_defaults[col]
                elif col in self.categorical_defaults:
                    cleaned[col] = self.categorical_defaults[col]
            else:
                # Clip numeric inputs
                if col in self.numeric_defaults:
                    try:
                        num_val = float(val)
                        clip_val = self.clipping_thresholds.get(col)
                        if clip_val is not None:
                            cleaned[col] = min(max(num_val, 0.0), clip_val)
                        else:
                            cleaned[col] = max(num_val, 0.0)
                    except (ValueError, TypeError):
                        pass
        return cleaned
