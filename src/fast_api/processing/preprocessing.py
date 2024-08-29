from sklearn.base import BaseEstimator, TransformerMixin

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline





class MapPhoneService(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        # Map 'PhoneService' values to numeric (1 for 'Yes', 0 for 'No')
        phone_service_mapping = {'Yes': 1, 'No': 0}
        X['PhoneService'] = X['PhoneService'].map(phone_service_mapping).fillna(0).astype(int)
        return X

class ImputeTenure(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
    
    def fit(self, X, y=None):
        return self
    
    def process_value(self,x):
        
        try:
            return int(round(float(x)))
        except (ValueError, TypeError):
            # Handle values that cannot be converted
            print(f"Invalid tenure value: {x}")
            return None
          
    def transform(self, X):
        
        X = X.copy()
        X['tenure'] = X['tenure'].apply(self.process_value)
        return X



class ImputeTotalCharges(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass  
    
    def fit(self, X, y=None):
        return self
    
    def process_value(self, x):
        try:
            return float(x)
        except (ValueError, TypeError):
            # Log or handle values that cannot be converted
            print(f"Invalid TotalCharges value: {x}")
            return None  # Keep as None if invalid, or raise an error if preferred

    def transform(self, X):
        X = X.copy()
        # Apply conversion to 'TotalCharges'
        X['TotalCharges'] = X['TotalCharges'].apply(self.process_value)
        return X



class OneHotEncodeContract(BaseEstimator, TransformerMixin):
    def __init__(self, contract_types=None):
        if contract_types is None:
            self.contract_types = ['Month-to-month', 'One year', 'Two year']
        else:
            self.contract_types = contract_types
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        if hasattr(X['Contract'].iloc[0], 'value'):
            X['Contract'] = X['Contract'].apply(lambda x: x.value)
        else:
            X['Contract'] = X['Contract'].astype(str)
        dummies = pd.get_dummies(X['Contract'], prefix='Contract').astype(int)
        for contract_type in self.contract_types:
            if f'Contract_{contract_type}' not in dummies.columns:
                dummies[f'Contract_{contract_type}'] = 0
        
        X = X.join(dummies)
        return X


pipeline = Pipeline([
        
            ('map_phone_service', MapPhoneService()),
            ('impute_tenure', ImputeTenure()),
            ('impute_total_charges', ImputeTotalCharges()),
            ('one_hot_encode_contract', OneHotEncodeContract()),
       
])

