# Symptom Analysis SOP

## Goal
Connect user symptoms to appropriate medical specialist types through AI-powered analysis, using a holistic systems medicine perspective that identifies cross-system connections and root causes.

## Inputs
- **Symptom Payload** (JSON):
  - `symptoms`: Array of symptom objects with description, duration, severity, frequency
  - `age_range`: Optional age range string
  - `existing_conditions`: Optional array of known conditions
  - `medications`: Optional array of current medications
  - `additional_context`: Optional free-text context

## Process Flow

**WhichDoctor uses a two-stage analysis process to provide more accurate specialist recommendations:**

### Stage 1: Initial Analysis + Question Generation
1. User submits symptoms
2. System performs initial analysis
3. AI generates 3-5 tailored follow-up questions
4. User sees results with optional refinement questions

### Stage 2: Refined Analysis (Optional)
1. User answers follow-up questions
2. System performs refined analysis with additional context
3. User sees updated recommendations with "What Changed" summary

---

### 1. Input Validation

**Initial Analysis Mode:**
- **Required**: At least 1 symptom with valid description (10-500 chars)
- **Sanitization**: Remove any potential injection attacks
- **Schema validation**: Ensure payload matches defined JSON schema
- **Error handling**: Return 400 Bad Request if validation fails

**Refinement Mode** (`is_refinement: true`):
- **Required**: All initial mode fields PLUS:
  - `initial_analysis`: Full initial analysis response
  - `followup_answers`: Array of question/answer pairs
- **Validation**: Ensure all follow-up questions were answered
- **Error handling**: Return 400 if refinement fields missing or invalid

### 2. Emergency Symptom Detection
**CRITICAL**: Check for emergency symptoms BEFORE AI analysis

**Emergency Triggers**:
- Chest pain or pressure
- Severe difficulty breathing
- Sudden severe headache
- Severe bleeding
- Loss of consciousness
- Stroke symptoms (FAST: Face drooping, Arm weakness, Speech difficulty, Time to call 911)
- Severe allergic reaction symptoms
- Suicidal thoughts or self-harm ideation

**Action**: If emergency detected → Return immediate warning, skip AI analysis

### 3. Build Gemini Prompt
**Prompt Structure**:
```
You are a medical navigation advisor helping users find the right specialist.

CRITICAL RULES:
- Never diagnose conditions
- Never provide medical advice or treatment recommendations
- Only suggest appropriate specialist types who can address interconnected issues
- Use advisory language: "may indicate", "consider", "could be related to"
- Never use diagnostic language: "you have", "diagnosed with", "you need"
- DO NOT recommend "Primary Care Physician" - they often don't know which specialist to refer to
- ONLY recommend specific specialists who have expertise in the interconnected patterns identified

HOLISTIC ANALYSIS FRAMEWORK:
Analyze symptoms from a systems medicine perspective. The human body is an
interconnected system where issues in one area can manifest in seemingly unrelated areas.

Actively look for:
- Cross-system connections (e.g., hormonal issues affecting multiple body systems)
- Cascade effects (e.g., nutritional deficiencies causing widespread symptoms)
- Bidirectional relationships (e.g., gut-brain axis, immune-endocrine interactions)
- Root cause patterns that explain multiple symptoms together

Common holistic patterns:
- Endocrine/Hormonal (thyroid, adrenal, reproductive)
- Autoimmune (inflammation across multiple organ systems)
- Nutritional (vitamin/mineral deficiencies causing diverse symptoms)
- Metabolic (blood sugar dysregulation, insulin resistance)
- Inflammatory (chronic inflammation in various systems)
- Gut-related (microbiome imbalances affecting digestion, mood, immunity, skin)
- Stress/HPA axis (chronic stress affecting hormones, immunity, digestion, sleep)

USER SYMPTOMS:
[Formatted symptom list with duration, severity, frequency]

AGE RANGE: [if provided]
EXISTING CONDITIONS: [if provided]
MEDICATIONS: [if provided]
ADDITIONAL CONTEXT: [if provided]

TASK:
1. Identify symptom clusters and explain HOW and WHY they connect across body systems
2. Suggest potential root cause CATEGORIES with systemic explanations (not diagnoses)
3. Recommend 1-3 specific specialist types who treat the ROOT system, not just individual symptoms
4. Provide educational resources from credible sources
5. Suggest next steps

OUTPUT FORMAT: JSON matching the defined output schema
```

### 4. Call Gemini API
**Configuration**:
- Model: `gemini-2.5-flash`
- Temperature: 0.3 (lower for medical consistency)
- Max tokens: 4096 (increased to prevent JSON truncation)
- Safety settings: Block harmful content

