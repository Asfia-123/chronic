import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np 
from groq import Groq
from preprocess import preprocess_input
from dotenv import load_dotenv
import mysql.connector
import logging
from datetime import datetime
import json
import traceback 

import warnings
# This line tells Python to ignore the UserWarning from scikit-learn
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Secure API Key Configuration ---
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    logger.error("✗ CRITICAL: GROQ_API_KEY not found in .env file. AI analysis will NOT work.")
else:
    logger.info("✓ Groq API key configured.")

# --- (Rule-based helper functions: get_ckd_stage, generate_health_summary) ---
def get_ckd_stage(gfr):
    if not gfr or gfr == 0: return 'Unknown'
    if gfr >= 90: return 'Stage 1 (Normal)'
    elif gfr >= 60: return 'Stage 2 (Mild)'
    elif gfr >= 30: return 'Stage 3 (Moderate)'
    elif gfr >= 15: return 'Stage 4 (Severe)'
    else: return 'Stage 5 (Kidney Failure)'

def generate_health_summary(data):
    return f"Patient {data.get('name', 'Unknown')} ({data.get('age', '?')} years), BMI: {data.get('bmi', '?')}, BP: {data.get('systolic_bp', '?')}/{data.get('diastolic_bp', '?')}"
# --- (End of helper functions) ---


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# --- AiAnalyzer Class ---
class AiAnalyzer:
    """
    AI analyzer using Groq for generating RECOMMENDATIONS.
    """
    def __init__(self):
        """Initialize the Groq client."""
        self.groq_client = None 
        if GROQ_API_KEY: 
            try:
                self.groq_client = Groq(api_key=GROQ_API_KEY)
                logger.info("✓ Groq client initialized successfully")
            except Exception as e:
                logger.error(f"✗ Error initializing Groq client: {e}")
                self.groq_client = None

    def get_ai_recommendations(self, data, risk_level, risk_percentage):
        """
        Generates health recommendations using Groq based on ML model's prediction.
        """
        if not self.groq_client:
            logger.error("✗ AI Model not available. Cannot generate recommendations.")
            raise Exception("AI Model is not configured. Check API key.")
            
        try:
            patient_summary = (
                f"Patient Data: Age: {data.get('age')}, Gender: {data.get('gender')}, "
                f"BMI: {data.get('bmi')}, BP: {data.get('systolic_bp')}/{data.get('diastolic_bp')}, "
                f"Cholesterol: {data.get('cholesterol')}, Glucose: {data.get('glucose')}, "
                f"Smoking: {data.get('smoking')}, Family History: {data.get('family_history')}, "
                f"Exercise Hours/Week: {data.get('exercise_hours')}"
            )

            prompt = f"""
            You are an expert medical AI analyst.
            A machine learning model has analyzed a patient and determined the following:
            - Predicted Risk Level: {risk_level}
            - Risk Confidence: {risk_percentage:.2f}%
            
            Patient Data:
            {patient_summary}
            

            Your Task:
            Generate a JSON object with seven (7) specific keys:
            1. risk_assessment: (String) A concise, empathetic summary (2-3 sentences) explaining what the {risk_level} risk means, based on the patient data.
            2. identified_risk_factors: (Array of strings) A list of the key risk factors you identify from the data (e.g., ["High Blood Pressure", "Smoking"]).
            3. diet_recommendations: (String) Actionable advice on diet.
            4. exercise_recommendations: (String) Specific guidance on physical activity.
            5. lifestyle_recommendations: (String) Advice on other factors like smoking, stress, sleep.
            6. follow_up_advice: (String) Recommendations for monitoring or consulting a healthcare provider.
            7. mental_health_advice: (String) Advice on stress, sleep, or mental well-being.
            
            Rules:
            - Do not add any text before or after the JSON object.
            - Ensure the output is a single, valid JSON object.
            - Output only valid JSON, no markdown formatting.
            """

            logger.info("Sending prompt to Groq API for recommendations...")
            
            # Make API call to Groq
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical AI assistant that provides health recommendations in JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",  # You can also use: "mixtral-8x7b-32768", "llama-3.1-70b-versatile"
                temperature=0.7,
                max_tokens=2048,
                top_p=1,
                stream=False
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            # Clean the response text
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            logger.info(f"Cleaned response text: {response_text}")
            
            try:
                ai_response_dict = json.loads(response_text)
                logger.info("✓ Groq recommendations generated successfully.")
                return ai_response_dict
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON Parsing Error: {json_err}")
                logger.error(f"Raw response: {response_text}")
                raise Exception(f"Failed to parse AI response as JSON.")

        except Exception as e:
            logger.error(f"✗ Error during Groq API call: {e}")
            logger.error(traceback.format_exc())
            raise Exception(f"AI recommendation generation failed. Error: {str(e)}")

    def analyze_risk_factors(self, data):
        """
        (This function is unchanged, used for DB logging)
        """
        factors = []
        try:
            sbp = float(data.get('systolic_bp', 0) or 0)
            dbp = float(data.get('diastolic_bp', 0) or 0)
            chol = float(data.get('cholesterol', 0) or 0)
            glucose = float(data.get('glucose', 0) or 0)
            gfr = float(data.get('gfr', 0) or 0)
            bmi = float(data.get('bmi', 0) or 0)
            exercise = float(data.get('exercise_hours', 0) or 0)
            fam = str(data.get('family_history', '0') or '0')
            smoking = str(data.get('smoking', '0') or '0')
        except Exception:
            sbp = dbp = chol = glucose = gfr = bmi = exercise = 0
            fam = '0'
            smoking = '0'
        
        if sbp >= 140 or dbp >= 90: factors.append({'factor': 'High Blood Pressure', 'severity': 'high', 'score': 1.0, 'value': f'{sbp}/{dbp}', 'description': 'Elevated blood pressure', 'impact': 'Increases cardiovascular and renal risk'})
        if chol >= 240: factors.append({'factor': 'High Cholesterol', 'severity': 'high', 'score': 1.0, 'value': str(chol), 'description': 'High total cholesterol', 'impact': 'Increases cardiovascular risk'})
        if (glucose and glucose >= 126): factors.append({'factor': 'High Glucose', 'severity': 'high', 'score': 1.0, 'value': str(glucose), 'description': 'High blood glucose', 'impact': 'Increases risk of diabetes'})
        if gfr and gfr < 60: factors.append({'factor': 'Reduced GFR', 'severity': 'medium', 'score': 0.7, 'value': str(gfr), 'description': 'Reduced kidney function', 'impact': 'Indicates CKD stage on progression'})
        if bmi and bmi >= 30: factors.append({'factor': 'Obesity', 'severity': 'medium', 'score': 0.5, 'value': str(bmi), 'description': 'High BMI', 'impact': 'Increases metabolic and cardiovascular risk'})
        if exercise < 1: factors.append({'factor': 'Low Physical Activity', 'severity': 'low', 'score': 0.3, 'value': str(exercise), 'description': 'Insufficient exercise', 'impact': 'Lifestyle modification recommended'})
        if fam.lower() in ['1', 'yes', 'true', 'y']: factors.append({'factor': 'Family History', 'severity': 'medium', 'score': 0.4, 'value': str(fam), 'description': 'Positive family history', 'impact': 'Genetic predisposition'})
        if smoking.lower() in ['1', 'yes', 'true', 'y']: factors.append({'factor': 'Smoking', 'severity': 'high', 'score': 0.8, 'value': str(smoking), 'description': 'Patient is a smoker', 'impact': 'Significantly increases risk'})
        return factors
