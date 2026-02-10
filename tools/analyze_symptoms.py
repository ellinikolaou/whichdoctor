"""
Core symptom analysis engine for WhichDoctor.
Layer 3: Tools - Deterministic Python script

Follows: architecture/symptom_analysis_sop.md
"""

import os
import json
import time
from typing import Dict, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Model configuration
MODEL_NAME = 'gemini-2.5-flash'
GENERATION_CONFIG = {
    'temperature': 0.3,  # Lower for medical consistency
    'max_output_tokens': 4096,  # Increased to prevent truncation
}

# Emergency symptom keywords (case-insensitive)
EMERGENCY_KEYWORDS = [
    'chest pain', 'chest pressure', 'heart attack',
    'difficulty breathing', 'can\'t breathe', 'shortness of breath',
    'severe headache', 'worst headache',
    'severe bleeding', 'bleeding won\'t stop',
    'loss of consciousness', 'passed out', 'fainted',
    'confusion', 'disoriented', 'altered mental',
    'stroke', 'face drooping', 'arm weakness', 'speech difficulty',
    'severe allergic', 'anaphylaxis', 'throat swelling',
    'suicidal', 'self-harm', 'want to die',
    'severe abdominal pain', 'severe stomach pain',
    'coughing blood', 'coughing up blood',
    'seizure', 'convulsion',
    'severe burn',
    'poisoning', 'overdose',
]

# Legal disclaimer
DISCLAIMER = """⚠️ MEDICAL DISCLAIMER
This tool provides educational information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of something you have read on this site.

If you think you may have a medical emergency, call 911 or go to the nearest emergency room immediately."""


def detect_emergency_symptoms(symptoms: List[Dict]) -> bool:
    """
    Detect if any symptoms indicate a medical emergency.
    
    Args:
        symptoms: List of symptom dictionaries with 'description' field
        
    Returns:
        True if emergency detected, False otherwise
    """
    for symptom in symptoms:
        description = symptom.get('description', '').lower()
        for keyword in EMERGENCY_KEYWORDS:
            if keyword in description:
                return True
    return False


