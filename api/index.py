"""
Vercel serverless function for WhichDoctor API.
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add project root to path so we can import tools
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.analyze_symptoms import analyze_symptoms, analyze_symptoms_refined

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')


def validate_input_payload(data: dict) -> tuple:
    """Validate input payload against schema."""
    if 'symptoms' not in data:
        return False, "Missing required field: 'symptoms'"

    symptoms = data['symptoms']

    if not isinstance(symptoms, list):
        return False, "'symptoms' must be an array"

    if len(symptoms) == 0:
        return False, "At least one symptom is required"

    for i, symptom in enumerate(symptoms):
        if not isinstance(symptom, dict):
            return False, f"Symptom {i+1} must be an object"

        if 'description' not in symptom:
            return False, f"Symptom {i+1} missing required field: 'description'"

        description = symptom['description']

        if not isinstance(description, str):
            return False, f"Symptom {i+1} description must be a string"

        if len(description) < 10:
            return False, f"Symptom {i+1} description too short (minimum 10 characters)"

        if len(description) > 500:
            return False, f"Symptom {i+1} description too long (maximum 500 characters)"

    if data.get('is_refinement', False):
        if 'initial_analysis' not in data:
            return False, "Refinement mode requires 'initial_analysis' field"

        if 'followup_answers' not in data:
            return False, "Refinement mode requires 'followup_answers' field"

        followup_answers = data['followup_answers']

        if not isinstance(followup_answers, list):
            return False, "'followup_answers' must be an array"

        if len(followup_answers) == 0:
            return False, "At least one follow-up answer is required for refinement"

        for i, answer in enumerate(followup_answers):
            if not isinstance(answer, dict):
                return False, f"Follow-up answer {i+1} must be an object"

            if 'question_id' not in answer or 'answer' not in answer:
                return False, f"Follow-up answer {i+1} must have 'question_id' and 'answer' fields"

            if not isinstance(answer['answer'], str):
                return False, f"Follow-up answer {i+1} 'answer' must be a string"

            if len(answer['answer']) < 1:
                return False, f"Follow-up answer {i+1} cannot be empty"

    return True, None


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'WhichDoctor API',
        'version': '1.0.0'
    })


@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """Analyze symptoms and return specialist recommendations."""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        is_valid, error_message = validate_input_payload(data)

        if not is_valid:
            return jsonify({'error': error_message}), 400

        is_refinement = data.get('is_refinement', False)

        if is_refinement:
            result = analyze_symptoms_refined(
                data,
                data['initial_analysis'],
                data['followup_answers']
            )
        else:
            result = analyze_symptoms(data)

        return jsonify(result), 200

    except Exception as e:
        print(f"Error in /api/analyze: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error. Please try again later.'
        }), 500
