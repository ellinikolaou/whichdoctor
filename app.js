// WhichDoctor - Frontend JavaScript
// Handles form submission, API calls, results display, and localStorage

const API_URL = 'http://localhost:5000/api/analyze';
let symptomCount = 1;
let initialAnalysisData = null;  // Store initial analysis for refinement

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeForm();
    setupEventListeners();
    updateCharacterCounts();
});

function initializeForm() {
    // Add character counter to first symptom
    const firstTextarea = document.getElementById('symptom-desc-0');
    if (firstTextarea) {
        firstTextarea.addEventListener('input', updateCharacterCount);
    }
}

function setupEventListeners() {
    // Add symptom button
    const addSymptomBtn = document.getElementById('addSymptomBtn');
    if (addSymptomBtn) {
        addSymptomBtn.addEventListener('click', addSymptomField);
    }

    // Form submission
    const form = document.getElementById('symptomForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }

    // Download PDF button
    const downloadBtn = document.getElementById('downloadPdfBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadPDF);
    }
}

function addSymptomField() {
    symptomCount++;
    const container = document.getElementById('symptomsContainer');

    const symptomGroup = document.createElement('div');
    symptomGroup.className = 'symptom-group';
    symptomGroup.setAttribute('data-symptom-index', symptomCount - 1);

    symptomGroup.innerHTML = `
        <h4>Symptom ${symptomCount}</h4>
        <div class="form-group">
            <label for="symptom-desc-${symptomCount - 1}">Description *</label>
            <textarea 
                id="symptom-desc-${symptomCount - 1}" 
                name="symptom-desc-${symptomCount - 1}" 
                required 
                minlength="10" 
                maxlength="500"
                placeholder="Describe your symptom in detail"
                rows="3"
            ></textarea>
            <small class="char-count">0 / 500 characters</small>
        </div>
        
        <div class="form-row">
            <div class="form-group">
                <label for="symptom-duration-${symptomCount - 1}">Duration</label>
                <input 
                    type="text" 
                    id="symptom-duration-${symptomCount - 1}" 
                    name="symptom-duration-${symptomCount - 1}"
                    placeholder="e.g., '2 weeks', '3 months'"
                >
            </div>
            
            <div class="form-group">
                <label for="symptom-severity-${symptomCount - 1}">Severity</label>
                <select id="symptom-severity-${symptomCount - 1}" name="symptom-severity-${symptomCount - 1}">
                    <option value="">Select...</option>
                    <option value="mild">Mild</option>
                    <option value="moderate">Moderate</option>
                    <option value="severe">Severe</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="symptom-frequency-${symptomCount - 1}">Frequency</label>
                <input 
                    type="text" 
                    id="symptom-frequency-${symptomCount - 1}" 
                    name="symptom-frequency-${symptomCount - 1}"
                    placeholder="e.g., 'daily', 'intermittent'"
                >
            </div>
        </div>
        <button type="button" class="btn btn-secondary" onclick="removeSymptom(${symptomCount - 1})">Remove Symptom</button>
    `;

    container.appendChild(symptomGroup);

    // Add character counter to new textarea
    const textarea = symptomGroup.querySelector('textarea');
    textarea.addEventListener('input', updateCharacterCount);
}

function removeSymptom(index) {
    const symptomGroup = document.querySelector(`[data-symptom-index="${index}"]`);
    if (symptomGroup && symptomCount > 1) {
        symptomGroup.remove();
        symptomCount--;
        renumberSymptoms();
    }
}

function renumberSymptoms() {
    const symptomGroups = document.querySelectorAll('.symptom-group');
    symptomGroups.forEach((group, index) => {
        const heading = group.querySelector('h4');
        if (heading) {
            heading.textContent = `Symptom ${index + 1}`;
        }
    });
}

function updateCharacterCount(event) {
    const textarea = event.target;
    const charCount = textarea.value.length;
    const counter = textarea.parentElement.querySelector('.char-count');
    if (counter) {
        counter.textContent = `${charCount} / 500 characters`;
    }
}

function updateCharacterCounts() {
    const textareas = document.querySelectorAll('textarea[id^="symptom-desc-"]');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', updateCharacterCount);
    });
}