def build_gemini_prompt(input_payload: Dict) -> str:
    """
    Build structured prompt for Gemini API.
    
    Args:
        input_payload: Validated input payload with symptoms
        
    Returns:
        Formatted prompt string
    """
    symptoms = input_payload.get('symptoms', [])
    age_range = input_payload.get('age_range', 'Not provided')
    existing_conditions = input_payload.get('existing_conditions', [])
    medications = input_payload.get('medications', [])
    additional_context = input_payload.get('additional_context', '')
    
    # Format symptoms
    symptom_list = []
    for i, symptom in enumerate(symptoms, 1):
        desc = symptom.get('description', '')
        duration = symptom.get('duration', 'Not specified')
        severity = symptom.get('severity', 'Not specified')
        frequency = symptom.get('frequency', 'Not specified')
        
        symptom_list.append(f"""
Symptom {i}:
- Description: {desc}
- Duration: {duration}
- Severity: {severity}
- Frequency: {frequency}
""")
    
    prompt = f"""You are a medical navigation advisor helping users find the right specialist.

CRITICAL RULES:
- Never diagnose conditions
- Never provide medical advice or treatment recommendations
- Only suggest appropriate specialist types who can address interconnected issues
- Use advisory language: "may indicate", "consider", "could be related to"
- Never use diagnostic language: "you have", "diagnosed with", "you need"
- Provide 1-3 specialist recommendations maximum
- DO NOT recommend "Primary Care Physician" - they often don't know which specialist to refer to
- ONLY recommend specific specialists who have expertise in the interconnected patterns you identify
- Include educational context from credible sources

HOLISTIC ANALYSIS FRAMEWORK:
You are analyzing symptoms from a systems medicine perspective. The human body is an interconnected system where issues in one area can manifest as symptoms in seemingly unrelated areas.

When analyzing symptoms, actively look for:
- Cross-system connections (e.g., hormonal issues affecting multiple body systems)
- Cascade effects (e.g., nutritional deficiencies causing widespread symptoms)
- Bidirectional relationships (e.g., gut-brain axis, immune-endocrine interactions)
- Root cause patterns that explain multiple symptoms together

Common holistic patterns to consider:
- Endocrine/Hormonal: Thyroid, adrenal, reproductive hormones affecting energy, weight, mood, temperature, digestion
- Autoimmune: Inflammation affecting multiple organ systems simultaneously
- Nutritional: Vitamin/mineral deficiencies causing diverse symptoms (fatigue, neurological, skin, immune)
- Metabolic: Blood sugar dysregulation, insulin resistance affecting multiple systems
- Inflammatory: Chronic inflammation manifesting in various body systems
- Gut-related: Microbiome imbalances affecting digestion, mood, immunity, skin
- Stress/HPA axis: Chronic stress affecting hormones, immunity, digestion, sleep

EXAMPLES OF HOLISTIC CONNECTIONS:
- Fatigue + weight gain + cold sensitivity + constipation → May indicate thyroid dysfunction affecting metabolism across multiple systems
- Joint pain + fatigue + brain fog + digestive issues → Could suggest autoimmune process or systemic inflammation
- Fatigue + tingling + mood changes + pale skin → Might point to B12 deficiency affecting nervous, blood, and energy systems
- Headaches + fatigue + digestive issues + anxiety → Consider gut-brain axis involvement

When you identify such patterns, explain the interconnections and recommend specialists who treat the ROOT system, not just individual symptoms.

USER INFORMATION:
Age Range: {age_range}
Existing Conditions: {', '.join(existing_conditions) if existing_conditions else 'None reported'}
Current Medications: {', '.join(medications) if medications else 'None reported'}
Additional Context: {additional_context if additional_context else 'None provided'}

SYMPTOMS:
{''.join(symptom_list)}

TASK:
Analyze these symptoms and provide a JSON response with the following structure:

{{
  "analysis": {{
    "symptom_clusters": [
      {{
        "symptoms": ["symptom1", "symptom2"],
        "possible_connections": "Educational explanation emphasizing HOW and WHY these symptoms connect across body systems",
        "system_involvement": "Which body systems are involved (e.g., 'Endocrine and Metabolic', 'Immune and Digestive')"
      }}
    ],
    "potential_root_causes": [
      {{
        "category": "Specific medical category (e.g., 'Endocrine - Thyroid', 'Autoimmune - Systemic', 'Nutritional - B12 Deficiency')",
        "description": "Educational explanation of how this root cause creates a cascade of symptoms across body systems",
        "related_symptoms": ["symptom1", "symptom2"],
        "confidence": "possible|likely|consider",
        "systemic_explanation": "Brief explanation of the systemic/holistic connection"
      }}
    ]
  }},
  "specialist_recommendations": [
    {{
      "specialist_type": "Specific specialist type (e.g., 'Endocrinologist', 'Rheumatologist')",
      "reason": "Why this specialist is relevant to these symptoms",
      "priority": "primary|secondary|consider",
      "what_they_treat": "Brief explanation of what this specialist treats"
    }}
  ],
  "educational_resources": [
    {{
      "title": "Resource title",
      "source": "Credible source (e.g., 'NIH', 'Mayo Clinic', 'MedlinePlus')",
      "relevance": "Why this resource is helpful for these symptoms"
    }}
  ],
  "next_steps": [
    "Actionable advice like 'Schedule appointment with recommended specialist'",
    "Keep a symptom diary to share with your doctor"
  ]
}}

Provide ONLY the JSON response, no additional text."""
    
    return prompt