**Error Handling**:
- Network error → Retry with exponential backoff (3 attempts)
- Rate limit → Wait and retry
- **Malformed JSON** → Validate and retry up to 3 times
- API failure → Return graceful fallback response
- Timeout → Return error after 30 seconds

**Retry Logic with JSON Validation**:
```python
max_retries = 3
base_delay = 1  # seconds
for attempt in range(max_retries):
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            # Validate JSON before accepting response
            try:
                parse_gemini_response(response.text)
                return response.text
            except (json.JSONDecodeError, ValueError) as parse_error:
                if attempt < max_retries - 1:
                    # Retry if JSON is malformed
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise
    except Exception as e:
        if attempt < max_retries - 1:
            delay = base_delay * (2 ** attempt)  # Exponential backoff
            time.sleep(delay)
        else:
            raise
```

### 5. Parse AI Response
- Extract JSON from response text
- Validate against output schema
- Ensure disclaimer is present
- Verify no diagnostic language used
- Check that specialist recommendations are present

### 6. Generate Follow-Up Questions (Initial Analysis Only)

**Purpose**: Create tailored questions to narrow down specialist recommendations

**Process**:
1. Send initial analysis results to Gemini with specialized prompt
2. Request 3-5 specific clarifying questions
3. Questions focus on:
   - Identifying patterns across body systems
   - Timeline of symptom development (what appeared first, what followed)
   - Triggers and relieving factors (stress, diet, sleep, hormonal cycles)
   - Related symptoms the user might not have connected (fatigue, digestion, mood, sleep, skin)
   - Distinguishing between similar conditions
   - Identifying red flags or patterns

**Question Format**:
```json
{
  "id": "q1",
  "question": "Clear, specific question text?",
  "type": "text" | "select",
  "context": "Why this question matters",
  "options": ["Option 1", "Option 2"] // For select type
}
```

**Error Handling**:
- If question generation fails → Return empty questions array
- Continue showing initial analysis (graceful degradation)
- No crash or error displayed to user

**Quality Requirements**:
- Questions must help identify root causes and systemic patterns
- Use plain language (no medical jargon)
- Avoid asking for self-diagnosis
- Ask about seemingly unrelated symptoms that could reveal systemic connections
- Each question should help narrow specialist recommendation by revealing systemic patterns

### 7. Refinement Analysis (If User Answers Questions)

**When**: User submits answers to follow-up questions

**Process**:
1. Collect original symptoms + initial analysis + follow-up Q&A
2. Build enriched prompt including all context
3. Call Gemini API for refined analysis
4. Request `refinement_summary` explaining what changed

**Refinement Prompt Structure**:
```
ORIGINAL SYMPTOMS: [...]
INITIAL SPECIALIST RECOMMENDATIONS: [...]
FOLLOW-UP QUESTIONS & ANSWERS:
Q1: [question]
A1: [user's answer]
Q2: [question]
A2: [user's answer]

HOLISTIC ANALYSIS FRAMEWORK:
Refine understanding of how symptoms connect across body systems,
which systemic patterns best explain the symptom constellation,
and what root cause most likely explains the interconnected symptoms.

TASK: Provide REFINED analysis explaining:
- What the follow-up answers revealed about systemic connections and root causes
- Why recommendations changed (or stayed the same) based on holistic analysis
- More specific next steps based on new context
```

**Output Extensions**:
- `is_refined: true` flag
- `refinement_summary`: Explanation of what changed
- Updated specialist recommendations
- No new follow-up questions (prevents infinite loop)

**Emergency Detection**: Still runs even in refinement mode

### 8. Augment with Educational Resources (Optional)
- Search PubMed for relevant medical research
- Add credible sources (NIH, Mayo Clinic, etc.)
- Graceful degradation if PubMed unavailable

### 9. Validate Output

**Required Fields (Initial Analysis)**:
- `disclaimer`: Legal disclaimer text
- `analysis`: Symptom clusters and potential root causes
- `specialist_recommendations`: At least 1 specialist with explanation
- `next_steps`: Actionable advice
- `followup_questions`: Array of 0-5 questions (empty if generation failed)
- `is_refined`: false

**Additional Fields (Refined Analysis)**:
- `analysis.refinement_summary`: Explanation of what changed
- `is_refined`: true
- `followup_questions`: Empty array (no more questions)

**Quality Checks**:
- No diagnostic language
- Specialist recommendations are specific (e.g., "Endocrinologist", not "doctor")
- No "Primary Care Physician" or "General Healthcare Provider" recommendations
- Symptom clusters include systemic explanations of cross-body-system connections
- Root causes explain how they create cascading effects across systems
- Emergency warning present if applicable
- Educational resources from credible sources only
- Follow-up questions use plain language and probe for systemic patterns

