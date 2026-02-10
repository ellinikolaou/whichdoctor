"""
Flask REST API server for WhichDoctor.
Layer 2: Navigation - Routes requests to appropriate tools
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import sys

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from tools.analyze_symptoms import analyze_symptoms, analyze_symptoms_refined

# Load environment variables
load_dotenv()

# Initialize Flask app with static folder configuration
app = Flask(__name__,
            static_folder='.',
            static_url_path='')

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # In production, specify allowed origins
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Secret key for sessions
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')


def validate_input_payload(data: dict) -> tuple:
    """
    Validate input payload against schema.

    Args:
        data: Request JSON data

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for symptoms array
    if 'symptoms' not in data:
        return False, "Missing required field: 'symptoms'"

    symptoms = data['symptoms']

    if not isinstance(symptoms, list):
        return False, "'symptoms' must be an array"

    if len(symptoms) == 0:
        return False, "At least one symptom is required"

    # Validate each symptom
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

    # Validate refinement fields if present
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

        # Validate each answer
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


@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'WhichDoctor API',
        'version': '1.0.0'
    })


@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """
    Analyze symptoms and return specialist recommendations.
    
    Request Body:
        {
            "symptoms": [
                {
                    "description": "string (required, 10-500 chars)",
                    "duration": "string (optional)",
                    "severity": "string (optional)",
                    "frequency": "string (optional)"
                }
            ],
            "age_range": "string (optional)",
            "existing_conditions": ["string"] (optional),
            "medications": ["string"] (optional),
            "additional_context": "string (optional)"
        }
    
    Response:
        {
            "disclaimer": "string",
            "analysis": {...},
            "specialist_recommendations": [...],
            "educational_resources": [...],
            "next_steps": [...],
            "emergency_warning": "string | null"
        }
    """
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Get JSON data
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Invalid JSON payload'
            }), 400

        # Validate input
        is_valid, error_message = validate_input_payload(data)

        if not is_valid:
            return jsonify({
                'error': error_message
            }), 400

        # Route based on mode
        is_refinement = data.get('is_refinement', False)

        if is_refinement:
            # Refinement mode - analyze with follow-up context
            print(f"[DEBUG] Calling analyze_symptoms_refined with {len(data.get('followup_answers', []))} follow-up answers")
            result = analyze_symptoms_refined(
                data,
                data['initial_analysis'],
                data['followup_answers']
            )
            print(f"[DEBUG] analyze_symptoms_refined returned, is_refined: {result.get('is_refined')}")
        else:
            # Initial analysis mode
            print(f"[DEBUG] Calling analyze_symptoms with {len(data.get('symptoms', []))} symptoms")
            result = analyze_symptoms(data)
            print(f"[DEBUG] analyze_symptoms returned, has error: {'error' in result}")

        return jsonify(result), 200

    except Exception as e:
        print(f"Error in /api/analyze: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error. Please try again later.'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Get environment
    env = os.getenv('ENVIRONMENT', 'development')
    
    # Run server
    if env == 'development':
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    else:
        # Production settings
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False
        )
