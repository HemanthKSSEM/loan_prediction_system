import os
import joblib
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

class PredictionEngine:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = os.path.join(self.base_dir, 'saved_models')
        
        self.dt_model = None
        self.ann_model = None
        self.encoders = None
        self.scaler = None
        self.feature_columns = None
        
        self.load_models()

    def load_models(self):
        try:
            self.dt_model = joblib.load(os.path.join(self.model_dir, 'dt_model.pkl'))
            self.encoders = joblib.load(os.path.join(self.model_dir, 'encoders.pkl'))
            self.scaler = joblib.load(os.path.join(self.model_dir, 'scaler.pkl'))
            self.feature_columns = joblib.load(os.path.join(self.model_dir, 'feature_columns.pkl'))
        except Exception as e:
            print(f"DT Models not loaded: {e}")

        try:
            self.ann_model = load_model(os.path.join(self.model_dir, 'ann_model.h5'))
        except Exception as e:
            print(f"ANN Model not loaded: {e}")

    def predict(self, application, use_ann=True):
        if not self.encoders or not self.scaler or not self.feature_columns:
            raise Exception("Models not properly loaded. Please train first.")
            
        features = {
            'age': getattr(application, 'age', 30),
            'gender': getattr(application, 'gender', 'Male'),
            'marital_status': getattr(application, 'marital_status', 'Single'),
            'dependents': getattr(application, 'dependents', 0),
            'education': getattr(application, 'education', 'Graduate'),
            'self_employed': getattr(application, 'self_employed', 'No'),
            'employment_type': getattr(application, 'employment_type', 'Salaried'),
            'income': float(getattr(application, 'income_annum', 50000)),
            'co_applicant_income': 0.0,  # Default value
            'existing_loan': 'No',  # Default value
            'loan_amount': float(getattr(application, 'loan_amount', 500000)),
            'loan_term': getattr(application, 'loan_term', 36),
            'credit_history': 1.0 if getattr(application, 'cibil_score', 750) >= 650 else 0.0,
            'property_area': getattr(application, 'property_area', 'Urban'),
            'residential_assets_value': float(getattr(application, 'residential_assets_value', 0)),
            'commercial_assets_value': float(getattr(application, 'commercial_assets_value', 0)),
            'luxury_assets_value': float(getattr(application, 'luxury_assets_value', 0)),
            'bank_asset_value': float(getattr(application, 'bank_asset_value', 0)),
        }
        
        df = pd.DataFrame([features])
        
        # Ensure columns are in the same order as training
        df = df[self.feature_columns]
        
        for col, le in self.encoders.items():
            if col in df.columns:
                try:
                    df[col] = le.transform(df[col])
                except:
                    df[col] = 0
                    
        X_scaled = self.scaler.transform(df)
        
        if use_ann and self.ann_model:
            prob = self.ann_model.predict(X_scaled)[0][0]
            status = 'Approved' if prob >= 0.5 else 'Rejected'
            confidence = prob if prob >= 0.5 else (1 - prob)
        else:
            if not self.dt_model:
                raise Exception("Decision Tree model not loaded.")
            prob = self.dt_model.predict_proba(X_scaled)[0][1]
            status = 'Approved' if prob >= 0.5 else 'Rejected'
            confidence = prob if prob >= 0.5 else (1 - prob)
            
        return {
            'status': status,
            'confidence': float(confidence) * 100
        }