### 10. Return Response
- HTTP 200 with JSON payload
- Include all required fields
- Log successful analysis (no PII)

## Edge Cases

### Empty or Invalid Symptoms
- **Trigger**: No symptoms provided or invalid format
- **Action**: Return 400 Bad Request with clear error message
- **User Message**: "Please provide at least one symptom description"

### Ambiguous Symptoms
- **Trigger**: Symptoms could indicate multiple unrelated conditions
- **Action**: Return multiple specialist recommendations with explanations
- **Example**: Fatigue could be endocrine, cardiac, or mental health related

### Emergency Symptoms
- **Trigger**: Life-threatening symptoms detected
- **Action**: Bypass AI analysis, return immediate emergency warning
- **Display**: Red banner with "SEEK IMMEDIATE MEDICAL ATTENTION"

### API Failure
- **Trigger**: Gemini API unavailable after retries
- **Action**: Return fallback response with Internal Medicine Specialist recommendation
- **Fallback**: "We're experiencing technical difficulties. Please try again or consult a medical professional."

### Rate Limiting
- **Trigger**: Too many requests from same user
- **Action**: Return 429 Too Many Requests
- **Message**: "Please wait a moment before submitting another analysis"

### Vague Symptoms
- **Trigger**: Symptoms too general to analyze (e.g., "I don't feel well")
- **Action**: AI generates follow-up questions to gather specifics
- **Benefit**: Two-stage flow naturally handles vague initial symptoms

### Question Generation Failure
- **Trigger**: Gemini API fails to generate follow-up questions
- **Action**: Return initial analysis with empty questions array
- **Graceful Degradation**: User still gets valuable specialist recommendations
- **User Impact**: No error shown, simply no refinement option available

### User Skips Follow-Up Questions
- **Trigger**: User clicks "Skip - Keep Current Results"
- **Action**: Remove follow-up form, keep initial analysis visible
- **No Loss**: User has initial recommendations, can return to form later if desired

## Behavioral Rules

### Advisory, Not Diagnostic
- ✅ "These symptoms may indicate a hormonal imbalance"
- ❌ "You have hypothyroidism"

### Holistic, Root-Cause Focused
- ✅ "These symptoms may suggest a thyroid imbalance affecting your metabolism, which could explain the fatigue, weight changes, and temperature sensitivity across multiple body systems"
- ❌ "You have three separate issues requiring three different doctors"

### Specific Specialists, Not General Providers
- ✅ "Consider consulting an Endocrinologist who specializes in hormonal imbalances"
- ❌ "See your general healthcare provider"
- ❌ "Visit your primary care physician"

### Specialist Types, Not Specific Doctors
- ✅ "Consider seeing an Endocrinologist"
- ❌ "You should see Dr. Smith at XYZ Clinic"

### Educational, Not Prescriptive
- ✅ "Thyroid function tests (TSH, T3, T4) can help identify hormonal issues"
- ❌ "You need to get thyroid tests immediately"

### Empowering, Not Alarming
- ✅ "These symptoms warrant professional evaluation"
- ❌ "This could be serious, you might have a dangerous condition"

## Logging and Monitoring

### What to Log
- Request timestamp
- Symptom count (not content - privacy)
- Model used
- Response time
- Success/failure status
- Error types (if any)

### What NOT to Log
- ❌ Symptom descriptions (PII)
- ❌ User demographics
- ❌ Medical history
- ❌ Any personally identifiable information

## Success Criteria

**Initial Analysis:**
- Response time < 5 seconds (95th percentile)
- API success rate > 99%
- Emergency detection accuracy: 100% (no false negatives)
- User receives actionable specialist recommendations
- No diagnostic language in output
- Disclaimer always present and prominent
- 3-5 relevant follow-up questions generated (when possible)

**Follow-Up Questions:**
- Questions are specific to submitted symptoms
- Questions use plain language (no medical jargon)
- Questions help distinguish between similar conditions
- Questions are answerable by typical user

**Refined Analysis:**
- Incorporates follow-up answers into holistic analysis
- Includes clear `refinement_summary` explaining systemic connections and changes
- More specific specialist recommendations based on root cause patterns
- No "Primary Care Physician" recommendations
- Graceful fallback to initial analysis on error
- No infinite question loops (refinement generates no new questions)

**User Experience:**
- Clear option to skip refinement (not forced)
- Both initial and refined analyses saved to history
- Smooth transition between analysis stages
- Mobile-responsive question forms