def generate_followup_questions_prompt(symptoms: List[Dict], initial_analysis: Dict) -> str:
    """
    Build prompt for generating follow-up questions.

    Args:
        symptoms: Original symptom list
        initial_analysis: The analysis result from initial query

    Returns:
        Formatted prompt string for question generation
    """
    # Format symptoms for context
    symptom_list = []
    for i, symptom in enumerate(symptoms, 1):
        desc = symptom.get('description', '')
        duration = symptom.get('duration', 'Not specified')
        severity = symptom.get('severity', 'Not specified')
        symptom_list.append(f"{i}. {desc} (Duration: {duration}, Severity: {severity})")

    # Extract key analysis points
    specialists = initial_analysis.get('specialist_recommendations', [])
    specialist_types = [s.get('specialist_type', '') for s in specialists[:3]]

    potential_causes = initial_analysis.get('analysis', {}).get('potential_root_causes', [])
    cause_categories = [c.get('category', '') for c in potential_causes[:3]]

    prompt = f"""You are a medical navigation advisor. Based on the initial symptom analysis, generate 3-5 specific follow-up questions that will help narrow down specialist recommendations.

INITIAL SYMPTOMS:
{'\\n'.join(symptom_list)}

INITIAL ANALYSIS:
Potential Root Causes: {', '.join(cause_categories) if cause_categories else 'Under evaluation'}
Specialist Recommendations: {', '.join(specialist_types) if specialist_types else 'To be determined'}

HOLISTIC ANALYSIS FOCUS:
Generate questions that help identify:
- Patterns across body systems
- Timeline of symptom development (what appeared first, what followed)
- Triggers and relieving factors (stress, diet, sleep, hormonal cycles)
- Related symptoms the user might not have connected (fatigue, digestion, mood, sleep, skin, temperature sensitivity)

TASK:
Generate 3-5 clarifying questions that will help:
1. Distinguish between similar conditions
2. Identify red flags or urgent symptoms
3. Understand symptom progression and patterns
4. Gather contextual information about triggers or alleviating factors

RULES:
- Questions must help identify root causes and systemic patterns
- Focus on symptoms, timing, patterns, triggers, diet, stress, sleep, hormonal factors
- Ask about seemingly unrelated symptoms that could reveal systemic connections
- Avoid asking for self-diagnosis
- Use plain language (no medical jargon)
- Each question should help narrow down the specialist recommendation by revealing systemic patterns
- Questions should be answerable with text or a simple selection

OUTPUT FORMAT (JSON only):
{{
  "questions": [
    {{
      "id": "q1",
      "question": "Clear, specific question text?",
      "type": "text",
      "context": "Brief explanation of why this question matters",
      "options": null
    }},
    {{
      "id": "q2",
      "question": "Question that needs a specific choice?",
      "type": "select",
      "context": "Why this helps",
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"]
    }}
  ]
}}

Generate 3-5 questions. Provide ONLY the JSON response, no additional text."""

    return prompt


def parse_followup_response(response_text: str) -> Dict:
    """
    Parse follow-up questions response (different structure than main analysis).

    Args:
        response_text: Raw response from Gemini API

    Returns:
        Parsed JSON dictionary with questions field
    """
    # Extract JSON from response (may have markdown code blocks)
    text = response_text.strip()

    # Remove markdown code blocks if present
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]

    if text.endswith('```'):
        text = text[:-3]

    text = text.strip()

    # Try to find JSON object boundaries
    start_idx = text.find('{')
    end_idx = text.rfind('}')

    if start_idx == -1 or end_idx == -1:
        raise ValueError("No JSON object found in response")

    json_text = text[start_idx:end_idx+1]

    try:
        data = json.loads(json_text)

        # Validate that questions field exists
        if 'questions' not in data:
            raise ValueError("Response missing 'questions' field")

        return data

    except json.JSONDecodeError as e:
        print(f"JSON parse error in follow-up questions: {str(e)}")
        raise ValueError(f"Failed to parse follow-up questions JSON: {str(e)}")


