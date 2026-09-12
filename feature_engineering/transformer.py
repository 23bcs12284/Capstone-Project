import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from typing import List, Dict, Any

class FeatureTransformer:
    def __init__(self, numeric_cols: List[str] = None, categorical_cols: List[str] = None):
        self.numeric_cols = numeric_cols or [
            "age", "income", "coapplicant_income", "credit_score", 
            "loan_amount", "loan_term", "employment_years", "dti"
        ]
        self.categorical_cols = categorical_cols or [
            "gender", "race", "home_ownership", "education", 
            "self_employed", "dependents", "property_area"
        ]
        
        self.scaler = StandardScaler()
        # Drop first to avoid multicollinearity for linear models, or keep all for tree models.
        # For XAI, keeping all categories is often clearer because we see feature impact for each value explicitly.
        # We will keep all categories (sparse_output=False).
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        
        self.transformed_feature_names: List[str] = []
        self.is_fitted = False

    def fit(self, X: pd.DataFrame) -> "FeatureTransformer":
        """
        Fits the scaler on numeric columns and the encoder on categorical columns.
        """
        # Exclude columns not in dataset
        self.numeric_cols = [c for c in self.numeric_cols if c in X.columns]
        self.categorical_cols = [c for c in self.categorical_cols if c in X.columns]
        
        # Fit scaler
        if self.numeric_cols:
            self.scaler.fit(X[self.numeric_cols])
            
        # Fit encoder
        if self.categorical_cols:
            self.encoder.fit(X[self.categorical_cols].astype(str))
            # Get output feature names for categorical columns
            encoded_names = self.encoder.get_feature_names_out(self.categorical_cols).tolist()
        else:
            encoded_names = []
            
        # Combine feature names: scaled numeric columns first, then encoded categorical columns
        self.transformed_feature_names = self.numeric_cols + encoded_names
        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Applies scaling and encoding to input DataFrame and returns a new DataFrame with correct column names.
        """
        if not self.is_fitted:
            raise ValueError("FeatureTransformer must be fitted before transforming data.")
            
        # Numeric transformation
        if self.numeric_cols:
            scaled_numeric = self.scaler.transform(X[self.numeric_cols])
            df_numeric = pd.DataFrame(scaled_numeric, columns=self.numeric_cols, index=X.index)
        else:
            df_numeric = pd.DataFrame(index=X.index)
            
        # Categorical transformation
        if self.categorical_cols:
            encoded_categorical = self.encoder.transform(X[self.categorical_cols].astype(str))
            encoded_names = self.encoder.get_feature_names_out(self.categorical_cols)
            df_categorical = pd.DataFrame(encoded_categorical, columns=encoded_names, index=X.index)
        else:
            df_categorical = pd.DataFrame(index=X.index)
            
        # Concatenate features
        X_trans = pd.concat([df_numeric, df_categorical], axis=1)
        
        # Reorder to match self.transformed_feature_names exactly
        X_trans = X_trans[self.transformed_feature_names]
        
        return X_trans

    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return self.fit(X).transform(X)

    def get_feature_names_out(self, input_features=None) -> List[str]:
        return self.transformed_feature_names

