# Save this file as preprocess.py
import numpy as np

def safe_float(value, default=0.0):
    """Safely convert a value to float."""
    try:
        if value in [None, '', 'null', 'None']:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Safely convert a value to int."""
    try:
        if value in [None, '', 'null', 'None']:
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default


def preprocess_input(data):
    """
    Preprocess user input data for the ML model prediction.
    'data' is the 'validated_data' dictionary from app.py.
    """
    
    # This is the feature order your model was trained on:
    feature_order = [
        'age', 
        'gender', 
        'bmi', 
        'systolic_bp', 
        'diastolic_bp', 
        'cholesterol', 
        'glucose', 
        'smoking',
        'family_history',
        'exercise_hours'
    ]
    
    # Extract features safely and convert them
    features = {
        'age': safe_float(data.get('age', 30)),
        
        # This is CRITICAL: Your model was trained on 0/1, not 'Male'/'Female'.
        'gender': 0.0 if data.get('gender', 'Male') == 'Male' else 1.0, 
        
        'bmi': safe_float(data.get('bmi', 25)),
        'systolic_bp': safe_float(data.get('systolic_bp', 120)),
        'diastolic_bp': safe_float(data.get('diastolic_bp', 80)),
        'cholesterol': safe_float(data.get('cholesterol', 200)),
        'glucose': safe_float(data.get('glucose', 100)),
        
        # This is also CRITICAL: Your model was trained on 0/1, not 'No'/'Yes'.
        'smoking': safe_float(data.get('smoking', 0)),
        'family_history': safe_float(data.get('family_history', 0)),
        
        'exercise_hours': safe_float(data.get('exercise_hours', 0))
    }

    # Convert to numpy array in the correct order
    try:
        feature_array = np.array([[features[key] for key in feature_order]])
    except KeyError as e:
        print(f"---! ERROR in preprocess_input !---")
        print(f"Missing key: {e}")
        print(f"Features dictionary: {features}")
        raise e
    
    print(f"Preprocessed features for ML model: {feature_array}")
    
    return feature_array