def extract_followup_questions(input_payload: Dict, initial_analysis: Dict) -> List[Dict]:
    """
    Generate follow-up questions using Gemini API.

    Args:
        input_payload: Original symptom payload
        initial_analysis: Initial analysis result

    Returns:
        List of question objects, or empty list on failure
    """
    try:
        symptoms = input_payload.get('symptoms', [])
        if not symptoms:
            return []

        # Generate question prompt
        prompt = generate_followup_questions_prompt(symptoms, initial_analysis)

        # Call Gemini API with retry logic for follow-up questions
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=GENERATION_CONFIG
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                if response and response.text:
                    # Parse using specialized parser for follow-up questions
                    questions_data = parse_followup_response(response.text)
                    questions = questions_data.get('questions', [])

                    # Validate questions (basic check)
                    if not isinstance(questions, list):
                        raise ValueError("Questions must be a list")

                    # Limit to 5 questions max
                    questions = questions[:5]

                    # Validate each question has required fields
                    valid_questions = []
                    for q in questions:
                        if all(k in q for k in ['id', 'question', 'type', 'context']):
                            valid_questions.append(q)

                    if len(valid_questions) > 0:
                        return valid_questions
                    else:
                        raise ValueError("No valid questions found")

            except Exception as e:
                print(f"Follow-up questions attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1 * (2 ** attempt))
                    continue
                else:
                    print(f"Failed to generate follow-up questions after {max_retries} attempts")
                    return []

        return []

    except Exception as e:
        print(f"Error generating follow-up questions: {str(e)}")
        # Graceful degradation: return empty list
        return []


def call_gemini_api(prompt: str, max_retries: int = 3) -> Optional[str]:
    """
    Call Gemini API with retry logic.

    Args:
        prompt: Formatted prompt string
        max_retries: Maximum number of retry attempts

    Returns:
        API response text or None if all retries fail
    """
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=GENERATION_CONFIG
    )

    base_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            if response and response.text:
                # Validate that response can be parsed as JSON before returning
                try:
                    parse_gemini_response(response.text)
                    return response.text
                except (json.JSONDecodeError, ValueError) as parse_error:
                    print(f"JSON parse error on attempt {attempt + 1}: {str(parse_error)}")
                    if attempt < max_retries - 1:
                        print(f"Retrying due to malformed JSON...")
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    else:
                        raise ValueError(f"Failed to get valid JSON after {max_retries} attempts: {str(parse_error)}")
            else:
                raise Exception("Empty response from API")

        except Exception as e:
            print(f"API call attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                time.sleep(delay)
            else:
                raise

    return None


def parse_gemini_response(response_text: str) -> Dict:
    """
    Parse and validate Gemini API response.

    Args:
        response_text: Raw response from Gemini API

    Returns:
        Parsed JSON dictionary
    """
    # Extract JSON from response (may have markdown code blocks)
    text = response_text.strip()

    # Remove markdown code blocks if present
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]

    if text.endswith('```'):
        text = text[:-3]

    text = text.strip()

    # Try to find JSON object boundaries
    start_idx = text.find('{')
    end_idx = text.rfind('}')

    if start_idx == -1 or end_idx == -1:
        raise ValueError("No JSON object found in response")

    json_text = text[start_idx:end_idx+1]

    try:
        data = json.loads(json_text)

        # Validate required fields
        required_keys = ['analysis', 'specialist_recommendations', 'educational_resources', 'next_steps']
        missing_keys = [key for key in required_keys if key not in data]

        if missing_keys:
            raise ValueError(f"Response missing required fields: {missing_keys}")

        return data

    except json.JSONDecodeError as e:
        # If JSON parsing fails, provide detailed error info
        print(f"JSON parse error: {str(e)}")
        print(f"Error at position {e.pos} (line {e.lineno}, column {e.colno})")
        print(f"Response length: {len(json_text)} characters")

        # Show context around error
        if e.pos > 0 and e.pos < len(json_text):
            context_start = max(0, e.pos - 100)
            context_end = min(len(json_text), e.pos + 100)
            print(f"Context: ...{json_text[context_start:context_end]}...")

        raise ValueError(f"Failed to parse JSON response at position {e.pos}: {str(e)}")


def analyze_symptoms(input_payload: Dict) -> Dict:
    """
    Main symptom analysis function.
    
    Args:
        input_payload: Validated input payload
        
    Returns:
        Complete output payload with analysis and recommendations
    """
    # Check for emergency symptoms first
    if detect_emergency_symptoms(input_payload.get('symptoms', [])):
        return {
            'disclaimer': DISCLAIMER,
            'emergency_warning': '🚨 SEEK IMMEDIATE MEDICAL ATTENTION 🚨\n\nCall 911 or go to the nearest emergency room immediately. These symptoms may indicate a medical emergency.',
            'analysis': {
                'symptom_clusters': [],
                'potential_root_causes': []
            },
            'specialist_recommendations': [
                {
                    'specialist_type': 'Emergency Room',
                    'reason': 'Your symptoms may indicate a medical emergency requiring immediate attention',
                    'priority': 'primary',
                    'what_they_treat': 'Life-threatening and urgent medical conditions'
                }
            ],
            'educational_resources': [],
            'next_steps': [
                'Call 911 immediately',
                'Go to the nearest emergency room',
                'Do not drive yourself - call an ambulance if needed'
            ],
            'followup_questions': [],
            'is_refined': False
        }
    
    # Build prompt and call API
    prompt = build_gemini_prompt(input_payload)
    
    try:
        response_text = call_gemini_api(prompt)
        if not response_text:
            raise Exception("No response from Gemini API")
        
        # Parse response
        analysis_data = parse_gemini_response(response_text)
        
        # Build complete output payload
        output = {
            'disclaimer': DISCLAIMER,
            'analysis': analysis_data.get('analysis', {}),
            'specialist_recommendations': analysis_data.get('specialist_recommendations', []),
            'educational_resources': analysis_data.get('educational_resources', []),
            'next_steps': analysis_data.get('next_steps', []),
            'emergency_warning': None,
            'is_refined': False
        }

        # Generate follow-up questions
        followup_questions = extract_followup_questions(input_payload, output)
        output['followup_questions'] = followup_questions

        return output
        
    except Exception as e:
        # Fallback response on error
        print(f"Error in symptom analysis: {str(e)}")
        return {
            'disclaimer': DISCLAIMER,
            'error': 'We are experiencing technical difficulties. Please try again or consult a medical professional.',
            'analysis': {
                'symptom_clusters': [],
                'potential_root_causes': []
            },
            'specialist_recommendations': [
                {
                    'specialist_type': 'Internal Medicine Specialist',
                    'reason': 'An internal medicine specialist can evaluate complex symptom patterns and coordinate care across multiple systems',
                    'priority': 'primary',
                    'what_they_treat': 'Complex multi-system conditions requiring comprehensive evaluation'
                }
            ],
            'educational_resources': [],
            'next_steps': [
                'Schedule an appointment with an internal medicine specialist or appropriate healthcare provider',
                'Keep a detailed symptom diary noting patterns and triggers',
                'Note any changes in symptoms or connections between them'
            ],
            'emergency_warning': None,
            'followup_questions': [],
            'is_refined': False
        }


