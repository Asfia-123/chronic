import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import pandas as pd
from preprocess import preprocess_input
from dotenv import load_dotenv
import mysql.connector

# Load environment variables from .env
load_dotenv()

# MySQL connection settings from .env
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'ehr_db')

# Function to get a MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Load the trained model
try:
    model = pickle.load(open('model.pkl', 'rb'))
    print("✓ Model loaded successfully!")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    model = None

@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """AI Prediction endpoint"""
    try:
        # Get JSON data from request
        data = request.json
        print(f"Received data: {data}")
        
        # Validate input data before preprocessing
        validated_data = validate_input_data(data)
        
        # Preprocess the input data
        features = preprocess_input(validated_data)
        
        # Make prediction using AI model
        if model is None:
            raise Exception("Model not loaded")
        
        prediction_proba = model.predict_proba(features)[0]
        risk_probability = prediction_proba[1] * 100  # Probability of high risk
        
        # Determine risk level
        if risk_probability < 30:
            risk_level = "Low Risk"
            risk_class = "low-risk"
            prediction_text = "AI Analysis: Your health indicators suggest low risk for chronic diseases. Continue your healthy lifestyle practices."
        elif risk_probability < 60:
            risk_level = "Moderate Risk"
            risk_class = "moderate-risk"
            prediction_text = "AI Analysis: Moderate risk detected. Several health factors require attention. Lifestyle modifications can significantly reduce your risk."
        else:
            risk_level = "High Risk"
            risk_class = "high-risk"
            prediction_text = "AI Analysis: High risk identified. Multiple concerning factors detected. Immediate medical consultation is strongly recommended."
        
        # Generate AI-based recommendations
        recommendations = generate_ai_recommendations(validated_data, risk_probability)
        
        # Identify risk factors using AI
        risk_factors = identify_ai_risk_factors(validated_data, risk_probability)
        
        # Get CKD stage if kidney data available
        ckd_stage = get_ckd_stage(int(validated_data.get('gfr', 90)))
        
        # Prepare response
        response = {
            'risk_level': risk_level,
            'probability': round(risk_probability, 2),
            'prediction': prediction_text,
            'recommendations': recommendations,
            'risk_class': risk_class,
            'risk_factors': risk_factors,
            'ckd_stage': ckd_stage,
            'selected_disease': validated_data.get('selectedDisease', 'all')
        }

        # Save prediction to MySQL database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_predictions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    age FLOAT,
                    height FLOAT,
                    weight FLOAT,
                    systolic_bp FLOAT,
                    diastolic_bp FLOAT,
                    glucose FLOAT,
                    hba1c FLOAT,
                    gfr FLOAT,
                    serum_creatinine FLOAT,
                    blood_urea_nitrogen FLOAT,
                    urine_albumin FLOAT,
                    cholesterol FLOAT,
                    exercise_hours FLOAT,
                    family_history VARCHAR(10),
                    selected_disease VARCHAR(50),
                    gender VARCHAR(10),
                    risk_level VARCHAR(50),
                    probability FLOAT,
                    prediction TEXT,
                    recommendations TEXT,
                    risk_class VARCHAR(50),
                    risk_factors TEXT,
                    ckd_stage VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Insert prediction data
            cursor.execute("""
                INSERT INTO risk_predictions (
                    age, height, weight, systolic_bp, diastolic_bp, glucose, hba1c, gfr, serum_creatinine,
                    blood_urea_nitrogen, urine_albumin, cholesterol, exercise_hours, family_history,
                    selected_disease, gender, risk_level, probability, prediction, recommendations,
                    risk_class, risk_factors, ckd_stage
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                validated_data.get('age'),
                validated_data.get('height'),
                validated_data.get('weight'),
                validated_data.get('systolic_bp'),
                validated_data.get('diastolic_bp'),
                validated_data.get('glucose'),
                validated_data.get('hba1c'),
                validated_data.get('gfr'),
                validated_data.get('serum_creatinine'),
                validated_data.get('blood_urea_nitrogen'),
                validated_data.get('urine_albumin'),
                validated_data.get('cholesterol'),
                validated_data.get('exercise_hours'),
                validated_data.get('family_history'),
                validated_data.get('selectedDisease'),
                validated_data.get('gender'), 
                risk_level,
                round(risk_probability, 2),
                prediction_text,
                ', '.join(recommendations),
                risk_class,
                ', '.join(risk_factors),
                ckd_stage
            ))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as db_err:
            print(f"Database error: {db_err}")

        print(f"AI Prediction: {response}")
        return jsonify(response)
    
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

def validate_input_data(data):
    """Validate and clean input data before processing"""
    if not data:
        raise ValueError("No data received")
    
    validated_data = {}
    
    # Define expected numerical fields and their default values
    numerical_fields = {
        'age': 30,
        'height': 170,
        'weight': 70,
        'systolic_bp': 120,
        'diastolic_bp': 80,
        'glucose': 100,
        'hba1c': 5.5,
        'gfr': 90,
        'serum_creatinine': 1.0,
        'blood_urea_nitrogen': 15,
        'urine_albumin': 10,
        'cholesterol': 200,
        'exercise_hours': 0
    }
    
    # Validate numerical fields
    for field, default_value in numerical_fields.items():
        value = data.get(field)
        
        if value is None:
            validated_data[field] = default_value
            continue
            
        # Convert to string first to handle any type
        str_value = str(value).strip()
        
        # Remove common units and non-numeric characters
        str_value = str_value.replace('mg/dL', '').replace('mg/dl', '').replace('mg', '')
        str_value = str_value.replace('ng/mL', '').replace('ng/ml', '')
        str_value = str_value.replace('%', '').replace('mmHg', '').replace('OK', '')
        str_value = str_value.replace('–', '-').replace('−', '-')  # Different dash types
        str_value = str_value.split('-')[0].strip()  # Take first value if range like "0.5-2.0"
        
        # Handle empty strings after cleaning
        if not str_value:
            validated_data[field] = default_value
            continue
            
        try:
            # Convert to float
            validated_data[field] = float(str_value)
        except (ValueError, TypeError):
            print(f"Warning: Could not convert {field} value '{value}' to number, using default {default_value}")
            validated_data[field] = default_value
    
    # Handle categorical/string fields
    categorical_fields = ['family_history', 'selectedDisease', 'gender', ]
    for field in categorical_fields:
        validated_data[field] = data.get(field, '0')
    
    print(f"Validated data: {validated_data}")
    return validated_data

def generate_ai_recommendations(data, risk_prob):
    """Generate personalized recommendations based on AI prediction"""
    recommendations = []
    
    # Calculate BMI
    height_m = float(data.get('height', 170)) / 100
    weight = float(data.get('weight', 70))
    bmi = weight / (height_m ** 2)
    
    # Risk-based recommendations
    if risk_prob > 60:
        recommendations.append("🚨 Urgent: Schedule immediate consultation with your healthcare provider")
        recommendations.append("💊 Discuss medication options to manage your condition")
        recommendations.append("📊 Get comprehensive lab tests done within the next week")
    elif risk_prob > 30:
        recommendations.append("⚠️ Schedule a medical checkup within the next month")
        recommendations.append("📋 Monitor your vital signs regularly at home")
    else:
        recommendations.append("✅ Maintain your current healthy lifestyle")
        recommendations.append("📅 Continue annual health screenings")
    
    # Diabetes-specific recommendations
    glucose = float(data.get('glucose', 100))
    hba1c = float(data.get('hba1c', 5.5))
    
    if glucose > 126 or hba1c > 6.5:
        recommendations.append("🍬 Strict blood sugar control: Avoid refined sugars and carbohydrates")
        recommendations.append("💉 Consider continuous glucose monitoring")
        recommendations.append("🥗 Follow a low-glycemic index diet")
    elif glucose > 100 or hba1c > 5.7:
        recommendations.append("🍎 Reduce sugar intake and increase fiber consumption")
        recommendations.append("🏃 Regular exercise to improve insulin sensitivity")
    
    # Kidney-specific recommendations
    gfr = float(data.get('gfr', 90))
    creatinine = float(data.get('serum_creatinine', 1.0))
    
    if gfr < 60:
        recommendations.append("🫘 Consult nephrologist for kidney function management")
        recommendations.append("🧂 Limit sodium intake (less than 2000mg daily)")
        recommendations.append("🥩 Monitor protein intake based on kidney function")
        recommendations.append("💧 Stay hydrated but monitor fluid intake")
    
    if creatinine > 1.3:
        recommendations.append("⚠️ Elevated creatinine: Avoid nephrotoxic medications (NSAIDs)")
    
    # Blood pressure recommendations
    systolic = float(data.get('systolic_bp', 120))
    diastolic = float(data.get('diastolic_bp', 80))
    
    if systolic > 140 or diastolic > 90:
        recommendations.append("💓 Blood pressure control critical: Reduce salt, manage stress")
        recommendations.append("🏥 Monitor blood pressure daily")
    elif systolic > 130 or diastolic > 80:
        recommendations.append("🫀 Monitor blood pressure regularly")
    
    # BMI recommendations
    if bmi > 30:
        recommendations.append("⚖️ Weight loss program recommended (BMI > 30)")
        recommendations.append("🏋️ Combine cardio and strength training exercises")
    elif bmi > 25:
        recommendations.append("🚶 Increase physical activity to achieve healthy weight")
    
    # Exercise recommendations
    exercise_hours = float(data.get('exercise_hours', 0))
    if exercise_hours < 2.5:
        recommendations.append("🏃‍♂️ Aim for at least 150 minutes of moderate exercise weekly")
    
    # Cholesterol recommendations
    cholesterol = float(data.get('cholesterol', 200))
    if cholesterol > 240:
        recommendations.append("🥑 High cholesterol: Reduce saturated fats, increase omega-3")
    elif cholesterol > 200:
        recommendations.append("🥗 Consider heart-healthy Mediterranean diet")
    
    # Family history
    if data.get('family_history') == '1':
        recommendations.append("👨‍👩‍👧 Family history present: More frequent health monitoring needed")
    
    return recommendations

def identify_ai_risk_factors(data, risk_prob):
    """Identify risk factors using AI analysis"""
    risk_factors = []
    
    # Calculate BMI
    height_m = float(data.get('height', 170)) / 100
    weight = float(data.get('weight', 70))
    bmi = weight / (height_m ** 2)
    
    # BMI risk factors
    if bmi > 30:
        risk_factors.append(f"Obesity detected (BMI: {bmi:.1f})")
    elif bmi > 25:
        risk_factors.append(f"Overweight (BMI: {bmi:.1f})")
    
    # Age risk factor
    age = float(data.get('age', 30))
    if age > 65:
        risk_factors.append(f"Advanced age ({age} years)")
    elif age > 45:
        risk_factors.append(f"Middle age risk factor ({age} years)")
    
    # Blood pressure
    systolic = float(data.get('systolic_bp', 120))
    diastolic = float(data.get('diastolic_bp', 80))
    if systolic > 140 or diastolic > 90:
        risk_factors.append(f"Hypertension (BP: {systolic}/{diastolic})")
    elif systolic > 130 or diastolic > 80:
        risk_factors.append(f"Elevated blood pressure ({systolic}/{diastolic})")
    
    # Glucose levels
    glucose = float(data.get('glucose', 100))
    if glucose > 126:
        risk_factors.append(f"Diabetes range glucose ({glucose} mg/dL)")
    elif glucose > 100:
        risk_factors.append(f"Pre-diabetic glucose levels ({glucose} mg/dL)")
    
    # HbA1c
    hba1c = float(data.get('hba1c', 5.5))
    if hba1c > 6.5:
        risk_factors.append(f"Diabetic HbA1c levels ({hba1c}%)")
    elif hba1c > 5.7:
        risk_factors.append(f"Pre-diabetic HbA1c ({hba1c}%)")
    
    # Kidney function
    gfr = float(data.get('gfr', 90))
    if gfr < 60:
        risk_factors.append(f"Reduced kidney function (GFR: {gfr})")
    
    creatinine = float(data.get('serum_creatinine', 1.0))
    if creatinine > 1.3:
        risk_factors.append(f"Elevated serum creatinine ({creatinine} mg/dL)")
    
    bun = float(data.get('blood_urea_nitrogen', 15))
    if bun > 25:
        risk_factors.append(f"High blood urea nitrogen ({bun} mg/dL)")
    
    urine_albumin = float(data.get('urine_albumin', 10))
    if urine_albumin > 30:
        risk_factors.append(f"Significant albuminuria ({urine_albumin} mg/g)")
    
    # Cholesterol
    cholesterol = float(data.get('cholesterol', 200))
    if cholesterol > 240:
        risk_factors.append(f"High cholesterol ({cholesterol} mg/dL)")
    elif cholesterol > 200:
        risk_factors.append(f"Borderline high cholesterol ({cholesterol} mg/dL)")
    
    # Lifestyle factors
    exercise = float(data.get('exercise_hours', 0))
    if exercise < 2.5:
        risk_factors.append("Sedentary lifestyle (insufficient exercise)")
    
    # Family history
    if data.get('family_history') == '1':
        risk_factors.append("Family history of chronic disease")
    
    return risk_factors

def get_ckd_stage(gfr):
    """Determine CKD stage based on GFR"""
    if gfr >= 90:
        return 'Stage 1 (Normal kidney function)'
    elif gfr >= 60:
        return 'Stage 2 (Mild kidney damage)'
    elif gfr >= 45:
        return 'Stage 3a (Mild to moderate kidney damage)'
    elif gfr >= 30:
        return 'Stage 3b (Moderate to severe kidney damage)'
    elif gfr >= 15:
        return 'Stage 4 (Severe kidney damage)'
    else:
        return 'Stage 5 (Kidney failure)'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)