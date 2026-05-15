import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# --- THIS IS THE FIX ---
# This line tells Python to ignore the UserWarning from scikit-learn
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
# --- END OF FIX ---


def load_data():
    """Load the EHR sample data"""
    try:
        df = pd.read_csv('data/synthetic_health_data.csv')
        print(f"✓ Data loaded successfully! Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print("✗ Error: synthetic_health_data.csv not found in data folder")
        return None

# ---
# --- MODIFIED: This function now CREATES 3 risk levels ---
# ---
def create_risk_labels(df):
    """Create 3-level risk labels (0=Low, 1=Moderate, 2=High)"""
    
    # We create a risk score by counting risk factors
    conditions = [
        (df['bmi'] > 25),              # Overweight
        (df['systolic_bp'] > 130),    # Elevated BP
        (df['diastolic_bp'] > 80),    # Elevated BP
        (df['cholesterol'] > 200),    # Borderline High
        (df['glucose'] > 100),        # Prediabetes
        (df['smoking'] == 1),
        (df['family_history'] == 1),
        (df['exercise_hours'] < 2)
    ]
    
    # Sum up all the risk factors for each patient
    risk_score = sum(conditions)
    
    # Classify based on the total score
    # 0-2 factors = Low (0)
    # 3-4 factors = Moderate (1)
    # 5+ factors  = High (2)
    labels = np.where(risk_score >= 5, 2,  # High risk
                      np.where(risk_score >= 3, 1, 0)) # Moderate or Low risk
    
    print("\n✓ Risk labels generated (0=Low, 1=Moderate, 2=High):")
    print(pd.Series(labels).value_counts())
    
    return labels
# --- END MODIFICATION ---


def preprocess_data(df):
    """Preprocess the data for training"""
    
    feature_columns = [
        'age', 'gender', 'bmi', 'systolic_bp', 'diastolic_bp', 
        'cholesterol', 'glucose', 'smoking', 'family_history', 
        'exercise_hours'
    ]
    
    # Handle missing values
    for col in feature_columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(df[col].mode().iloc[0])

    X = df[feature_columns]
    
    # ---
    # --- MODIFIED: We now ALWAYS use our new 3-level function
    # ---
    y = create_risk_labels(df)
    # --- END MODIFICATION ---
        
    return X, y

def train_and_evaluate(model, X_train, y_train, X_test, y_test):
    """A helper function to train and evaluate a given model"""
    model_name = model.__class__.__name__
    print("\n" + "-" * 20)
    print(f"🤖 Training {model_name}...")
    print("-" * 20)
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✓ {model_name} trained successfully!")
    print(f"✓ Accuracy: {accuracy:.2%}")
    print(f"\n📊 Classification Report ({model_name}):\n{classification_report(y_test, y_pred, zero_division=0)}")
    
    if hasattr(model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        print(f"\n📈 Top Features ({model_name}):")
        print(feature_importance.head(5))
    
    return model, accuracy

def save_model(model, filename):
    """Save the trained model with a specific filename"""
    with open(filename, 'wb') as f:
        pickle.dump(model, f)
    print(f"\n✓ Model saved as '{filename}'")


if __name__ == '__main__':
    print("=" * 60)
    print("🏥 EHR Chronic Disease Risk Prediction - 3-Level Model Training")
    print("=" * 60)
    
    df = load_data()
    
    if df is not None:
        X, y = preprocess_data(df)
        
        if X is not None and y is not None:
            # Split data ONCE
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            print(f"\n✓ Data split: {X_train.shape[0]} training, {X_test.shape[0]} test samples.")

            # --- 1. Train Gradient Boosting ---
            gb_model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
            gb_model, gb_accuracy = train_and_evaluate(gb_model, X_train, y_train, X_test, y_test)
            if gb_model:
                save_model(gb_model, 'model_gb.pkl')

            # --- 2. Train XGBoost ---
            xgb_model = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42, eval_metric='mlogloss')
            xgb_model, xgb_accuracy = train_and_evaluate(xgb_model, X_train, y_train, X_test, y_test)
            if xgb_model:
                save_model(xgb_model, 'model_xgb.pkl')

            # --- 3. Final Comparison ---
            print("\n" + "=" * 60)
            print("✅ Training completed successfully!")
            print("\n--- 📊 Final Accuracy Comparison ---")
            print(f"  Gradient Boosting: {gb_accuracy:.2%}")
            print(f"  XGBoost:           {xgb_accuracy:.2%}")
            print("=" * 60)
        else:
            print("\n✗ Data preprocessing failed.")
    else:
        print("\n✗ Data loading failed.")