def build_refinement_prompt(input_payload: Dict, initial_analysis: Dict, followup_answers: List[Dict]) -> str:
    """
    Build enriched prompt for refined analysis with follow-up context.

    Args:
        input_payload: Original symptom data
        initial_analysis: Previous analysis results
        followup_answers: User's answers to follow-up questions

    Returns:
        Formatted prompt string for refined analysis
    """
    symptoms = input_payload.get('symptoms', [])
    age_range = input_payload.get('age_range', 'Not provided')
    existing_conditions = input_payload.get('existing_conditions', [])
    medications = input_payload.get('medications', [])
    additional_context = input_payload.get('additional_context', '')

    # Format symptoms
    symptom_list = []
    for i, symptom in enumerate(symptoms, 1):
        desc = symptom.get('description', '')
        duration = symptom.get('duration', 'Not specified')
        severity = symptom.get('severity', 'Not specified')
        symptom_list.append(f"{i}. {desc} (Duration: {duration}, Severity: {severity})")

    # Format follow-up Q&A
    qa_list = []
    for i, qa in enumerate(followup_answers, 1):
        question = qa.get('question', '')
        answer = qa.get('answer', '')
        qa_list.append(f"Q{i}: {question}\nA{i}: {answer}")

    qa_text = '\n\n'.join(qa_list)

    # Extract initial specialists for context
    initial_specialists = initial_analysis.get('specialist_recommendations', [])
    specialist_summary = ', '.join([s.get('specialist_type', '') for s in initial_specialists[:3]])

    prompt = f"""You are a medical navigation advisor performing a REFINED symptom analysis based on follow-up information.

ORIGINAL SYMPTOMS:
{'\\n'.join(symptom_list)}

USER INFORMATION:
Age Range: {age_range}
Existing Conditions: {', '.join(existing_conditions) if existing_conditions else 'None reported'}
Current Medications: {', '.join(medications) if medications else 'None reported'}
Additional Context: {additional_context if additional_context else 'None provided'}

INITIAL SPECIALIST RECOMMENDATIONS:
{specialist_summary if specialist_summary else 'Under evaluation'}

FOLLOW-UP QUESTIONS & ANSWERS:
{qa_text}

TASK:
Based on the additional information from follow-up answers, provide a REFINED analysis with updated specialist recommendations.

HOLISTIC ANALYSIS FRAMEWORK:
With the additional context from follow-up answers, refine your understanding of:
- How symptoms connect across body systems
- Which systemic patterns best explain the symptom constellation
- What root cause most likely explains the interconnected symptoms

Consider the same holistic patterns as before:
- Endocrine/Hormonal, Autoimmune, Nutritional, Metabolic, Inflammatory, Gut-related, Stress/HPA axis

CRITICAL RULES:
- Never diagnose conditions
- Never provide medical advice or treatment recommendations
- Only suggest appropriate specialist types who can address interconnected issues
- Use advisory language: "may indicate", "consider", "could be related to"
- Never use diagnostic language: "you have", "diagnosed with", "you need"
- Provide 1-3 specialist recommendations maximum
- DO NOT recommend "Primary Care Physician"
- Focus on specialists who treat root causes and systemic patterns
- Note what the follow-up answers revealed about systemic connections
- Explain why recommendations changed or stayed the same based on holistic analysis

OUTPUT FORMAT (JSON only):
{{
  "analysis": {{
    "refinement_summary": "Brief explanation of what the follow-up answers revealed about systemic connections and root causes, and how they affected the holistic analysis",
    "symptom_clusters": [
      {{
        "symptoms": ["symptom1", "symptom2"],
        "possible_connections": "Educational explanation considering follow-up context"
      }}
    ],
    "potential_root_causes": [
      {{
        "category": "Medical category",
        "description": "Educational, non-diagnostic explanation incorporating new information",
        "related_symptoms": ["symptom1"],
        "confidence": "possible|likely|consider"
      }}
    ]
  }},
  "specialist_recommendations": [
    {{
      "specialist_type": "Specific specialist type",
      "reason": "Why this specialist is relevant (considering follow-up answers)",
      "priority": "primary|secondary|consider",
      "what_they_treat": "Brief explanation"
    }}
  ],
  "educational_resources": [
    {{
      "title": "Resource title",
      "source": "Credible source",
      "relevance": "Why this resource helps"
    }}
  ],
  "next_steps": [
    "Actionable advice considering follow-up context"
  ]
}}

Provide ONLY the JSON response, no additional text."""

    return prompt


