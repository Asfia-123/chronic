import numpy as np
import pandas as pd

def preprocess_input(data):
    """
    Preprocess user input data for AI model prediction
    
    Args:
        data: Dictionary containing patient health data
        
    Returns:
        numpy array: Preprocessed features ready for model prediction
    """
    
    # Calculate BMI
    height_m = float(data.get('height', 170)) / 100  # Convert cm to meters
    weight = float(data.get('weight', 70))
    bmi = weight / (height_m ** 2)
    
    # Extract and convert all features
    features = {
        'age': int(data.get('age', 30)),
        'bmi': bmi,
        'systolic_bp': int(data.get('systolic_bp', 120)),
        'diastolic_bp': int(data.get('diastolic_bp', 80)),
        'cholesterol': int(data.get('cholesterol', 200)),
        'glucose': int(data.get('glucose', 100)),
        'postprandial_glucose': int(data.get('postprandial_glucose', 120)),
        'hba1c': float(data.get('hba1c', 5.5)),
        'family_history': int(data.get('family_history', 0)),
        'exercise_hours': float(data.get('exercise_hours', 0)),
        'serum_creatinine': float(data.get('serum_creatinine', 1.0)),
        'gfr': int(data.get('gfr', 90)),
        'blood_urea_nitrogen': int(data.get('blood_urea_nitrogen', 15)),
        'urine_albumin': int(data.get('urine_albumin', 10)),
        'serum_potassium': float(data.get('serum_potassium', 4.0)),
        'hemoglobin': float(data.get('hemoglobin', 14.0)),
        'gender': 1 if data.get('gender', '1') == '1' else 0  # 1 for Male, 0 for Female
    }
    
    # Create feature array in correct order (must match training data)
    feature_order = [
        'age', 'bmi', 'systolic_bp', 'diastolic_bp', 'cholesterol',
        'glucose', 'postprandial_glucose', 'hba1c', 'family_history',
        'exercise_hours', 'serum_creatinine', 'gfr', 'blood_urea_nitrogen',
        'urine_albumin', 'serum_potassium', 'hemoglobin', 'gender'
    ]
    
    feature_array = np.array([[features[key] for key in feature_order]])
    
    print(f"Preprocessed features: {feature_array}")
    
    return feature_array

def validate_input(data):
    """
    Validate input data ranges
    
    Returns:
        tuple: (is_valid, error_message)
    """
    validations = {
        'age': (1, 120, 'Age'),
        'height': (50, 250, 'Height'),
        'weight': (20, 300, 'Weight'),
        'systolic_bp': (70, 250, 'Systolic BP'),
        'diastolic_bp': (40, 150, 'Diastolic BP'),
        'cholesterol': (100, 400, 'Cholesterol'),
        'glucose': (50, 300, 'Glucose'),
    }
    
    for field, (min_val, max_val, name) in validations.items():
        if field in data:
            value = float(data[field])
            if value < min_val or value > max_val:
                return False, f"{name} must be between {min_val} and {max_val}"
    
    return True, "Valid"