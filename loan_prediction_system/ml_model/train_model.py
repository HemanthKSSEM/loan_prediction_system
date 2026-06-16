import os
import pandas as pd
import numpy as np
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

def train_models():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Project dataset path
    data_path = os.path.join(base_dir, '..', 'dataset', 'loan_data.csv')
    
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}")
        return
        
    print("Loading project dataset...")
    df = pd.read_csv(data_path)
    
    # Clean column names (remove leading/trailing spaces)
    df.columns = df.columns.str.strip()
    
    # Clean string values
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()
            
    # Separate features and target
    X = df.drop('loan_status', axis=1)
    y = df['loan_status'].apply(lambda x: 1 if x == 'Approved' else 0)
    
    # Preprocessing
    print("Preprocessing data...")
    encoders = {}
    
    for col in X.columns:
        if X[col].dtype == 'object':
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col])
            encoders[col] = le
            
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    # Model saving directory
    model_dir = os.path.join(base_dir, 'saved_models')
    os.makedirs(model_dir, exist_ok=True)
    
    # Save preprocessing objects
    joblib.dump(encoders, os.path.join(model_dir, 'encoders.pkl'))
    joblib.dump(scaler, os.path.join(model_dir, 'scaler.pkl'))
    joblib.dump(list(X.columns), os.path.join(model_dir, 'feature_columns.pkl'))
    
    # Train Decision Tree
    print("Training Decision Tree...")
    dt_model = DecisionTreeClassifier(max_depth=5, random_state=42)
    dt_model.fit(X_train, y_train)
    dt_pred = dt_model.predict(X_test)
    print(f"DT Accuracy: {accuracy_score(y_test, dt_pred):.4f}")
    joblib.dump(dt_model, os.path.join(model_dir, 'dt_model.pkl'))
    
    # Train ANN
    print("Training ANN...")
    ann_model = Sequential([
        Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    
    ann_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    ann_model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.1, verbose=0)
    
    _, ann_accuracy = ann_model.evaluate(X_test, y_test, verbose=0)
    print(f"ANN Accuracy: {ann_accuracy:.4f}")
    ann_model.save(os.path.join(model_dir, 'ann_model.h5'))
    
    print("Training complete! Models saved.")

if __name__ == "__main__":
    train_models()