# --- END OF AiAnalyzer Class ---

# instantiate analyzer
ai_analyzer = AiAnalyzer()

# --- 
# --- MODIFICATION: Loading BOTH models ---
# --- 
ml_model_xgb = None
ml_model_gb = None

try:
    XGB_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model_xgb.pkl') 
    with open(XGB_MODEL_PATH, 'rb') as f:
        ml_model_xgb = pickle.load(f) 
    logger.info("✓ Trained ML model (model_xgb.pkl) loaded for prediction.")
except Exception as e:
    logger.error(f"✗ CRITICAL: Could not load 'model_xgb.pkl': {e}")

try:
    GB_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model_gb.pkl') 
    with open(GB_MODEL_PATH, 'rb') as f:
        ml_model_gb = pickle.load(f) 
    logger.info("✓ Trained ML model (model_gb.pkl) loaded for prediction.")
except Exception as e:
    logger.error(f"✗ WARNING: Could not load 'model_gb.pkl': {e}")
# --- END MODIFICATION ---

# --- (Database functions: get_db_connection, fetch_latest_patient, init_database) ---
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'ehr_db')

def get_db_connection():
    try:
        conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"✗ Database Connection Error: {err}")
        raise err

def fetch_latest_patient(user_id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if user_id:
        query = "SELECT * FROM patients WHERE user_id=%s ORDER BY id DESC LIMIT 1"
        cursor.execute(query, (user_id,))
    else:
        query = "SELECT * FROM patients ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
    rec = cursor.fetchone()
    cursor.close()
    conn.close()
    return rec

def init_database():
    """Initialize database tables if they don't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, age FLOAT NOT NULL,
                gender VARCHAR(20), contact VARCHAR(50), address VARCHAR(255), height FLOAT, weight FLOAT, bmi FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_name (name), INDEX idx_created_at (created_at)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disease_records (
                id INT AUTO_INCREMENT PRIMARY KEY, patient_id INT NOT NULL, disease_type VARCHAR(100),
                systolic_bp FLOAT, diastolic_bp FLOAT, glucose FLOAT, hba1c FLOAT, gfr FLOAT,
                serum_creatinine FLOAT, blood_urea_nitrogen FLOAT, urine_albumin FLOAT,
                cholesterol FLOAT, exercise_hours FLOAT, family_history VARCHAR(10),
                risk_level VARCHAR(50), probability FLOAT, prediction_text TEXT, ckd_stage VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                INDEX idx_patient_id (patient_id), INDEX idx_disease_type (disease_type), INDEX idx_created_at (created_at)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_factors (
                id INT AUTO_INCREMENT PRIMARY KEY, disease_record_id INT NOT NULL, factor_name VARCHAR(100),
                severity VARCHAR(20), score FLOAT, value VARCHAR(50), description TEXT, impact TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (disease_record_id) REFERENCES disease_records(id) ON DELETE CASCADE,
                INDEX idx_record_id (disease_record_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INT AUTO_INCREMENT PRIMARY KEY, disease_record_id INT NOT NULL, priority VARCHAR(20),
                category VARCHAR(50), action TEXT, reason TEXT, timeline VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (disease_record_id) REFERENCES disease_records(id) ON DELETE CASCADE,
                INDEX idx_record_id (disease_record_id)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("✓ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"✗ Error initializing database: {e}")
# --- END ---

with app.app_context():
    init_database()

@app.route('/')
def home():
    return render_template('index.html')

# --- MODIFIED validate_input_data ---
def validate_input_data(data):
    mapped = {}
    def safe_float(value, default=0.0):
        try:
            if value is None or value == '' or value == 'None': return default
            return float(value)
        except (ValueError, TypeError): return default
    
    # Patient info
    mapped['name'] = data.get('fullName', data.get('name', 'Unknown'))
    mapped['contact'] = data.get('contactNumber', data.get('contact', ''))
    mapped['age'] = safe_float(data.get('age', 0))
    gender_val = data.get('gender', '0') 
    mapped['gender'] = 'Male' if gender_val == '0' else 'Female'
    mapped['height'] = safe_float(data.get('height', 0))
    mapped['weight'] = safe_float(data.get('weight', 0))
    mapped['address'] = data.get('address', '')
    mapped['bmi'] = safe_float(data.get('bmi', 0))
    
    # Health data for ML Model
    mapped['systolic_bp'] = safe_float(data.get('systolic_bp', 0))
    mapped['diastolic_bp'] = safe_float(data.get('diastolic_bp', 0))
    mapped['cholesterol'] = safe_float(data.get('cholesterol', 0))
    mapped['glucose'] = safe_float(data.get('glucose', 0))
    mapped['exercise_hours'] = safe_float(data.get('exercise_hours', 0))
    
    # Handle '0' or '1' string values from form
    mapped['family_history'] = safe_float(data.get('family_history', 0))
    mapped['smoking'] = safe_float(data.get('smoking', 0)) 
    
    mapped['selectedDisease'] = data.get('selectedDisease', data.get('diseaseSelect', 'all'))
    
    # Other fields (for DB and helper functions)
    mapped['hba1c'] = safe_float(data.get('hba1c', 0))
    mapped['gfr'] = safe_float(data.get('gfr', 0))
    mapped['serum_creatinine'] = safe_float(data.get('serum_creatinine', 0))
    mapped['blood_urea_nitrogen'] = safe_float(data.get('blood_urea_nitrogen', 0))
    mapped['urine_albumin'] = safe_float(data.get('urine_albumin', 0))
    
    return mapped
# --- END MODIFICATION ---

# --- 
# --- MAJOR MODIFICATION: /predict route ---
# --- 
@app.route('/predict', methods=['POST'])
def predict():
    """HYBRID Prediction endpoint (ML Model + Groq AI)"""
    try:
        data = request.json
        logger.info(f"Received data for HYBRID analysis: {data}")
        validated_data = validate_input_data(data)
        
        # --- 1. ML Model Prediction ---
        if not ml_model_xgb or not ml_model_gb:
            logger.error("✗ One or more ML models are not loaded. Cannot make prediction.")
            raise Exception("ML Models are not loaded. Check server logs.")
            
        # Use preprocess_input to get the NumPy array
        preprocessed_data_array = preprocess_input(validated_data)
        
        # --- PREDICT WITH XGBOOST (PRIMARY) ---clear

        probabilities_xgb = ml_model_xgb.predict_proba(preprocessed_data_array)
        risk_class_index_xgb = int(ml_model_xgb.predict(preprocessed_data_array)[0])
        risk_probability_xgb = float(probabilities_xgb[0][risk_class_index_xgb] * 100.0)
        risk_level_xgb = "High" if risk_class_index_xgb == 1 else "Low"
        logger.info(f"✓ XGBoost Prediction: {risk_level_xgb} ({risk_probability_xgb:.2f}%)")
        
        # --- PREDICT WITH GRADIENT BOOSTING (FOR LOGGING) ---
        probabilities_gb = ml_model_gb.predict_proba(preprocessed_data_array)
        risk_class_index_gb = int(ml_model_gb.predict(preprocessed_data_array)[0])
        risk_probability_gb = round(probabilities_gb[0][risk_class_index_gb] * 100.0, 2)
        risk_level_gb = "High" if risk_class_index_gb == 1 else "Low"
        logger.info(f"✓ GradientBoosting Prediction: {risk_level_gb} ({risk_probability_gb:.2f}%)")

        # --- We will use the XGBoost result for the user ---
        risk_level = risk_level_xgb
        risk_probability = risk_probability_xgb
        
        # --- 2. AI Recommendation Generation ---
        ai_analysis_results = ai_analyzer.get_ai_recommendations(
            validated_data, risk_level, risk_probability
        )
        
        # --- 3. Process and Combine Results ---
        ai_risk_assessment = ai_analysis_results.get('risk_assessment', 'No assessment provided.')
        ai_risk_factors_list = ai_analysis_results.get('identified_risk_factors', [])
        
        risk_class_css = 'low-risk'
        if risk_level == 'High': risk_class_css = 'high-risk'
            
        ckd_stage = get_ckd_stage(int(validated_data.get('gfr', 0)))
        health_summary = generate_health_summary(validated_data)
        
        recommendations = []
        if ai_analysis_results.get('diet_recommendations'): recommendations.append(f"Diet: {ai_analysis_results['diet_recommendations']}")
        if ai_analysis_results.get('exercise_recommendations'): recommendations.append(f"Exercise: {ai_analysis_results['exercise_recommendations']}")
        if ai_analysis_results.get('lifestyle_recommendations'): recommendations.append(f"Lifestyle: {ai_analysis_results['lifestyle_recommendations']}")
        if ai_analysis_results.get('follow_up_advice'): recommendations.append(f"Follow-up: {ai_analysis_results['follow_up_advice']}")
        if ai_analysis_results.get('mental_health_advice'): recommendations.append(f"Mental Health: {ai_analysis_results['mental_health_advice']}")
        
        response = {
            'risk_level': risk_level,                 
            'probability': f"{risk_probability:.2f}",        
            'prediction': ai_risk_assessment,       
            'risk_summary': ai_risk_assessment,      
            'recommendations': recommendations,      
            'risk_class': risk_class_css,
            'risk_factors': [
                {'factor': f, 'severity': 'ai-detected', 'value': 'N/A', 'description': f, 'impact': 'AI-identified risk'}
                for f in ai_risk_factors_list
            ],
            'ckd_stage': ckd_stage,
            'selected_disease': validated_data.get('selectedDisease', 'all'),
            'health_summary': health_summary,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # --- 4. Database Saving ---
        db_risk_factors = ai_analyzer.analyze_risk_factors(validated_data) 
        
        db_save_data = response.copy()
        db_save_data['risk_factors'] = db_risk_factors
        db_save_data['prediction'] = ai_risk_assessment
        
        db_validated_data = validated_data.copy()
        db_validated_data['family_history'] = 'Yes' if validated_data['family_history'] == 1.0 else 'No'
        
        patient_id = save_complete_patient_data(db_validated_data, db_save_data)
        response['patient_id'] = patient_id
        
        logger.info(f"HYBRID Prediction completed: {risk_level} ({risk_probability}%) - Patient ID: {patient_id}")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"---! ERROR IN /predict !---: {str(e)}")
        logger.error(traceback.format_exc()) 
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'trace': traceback.format_exc()
        }), 500
# --- END MODIFICATION ---


# --- (Database save function: save_complete_patient_data) ---
def save_complete_patient_data(data, prediction):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        patient_name = data.get('name', 'Unknown Patient')
        patient_age = data.get('age', 30)
        patient_gender = data.get('gender', 'Unknown')
        patient_contact = data.get('contact', '')
        patient_address = data.get('address', '')
        
        cursor.execute("""
            SELECT id FROM patients WHERE name = %s AND age = %s ORDER BY created_at DESC LIMIT 1
        """, (patient_name, patient_age))
        
        existing_patient = cursor.fetchone()
        
        if existing_patient:
            patient_id = existing_patient[0]
            cursor.execute("""
                UPDATE patients SET gender = %s, contact = %s, address = %s,
                    height = %s, weight = %s, bmi = %s, updated_at = NOW()
                WHERE id = %s
            """, (patient_gender, patient_contact, patient_address,
                    data.get('height'), data.get('weight'), data.get('bmi', 0), patient_id))
        else:
            cursor.execute("""
                INSERT INTO patients (
                    name, age, gender, contact, address,
                    height, weight, bmi, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                patient_name, patient_age, patient_gender,
                patient_contact, patient_address,
                data.get('height'), data.get('weight'), data.get('bmi', 0)
            ))
            patient_id = cursor.lastrowid
            
        disease_type = data.get('selectedDisease', 'all')
        
        cursor.execute("""
            INSERT INTO disease_records (
                patient_id, disease_type, systolic_bp, diastolic_bp,
                glucose, hba1c, gfr, serum_creatinine,
                blood_urea_nitrogen, urine_albumin, cholesterol,
                exercise_hours, family_history,
                risk_level, probability, prediction_text,
                ckd_stage, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, NOW()
            )
        """, (
            patient_id, disease_type,
            data.get('systolic_bp'), data.get('diastolic_bp'),
            data.get('glucose'), data.get('hba1c'), data.get('gfr'),
            data.get('serum_creatinine'), data.get('blood_urea_nitrogen'),
            data.get('urine_albumin'), data.get('cholesterol'),
            data.get('exercise_hours'), data.get('family_history'),
            prediction.get('risk_level'),
            prediction.get('probability'),
            prediction.get('prediction'),
            prediction.get('ckd_stage')
        ))
        
        disease_record_id = cursor.lastrowid
        
        for factor in prediction.get('risk_factors', []):
            if 'factor_name' not in factor and 'factor' in factor:
                cursor.execute("""
                    INSERT INTO risk_factors (
                        disease_record_id, factor_name, severity, value, description, impact
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    disease_record_id,
                    factor.get('factor'),
                    factor.get('severity'),
                    factor.get('value'),
                    factor.get('description'),
                    factor.get('impact')
                ))
            elif 'factor_name' in factor:
                cursor.execute("""
                    INSERT INTO risk_factors (
                        disease_record_id, factor_name, severity,
                        score, value, description, impact
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    disease_record_id,
                    factor.get('factor_name'),
                    factor.get('severity'),
                    factor.get('score'),
                    factor.get('value'),
                    factor.get('description'),
                    factor.get('impact')
                ))
                
        for recommendation in prediction.get('recommendations', []):
            if isinstance(recommendation, str):
                category = "general"
                if recommendation.lower().startswith('diet:'): category = 'diet'
                elif recommendation.lower().startswith('exercise:'): category = 'exercise'
                elif recommendation.lower().startswith('lifestyle:'): category = 'lifestyle'
                elif recommendation.lower().startswith('follow-up:'): category = 'follow_up'
                
                cursor.execute("""
                    INSERT INTO recommendations (
                        disease_record_id, priority, category, action, reason, timeline
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    disease_record_id,
                    'medium',
                    category,
                    recommendation,
                    'AI-generated recommendation',
                    'immediate'
                ))
                
        conn.commit()
        return patient_id
    
    except Exception as db_err:
        logger.error(f"✗ Database save error: {db_err}")
        if conn: conn.rollback()
        raise db_err
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
# --- (End of database save function) ---


# --- (GET routes: /patient/<id>, /patients) ---
def json_safe_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

@app.route('/patient/<int:patient_id>', methods=['GET'])
def get_patient_details(patient_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
            
        cursor.execute("""
            SELECT * FROM disease_records WHERE patient_id = %s ORDER BY created_at DESC
        """, (patient_id,))
        
        disease_records = cursor.fetchall()
        
        for record in disease_records:
            record_id = record['id']
            cursor.execute("SELECT * FROM risk_factors WHERE disease_record_id = %s", (record_id,))
            record['risk_factors'] = cursor.fetchall()
            cursor.execute("SELECT * FROM recommendations WHERE disease_record_id = %s", (record_id,))
            record['recommendations'] = cursor.fetchall()
            
        patient['disease_records'] = disease_records
        
        safe_json_string = json.dumps(patient, default=json_safe_converter)
        return app.response_class(response=safe_json_string, status=200, mimetype='application/json')
        
    except Exception as e:
        logger.error(f"Error retrieving patient details: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/patients', methods=['GET'])
def get_all_patients():
    """Get all patients with their latest disease record"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.*, 
                   dr.risk_level, 
                   dr.probability, 
                   dr.disease_type,
                   dr.created_at as last_checkup
            FROM patients p
            LEFT JOIN disease_records dr ON p.id = dr.patient_id
            WHERE dr.id = (
                SELECT id FROM disease_records 
                WHERE patient_id = p.id 
                ORDER BY created_at DESC 
                LIMIT 1
            )
            ORDER BY p.created_at DESC
        """)
        
        patients = cursor.fetchall()
        
        safe_json_string = json.dumps(patients, default=json_safe_converter)
        return app.response_class(response=safe_json_string, status=200, mimetype='application/json')
        
    except Exception as e:
        logger.error(f"Error retrieving patients list: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/patient/<int:patient_id>/history', methods=['GET'])
def get_patient_history(patient_id):
    """Get patient's disease record history"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        cursor.execute("""
            SELECT dr.*, 
                   COUNT(DISTINCT rf.id) as risk_factor_count,
                   COUNT(DISTINCT r.id) as recommendation_count
            FROM disease_records dr
            LEFT JOIN risk_factors rf ON dr.id = rf.disease_record_id
            LEFT JOIN recommendations r ON dr.id = r.disease_record_id
            WHERE dr.patient_id = %s
            GROUP BY dr.id
            ORDER BY dr.created_at DESC
        """, (patient_id,))
        
        history = cursor.fetchall()
        
        response_data = {
            'patient': patient,
            'history': history
        }
        
        safe_json_string = json.dumps(response_data, default=json_safe_converter)
        return app.response_class(response=safe_json_string, status=200, mimetype='application/json')
        
    except Exception as e:
        logger.error(f"Error retrieving patient history: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get overall system statistics"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total patients
        cursor.execute("SELECT COUNT(*) as total FROM patients")
        total_patients = cursor.fetchone()['total']
        
        # Total assessments
        cursor.execute("SELECT COUNT(*) as total FROM disease_records")
        total_assessments = cursor.fetchone()['total']
        
        # High risk patients
        cursor.execute("""
            SELECT COUNT(DISTINCT patient_id) as total 
            FROM disease_records 
            WHERE risk_level = 'High'
        """)
        high_risk_patients = cursor.fetchone()['total']
        
        # Risk distribution
        cursor.execute("""
            SELECT risk_level, COUNT(*) as count 
            FROM disease_records 
            GROUP BY risk_level
        """)
        risk_distribution = cursor.fetchall()
        
        # Disease type distribution
        cursor.execute("""
            SELECT disease_type, COUNT(*) as count 
            FROM disease_records 
            GROUP BY disease_type
        """)
        disease_distribution = cursor.fetchall()
        
        # Recent assessments (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM disease_records 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        recent_assessments = cursor.fetchone()['total']
        
        statistics = {
            'total_patients': total_patients,
            'total_assessments': total_assessments,
            'high_risk_patients': high_risk_patients,
            'recent_assessments': recent_assessments,
            'risk_distribution': risk_distribution,
            'disease_distribution': disease_distribution
        }
        
        return jsonify(statistics)
        
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'ml_model_xgb': ml_model_xgb is not None,
            'ml_model_gb': ml_model_gb is not None,
            'ai_analyzer': ai_analyzer.groq_client is not None,
            'database': False
        }
    }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        health_status['services']['database'] = True
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status['services']['database'] = False
    
    all_services_healthy = all(health_status['services'].values())
    health_status['status'] = 'healthy' if all_services_healthy else 'degraded'
    
    status_code = 200 if all_services_healthy else 503
    return jsonify(health_status), status_code

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Run the application
if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Health Risk Prediction System")
    logger.info("=" * 60)
    logger.info(f"ML Model (XGBoost): {'✓ Loaded' if ml_model_xgb else '✗ Not loaded'}")
    logger.info(f"ML Model (GradientBoosting): {'✓ Loaded' if ml_model_gb else '✗ Not loaded'}")
    logger.info(f"AI Analyzer (Groq): {'✓ Configured' if ai_analyzer.groq_client else '✗ Not configured'}")
    logger.info(f"Database: {DB_NAME}@{DB_HOST}")
    logger.info("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)