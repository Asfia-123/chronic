import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    """Load the EHR sample data"""
    try:
        df = pd.read_csv('data/ehr_sample.csv')
        print(f"✓ Data loaded successfully! Shape: {df.shape}")
        print(f"\nColumns: {df.columns.tolist()}")
        print(f"\nFirst few rows:\n{df.head()}")
        return df
    except FileNotFoundError:
        print("✗ Error: ehr_sample.csv not found in data folder")
        return None

def preprocess_data(df):
    """Preprocess the data for training"""
    # Assuming your CSV has these columns
    # Adjust based on your actual CSV structure
    
    # Define features
    feature_columns = [
        'age', 'bmi', 'systolic_bp', 'diastolic_bp', 'cholesterol',
        'glucose', 'postprandial_glucose', 'hba1c', 'family_history',
        'exercise_hours', 'serum_creatinine', 'gfr', 'blood_urea_nitrogen',
        'urine_albumin', 'serum_potassium', 'hemoglobin', 'gender'
    ]
    
    # Handle missing values
    df = df.fillna(df.median(numeric_only=True))
    
    # Extract features and target
    X = df[feature_columns]
    
    # Assuming you have a 'risk_level' column with values: 0 (Low), 1 (Moderate), 2 (High)
    # Or you can create it based on certain conditions
    if 'risk_level' in df.columns:
        y = df['risk_level']
    else:
        # Create risk level based on multiple conditions
        y = create_risk_labels(df)
    
    return X, y

def create_risk_labels(df):
    """Create risk labels based on health parameters"""
    risk_score = 0
    
    # Simple risk scoring logic
    conditions = [
        df['glucose'] > 126,
        df['hba1c'] > 6.5,
        df['systolic_bp'] > 140,
        df['cholesterol'] > 240,
        df['gfr'] < 60,
        df['bmi'] > 30
    ]
    
    risk_score = sum(conditions)
    
    # Classify risk
    labels = np.where(risk_score >= 4, 2,  # High risk
                     np.where(risk_score >= 2, 1, 0))  # Moderate or Low risk
    
    return labels

def train_model(X, y):
    """Train the machine learning model"""
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n✓ Training set: {X_train.shape}")
    print(f"✓ Test set: {X_test.shape}")
    
    # Train Gradient Boosting Classifier (usually better for medical data)
    print("\n🤖 Training AI model...")
    model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✓ Model trained successfully!")
    print(f"✓ Accuracy: {accuracy:.2%}")
    print(f"\n📊 Classification Report:\n{classification_report(y_test, y_pred)}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n📈 Top 10 Important Features:")
    print(feature_importance.head(10))
    
    # Save confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig('confusion_matrix.png')
    print("✓ Confusion matrix saved as 'confusion_matrix.png'")
    
    # Save feature importance plot
    plt.figure(figsize=(10, 6))
    feature_importance.head(10).plot(x='feature', y='importance', kind='barh')
    plt.title('Top 10 Feature Importance')
    plt.xlabel('Importance')
    plt.tight_layout()
    plt.savefig('feature_importance.png')
    print("✓ Feature importance plot saved as 'feature_importance.png'")
    
    return model

def save_model(model):
    """Save the trained model"""
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("\n✓ Model saved as 'model.pkl'")

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 EHR Chronic Disease Risk Prediction - Model Training")
    print("=" * 60)
    
    # Load data
    df = load_data()
    
    if df is not None:
        # Preprocess
        X, y = preprocess_data(df)
        
        # Train
        model = train_model(X, y)
        
        # Save
        save_model(model)
        
        print("\n" + "=" * 60)
        print("✅ Training completed successfully!")
        print("=" * 60)