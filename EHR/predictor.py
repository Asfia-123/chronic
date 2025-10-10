import pickle
import numpy as np
from preprocess import preprocess_input

def load_model():
    """Load the trained model"""
    try:
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)
        print("✓ Model loaded successfully!")
        return model
    except FileNotFoundError:
        print("✗ Error: model.pkl not found. Please train the model first.")
        return None

def predict_risk(patient_data):
    """
    Make risk prediction for a patient
    
    Args:
        patient_data: Dictionary with patient health information
        
    Returns:
        Dictionary with prediction results
    """
    model = load_model()
    
    if model is None:
        return None
    
    # Preprocess input
    features = preprocess_input(patient_data)
    
    # Make prediction
    prediction = model.predict(features)[0]
    prediction_proba = model.predict_proba(features)[0]
    
    # Map prediction to risk level
    risk_levels = ['Low Risk', 'Moderate Risk', 'High Risk']
    risk_level = risk_levels[prediction]
    confidence = prediction_proba[prediction] * 100
    
    result = {
        'risk_level': risk_level,
        'confidence': round(confidence, 2),
        'probabilities': {
            'low': round(prediction_proba[0] * 100, 2),
            'moderate': round(prediction_proba[1] * 100, 2) if len(prediction_proba) > 1 else 0,
            'high': round(prediction_proba[2] * 100, 2) if len(prediction_proba) > 2 else 0
        }
    }
    
    return result

# Test the predictor
if __name__ == '__main__':
    # Sample patient data
    test_patient = {
        'age': 55,
        'height': 175,
        'weight': 85,
        'gender': '1',  # Male
        'systolic_bp': 145,
        'diastolic_bp': 95,
        'cholesterol': 240,
        'glucose': 130,
        'postprandial_glucose': 180,
        'hba1c': 6.8,
        'family_history': '1',
        'exercise_hours': 1,
        'serum_creatinine': 1.4,
        'gfr': 55,
        'blood_urea_nitrogen': 28,
        'urine_albumin': 40,
        'serum_potassium': 4.5,
        'hemoglobin': 13.5
    }
    
    print("Testing predictor with sample data...")
    result = predict_risk(test_patient)
    
    if result:
        print(f"\n🔍 Prediction Results:")
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  Confidence: {result['confidence']}%")
        print(f"\n📊 Probabilities:")
        print(f"  Low Risk: {result['probabilities']['low']}%")
        print(f"  Moderate Risk: {result['probabilities']['moderate']}%")
        print(f"  High Risk: {result['probabilities']['high']}%")