async function handleFormSubmit(event) {
    event.preventDefault();

    // Collect form data
    const payload = collectFormData();

    // Validate
    if (!payload.symptoms || payload.symptoms.length === 0) {
        alert('Please add at least one symptom');
        return;
    }

    // Show loading state
    showLoading();

    try {
        // Call API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'API request failed');
        }

        const result = await response.json();

        // Save to localStorage
        saveToHistory(payload, result);

        // Display results
        displayResults(result);

        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}. Please try again.`);
    } finally {
        hideLoading();
    }
}

function collectFormData() {
    const symptoms = [];

    // Collect all symptoms
    for (let i = 0; i < symptomCount; i++) {
        const descElement = document.getElementById(`symptom-desc-${i}`);
        if (!descElement) continue;

        const description = descElement.value.trim();
        if (!description) continue;

        const symptom = {
            description: description,
            duration: document.getElementById(`symptom-duration-${i}`)?.value || '',
            severity: document.getElementById(`symptom-severity-${i}`)?.value || '',
            frequency: document.getElementById(`symptom-frequency-${i}`)?.value || ''
        };

        symptoms.push(symptom);
    }

    // Collect additional info
    const ageRange = document.getElementById('ageRange')?.value || '';
    const existingConditions = document.getElementById('existingConditions')?.value
        .split(',')
        .map(c => c.trim())
        .filter(c => c);
    const medications = document.getElementById('medications')?.value
        .split(',')
        .map(m => m.trim())
        .filter(m => m);
    const additionalContext = document.getElementById('additionalContext')?.value || '';

    return {
        symptoms,
        age_range: ageRange,
        existing_conditions: existingConditions,
        medications: medications,
        additional_context: additionalContext
    };
}

function showLoading(message = 'Analyzing your symptoms...') {
    const loadingState = document.getElementById('loadingState');
    const loadingText = loadingState.querySelector('p');
    if (loadingText) {
        loadingText.textContent = message;
    }
    loadingState.style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('submitBtn').disabled = true;
}

function hideLoading() {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('submitBtn').disabled = false;
}

function buildResultsHTML(result) {
    let html = '';

    // Emergency Warning
    if (result.emergency_warning) {
        html += `
            <div class="emergency-warning">
                <h4>🚨 SEEK IMMEDIATE MEDICAL ATTENTION 🚨</h4>
                <p>${result.emergency_warning}</p>
            </div>
        `;
    }

    // Error Message
    if (result.error) {
        html += `
            <div class="emergency-warning">
                <h4>⚠️ Technical Issue</h4>
                <p>${result.error}</p>
            </div>
        `;
    }

    // Specialist Recommendations
    if (result.specialist_recommendations && result.specialist_recommendations.length > 0) {
        html += '<h4>Recommended Specialists</h4>';
        result.specialist_recommendations.forEach(spec => {
            const badgeClass = spec.priority === 'primary' ? 'primary' : 'secondary';
            html += `
                <div class="specialist-card ${spec.priority}">
                    <span class="badge ${badgeClass}">${spec.priority.toUpperCase()}</span>
                    <h4>${spec.specialist_type}</h4>
                    <p><strong>Why:</strong> ${spec.reason}</p>
                    <p><strong>What they treat:</strong> ${spec.what_they_treat}</p>
                </div>
            `;
        });
    }

    // Analysis
    if (result.analysis && result.analysis.potential_root_causes && result.analysis.potential_root_causes.length > 0) {
        html += '<h4>Potential Root Cause Categories</h4>';
        result.analysis.potential_root_causes.forEach(cause => {
            html += `
                <div class="specialist-card">
                    <h4>${cause.category}</h4>
                    <p>${cause.description}</p>
                    <p><small><strong>Confidence:</strong> ${cause.confidence}</small></p>
                </div>
            `;
        });
    }

    // Next Steps
    if (result.next_steps && result.next_steps.length > 0) {
        html += '<h4>Recommended Next Steps</h4><ul class="resource-list">';
        result.next_steps.forEach(step => {
            html += `<li>${step}</li>`;
        });
        html += '</ul>';
    }

    // Educational Resources
    if (result.educational_resources && result.educational_resources.length > 0) {
        html += '<h4>Educational Resources</h4><ul class="resource-list">';
        result.educational_resources.forEach(resource => {
            if (resource.url) {
                html += `<li><a href="${resource.url}" target="_blank">${resource.title}</a> - ${resource.source}<br><small>${resource.relevance}</small></li>`;
            } else {
                html += `<li><strong>${resource.title}</strong> - ${resource.source}<br><small>${resource.relevance}</small></li>`;
            }
        });
        html += '</ul>';
    }

    // Disclaimer
    html += `
        <div class="disclaimer" style="margin-top: 2rem;">
            <h2>⚠️ Medical Disclaimer</h2>
            <p>${result.disclaimer}</p>
        </div>
    `;

    return html;
}

function displayResults(result) {
    const resultsContent = document.getElementById('resultsContent');
    const resultsSection = document.getElementById('resultsSection');

    // Build and display HTML
    const html = buildResultsHTML(result);
    resultsContent.innerHTML = html;
    resultsSection.style.display = 'block';

    // Display follow-up questions if present and not refined
    if (result.followup_questions && result.followup_questions.length > 0 && !result.is_refined) {
        displayFollowUpQuestions(result.followup_questions, result);
    }
}

function renderQuestion(question) {
    if (question.type === 'select' && question.options) {
        return `
            <div class="form-group followup-question">
                <label for="followup-${question.id}">
                    ${question.question}
                    ${question.context ? `<small class="question-context">${question.context}</small>` : ''}
                </label>
                <select id="followup-${question.id}" name="${question.id}" required>
                    <option value="">Select...</option>
                    ${question.options.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                </select>
            </div>
        `;
    } else {
        // Default to text input
        return `
            <div class="form-group followup-question">
                <label for="followup-${question.id}">
                    ${question.question}
                    ${question.context ? `<small class="question-context">${question.context}</small>` : ''}
                </label>
                <textarea
                    id="followup-${question.id}"
                    name="${question.id}"
                    required
                    maxlength="500"
                    rows="2"
                    placeholder="Your answer"
                ></textarea>
            </div>
        `;
    }
}

function displayFollowUpQuestions(questions, analysisResult) {
    if (!questions || questions.length === 0) {
        return;
    }

    // Store initial analysis for later refinement
    initialAnalysisData = analysisResult;

    const resultsSection = document.getElementById('resultsSection');

    // Create follow-up section
    const followupSection = document.createElement('div');
    followupSection.id = 'followupSection';
    followupSection.className = 'followup-section';
    followupSection.innerHTML = `
        <div class="followup-header">
            <h3>Refine Your Analysis</h3>
            <p>Answer these questions for more specific recommendations:</p>
        </div>
        <form id="followupForm">
            ${questions.map(q => renderQuestion(q)).join('')}
            <div class="followup-actions">
                <button type="submit" class="btn btn-primary">Get Refined Analysis</button>
                <button type="button" class="btn btn-secondary" onclick="skipFollowUp()">
                    Skip - Keep Current Results
                </button>
            </div>
        </form>
    `;

    // Insert after results content
    resultsSection.appendChild(followupSection);

    // Add submit handler
    document.getElementById('followupForm').addEventListener('submit', handleFollowUpSubmit);
}

function skipFollowUp() {
    const followupSection = document.getElementById('followupSection');
    if (followupSection) {
        followupSection.remove();
    }
    // Keep current results visible
}

async function handleFollowUpSubmit(event) {
    event.preventDefault();

    if (!initialAnalysisData) {
        alert('Error: Initial analysis data not found');
        return;
    }

    // Collect follow-up answers
    const followupAnswers = [];
    const questions = initialAnalysisData.followup_questions || [];

    questions.forEach(q => {
        const input = document.getElementById(`followup-${q.id}`);
        if (input && input.value) {
            followupAnswers.push({
                question_id: q.id,
                question: q.question,
                answer: input.value
            });
        }
    });

    // Validate all questions answered
    if (followupAnswers.length !== questions.length) {
        alert('Please answer all questions');
        return;
    }

    // Build refinement payload
    const originalPayload = collectFormData();  // Re-collect original symptom data
    const refinementPayload = {
        ...originalPayload,
        is_refinement: true,
        initial_analysis: initialAnalysisData,
        followup_answers: followupAnswers
    };

    // Show loading
    showLoading('Refining your analysis...');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(refinementPayload)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Refinement failed');
        }

        const refinedResult = await response.json();

        // Save refined analysis to history
        saveToHistory(refinementPayload, refinedResult);

        // Display refined results
        displayRefinedResults(refinedResult, initialAnalysisData);

        // Remove follow-up form
        const followupSection = document.getElementById('followupSection');
        if (followupSection) {
            followupSection.remove();
        }

    } catch (error) {
        console.error('Refinement error:', error);
        alert(`Error: ${error.message}. Keeping current results.`);
    } finally {
        hideLoading();
    }
}

function displayRefinedResults(refinedResult, initialResult) {
    const resultsContent = document.getElementById('resultsContent');
    const resultsSection = document.getElementById('resultsSection');

    // Add refinement banner
    let html = `
        <div class="refinement-banner">
            <h4>✨ Refined Analysis</h4>
            <p>Based on your additional answers, here are updated recommendations:</p>
        </div>
    `;

    // Show what changed (if refinement_summary exists)
    if (refinedResult.analysis?.refinement_summary) {
        html += `
            <div class="refinement-summary">
                <h4>What Changed</h4>
                <p>${refinedResult.analysis.refinement_summary}</p>
            </div>
        `;
    }

    // Display rest of results (reuse existing display logic)
    html += buildResultsHTML(refinedResult);

    resultsContent.innerHTML = html;
    resultsSection.style.display = 'block';

    // Scroll to top of results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function saveToHistory(payload, result) {
    try {
        const history = JSON.parse(localStorage.getItem('whichdoctor_history') || '[]');

        const entry = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            payload: payload,
            result: result,
            is_refined: result.is_refined || false,
            has_followup: (result.followup_questions || []).length > 0
        };

        history.unshift(entry); // Add to beginning

        // Keep only last 10 entries
        if (history.length > 10) {
            history.splice(10);
        }

        localStorage.setItem('whichdoctor_history', JSON.stringify(history));
    } catch (error) {
        console.error('Failed to save to history:', error);
    }
}

function downloadPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const resultsContent = document.getElementById('resultsContent');
    const text = resultsContent.innerText;

    // Add title
    doc.setFontSize(16);
    doc.text('WhichDoctor - Analysis Results', 10, 10);

    // Add date
    doc.setFontSize(10);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 10, 20);

    // Add content
    doc.setFontSize(10);
    const lines = doc.splitTextToSize(text, 180);
    doc.text(lines, 10, 30);

    // Save
    doc.save(`whichdoctor-analysis-${Date.now()}.pdf`);
}