def analyze_symptoms_refined(input_payload: Dict, initial_analysis: Dict, followup_answers: List[Dict]) -> Dict:
    """
    Perform refined symptom analysis with follow-up context.

    Args:
        input_payload: Original validated input
        initial_analysis: Previous analysis results
        followup_answers: User's answers to follow-up questions

    Returns:
        Complete refined output payload
    """
    # Check for emergencies (still important in refinement)
    if detect_emergency_symptoms(input_payload.get('symptoms', [])):
        return {
            'disclaimer': DISCLAIMER,
            'emergency_warning': '🚨 SEEK IMMEDIATE MEDICAL ATTENTION 🚨\n\nCall 911 or go to the nearest emergency room immediately. These symptoms may indicate a medical emergency.',
            'analysis': {
                'refinement_summary': 'Emergency symptoms detected - immediate medical attention required',
                'symptom_clusters': [],
                'potential_root_causes': []
            },
            'specialist_recommendations': [
                {
                    'specialist_type': 'Emergency Room',
                    'reason': 'Your symptoms may indicate a medical emergency requiring immediate attention',
                    'priority': 'primary',
                    'what_they_treat': 'Life-threatening and urgent medical conditions'
                }
            ],
            'educational_resources': [],
            'next_steps': [
                'Call 911 immediately',
                'Go to the nearest emergency room',
                'Do not drive yourself - call an ambulance if needed'
            ],
            'is_refined': True,
            'followup_questions': []
        }

    # Build refined prompt
    prompt = build_refinement_prompt(input_payload, initial_analysis, followup_answers)

    try:
        response_text = call_gemini_api(prompt)
        if not response_text:
            raise Exception("No response from Gemini API")

        # Parse response
        analysis_data = parse_gemini_response(response_text)

        # Build refined output payload
        output = {
            'disclaimer': DISCLAIMER,
            'analysis': analysis_data.get('analysis', {}),
            'specialist_recommendations': analysis_data.get('specialist_recommendations', []),
            'educational_resources': analysis_data.get('educational_resources', []),
            'next_steps': analysis_data.get('next_steps', []),
            'emergency_warning': None,
            'is_refined': True,
            'followup_questions': []  # No more questions after refinement
        }

        return output

    except Exception as e:
        # Fallback: return original analysis with error flag
        print(f"Error in refined analysis: {str(e)}")
        return {
            **initial_analysis,
            'error': 'Refinement failed. Showing original analysis.',
            'is_refined': False,
            'followup_questions': []
        }


if __name__ == '__main__':
    # Test the analyzer
    test_payload = {
        'symptoms': [
            {
                'description': 'Persistent fatigue and weakness',
                'duration': '3 months',
                'severity': 'moderate',
                'frequency': 'daily'
            },
            {
                'description': 'Unexplained weight gain',
                'duration': '2 months',
                'severity': 'mild'
            }
        ],
        'age_range': '30-40',
        'existing_conditions': [],
        'medications': [],
        'additional_context': 'Symptoms worse in the morning'
    }
    
    result = analyze_symptoms(test_payload)
    print(json.dumps(result, indent=2))
