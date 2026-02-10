// WhichDoctor - History Page JavaScript
// Loads and displays analysis history from localStorage

document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    setupEventListeners();
});

function setupEventListeners() {
    const clearBtn = document.getElementById('clearHistoryBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearHistory);
    }
}

function loadHistory() {
    try {
        const history = JSON.parse(localStorage.getItem('whichdoctor_history') || '[]');
        const container = document.getElementById('historyContainer');
        const emptyState = document.getElementById('emptyState');

        if (history.length === 0) {
            container.innerHTML = '';
            emptyState.style.display = 'block';
            return;
        }

        emptyState.style.display = 'none';
        container.innerHTML = '';

        history.forEach((entry, index) => {
            const entryElement = createHistoryEntry(entry, index);
            container.appendChild(entryElement);
        });

    } catch (error) {
        console.error('Failed to load history:', error);
        document.getElementById('historyContainer').innerHTML = `
            <div class="emergency-warning">
                <h4>Error Loading History</h4>
                <p>Unable to load your history. The data may be corrupted.</p>
            </div>
        `;
    }
}

function createHistoryEntry(entry, index) {
    const article = document.createElement('article');
    article.className = 'history-entry';
    article.setAttribute('data-entry-id', entry.id);

    const date = new Date(entry.timestamp);
    const formattedDate = date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    // Extract symptoms summary
    const symptomsSummary = entry.payload.symptoms
        .map(s => s.description.substring(0, 80) + (s.description.length > 80 ? '...' : ''))
        .join(' | ');

    // Extract specialist recommendations
    let specialistsHtml = '';
    if (entry.result.specialist_recommendations && entry.result.specialist_recommendations.length > 0) {
        specialistsHtml = '<div class="specialists-summary"><strong>Recommended:</strong> ';
        specialistsHtml += entry.result.specialist_recommendations
            .map(spec => spec.specialist_type)
            .join(', ');
        specialistsHtml += '</div>';
    }

    // Emergency warning
    let warningHtml = '';
    if (entry.result.emergency_warning) {
        warningHtml = `
            <div class="emergency-warning" style="margin-top: 1rem;">
                <strong>⚠️ Emergency Warning:</strong> ${entry.result.emergency_warning}
            </div>
        `;
    }

    article.innerHTML = `
        <div class="history-header">
            <h3>Analysis from ${formattedDate}</h3>
            <div class="history-actions">
                <button class="btn btn-secondary btn-sm" onclick="downloadHistoryEntry(${entry.id})">Download PDF</button>
                <button class="btn btn-secondary btn-sm" onclick="deleteHistoryEntry(${entry.id})">Delete</button>
            </div>
        </div>

        <div class="history-content">
            <div class="symptoms-summary">
                <strong>Symptoms:</strong> ${symptomsSummary}
            </div>

            ${specialistsHtml}
            ${warningHtml}

            <button class="btn btn-link" onclick="toggleDetails(${entry.id})">
                <span id="toggle-text-${entry.id}">Show Full Details</span>
            </button>

            <div id="details-${entry.id}" class="history-details" style="display: none;">
                ${generateDetailsHtml(entry)}
            </div>
        </div>
    `;

    return article;
}

function generateDetailsHtml(entry) {
    const result = entry.result;
    let html = '';

    // Full symptoms
    html += '<div class="detail-section"><h4>Symptoms Analyzed</h4><ul>';
    entry.payload.symptoms.forEach(symptom => {
        html += `<li><strong>${symptom.description}</strong>`;
        if (symptom.duration) html += `<br>Duration: ${symptom.duration}`;
        if (symptom.severity) html += `, Severity: ${symptom.severity}`;
        if (symptom.frequency) html += `, Frequency: ${symptom.frequency}`;
        html += '</li>';
    });
    html += '</ul></div>';

    // Additional context
    if (entry.payload.age_range || entry.payload.existing_conditions?.length > 0 ||
        entry.payload.medications?.length > 0 || entry.payload.additional_context) {
        html += '<div class="detail-section"><h4>Additional Information</h4>';
        if (entry.payload.age_range) html += `<p><strong>Age Range:</strong> ${entry.payload.age_range}</p>`;
        if (entry.payload.existing_conditions?.length > 0) {
            html += `<p><strong>Existing Conditions:</strong> ${entry.payload.existing_conditions.join(', ')}</p>`;
        }
        if (entry.payload.medications?.length > 0) {
            html += `<p><strong>Medications:</strong> ${entry.payload.medications.join(', ')}</p>`;
        }
        if (entry.payload.additional_context) {
            html += `<p><strong>Additional Context:</strong> ${entry.payload.additional_context}</p>`;
        }
        html += '</div>';
    }

    // Specialist Recommendations
    if (result.specialist_recommendations && result.specialist_recommendations.length > 0) {
        html += '<div class="detail-section"><h4>Specialist Recommendations</h4>';
        result.specialist_recommendations.forEach(spec => {
            const badgeClass = spec.priority === 'primary' ? 'primary' : 'secondary';
            html += `
                <div class="specialist-card ${spec.priority}">
                    <span class="badge ${badgeClass}">${spec.priority.toUpperCase()}</span>
                    <h5>${spec.specialist_type}</h5>
                    <p><strong>Why:</strong> ${spec.reason}</p>
                    <p><strong>What they treat:</strong> ${spec.what_they_treat}</p>
                </div>
            `;
        });
        html += '</div>';
    }

    // Analysis
    if (result.analysis && result.analysis.potential_root_causes && result.analysis.potential_root_causes.length > 0) {
        html += '<div class="detail-section"><h4>Potential Root Cause Categories</h4>';
        result.analysis.potential_root_causes.forEach(cause => {
            html += `
                <div class="specialist-card">
                    <h5>${cause.category}</h5>
                    <p>${cause.description}</p>
                    <p><small><strong>Confidence:</strong> ${cause.confidence}</small></p>
                </div>
            `;
        });
        html += '</div>';
    }

    // Next Steps
    if (result.next_steps && result.next_steps.length > 0) {
        html += '<div class="detail-section"><h4>Recommended Next Steps</h4><ul class="resource-list">';
        result.next_steps.forEach(step => {
            html += `<li>${step}</li>`;
        });
        html += '</ul></div>';
    }

    // Educational Resources
    if (result.educational_resources && result.educational_resources.length > 0) {
        html += '<div class="detail-section"><h4>Educational Resources</h4><ul class="resource-list">';
        result.educational_resources.forEach(resource => {
            if (resource.url) {
                html += `<li><a href="${resource.url}" target="_blank">${resource.title}</a> - ${resource.source}<br><small>${resource.relevance}</small></li>`;
            } else {
                html += `<li><strong>${resource.title}</strong> - ${resource.source}<br><small>${resource.relevance}</small></li>`;
            }
        });
        html += '</ul></div>';
    }

    // Disclaimer
    if (result.disclaimer) {
        html += `
            <div class="disclaimer" style="margin-top: 2rem;">
                <h4>⚠️ Medical Disclaimer</h4>
                <p>${result.disclaimer}</p>
            </div>
        `;
    }

    return html;
}

function toggleDetails(entryId) {
    const details = document.getElementById(`details-${entryId}`);
    const toggleText = document.getElementById(`toggle-text-${entryId}`);

    if (details.style.display === 'none') {
        details.style.display = 'block';
        toggleText.textContent = 'Hide Full Details';
    } else {
        details.style.display = 'none';
        toggleText.textContent = 'Show Full Details';
    }
}

function deleteHistoryEntry(entryId) {
    if (!confirm('Are you sure you want to delete this history entry?')) {
        return;
    }

    try {
        const history = JSON.parse(localStorage.getItem('whichdoctor_history') || '[]');
        const filteredHistory = history.filter(entry => entry.id !== entryId);
        localStorage.setItem('whichdoctor_history', JSON.stringify(filteredHistory));

        loadHistory(); // Reload the display
    } catch (error) {
        console.error('Failed to delete entry:', error);
        alert('Failed to delete entry. Please try again.');
    }
}

function clearHistory() {
    if (!confirm('Are you sure you want to clear all history? This cannot be undone.')) {
        return;
    }

    localStorage.removeItem('whichdoctor_history');
    loadHistory();
}

function downloadHistoryEntry(entryId) {
    try {
        const history = JSON.parse(localStorage.getItem('whichdoctor_history') || '[]');
        const entry = history.find(e => e.id === entryId);

        if (!entry) {
            alert('Entry not found');
            return;
        }

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        const date = new Date(entry.timestamp);
        const formattedDate = date.toLocaleString();

        // Add title
        doc.setFontSize(16);
        doc.text('WhichDoctor - Analysis Results', 10, 10);

        // Add date
        doc.setFontSize(10);
        doc.text(`Analysis Date: ${formattedDate}`, 10, 20);

        // Add symptoms
        doc.setFontSize(12);
        doc.text('Symptoms:', 10, 30);
        doc.setFontSize(10);
        let yPos = 35;
        entry.payload.symptoms.forEach((symptom, idx) => {
            const text = `${idx + 1}. ${symptom.description}`;
            const lines = doc.splitTextToSize(text, 180);
            doc.text(lines, 10, yPos);
            yPos += lines.length * 5 + 3;
        });

        // Add specialists
        if (entry.result.specialist_recommendations && entry.result.specialist_recommendations.length > 0) {
            yPos += 5;
            doc.setFontSize(12);
            doc.text('Recommended Specialists:', 10, yPos);
            yPos += 5;
            doc.setFontSize(10);

            entry.result.specialist_recommendations.forEach(spec => {
                const text = `- ${spec.specialist_type} (${spec.priority}): ${spec.reason}`;
                const lines = doc.splitTextToSize(text, 180);
                doc.text(lines, 10, yPos);
                yPos += lines.length * 5 + 3;
            });
        }

        // Add disclaimer
        yPos += 10;
        doc.setFontSize(8);
        const disclaimer = doc.splitTextToSize(entry.result.disclaimer || 'This is educational information only.', 180);
        doc.text(disclaimer, 10, yPos);

        // Save
        doc.save(`whichdoctor-history-${entryId}.pdf`);
    } catch (error) {
        console.error('Failed to download PDF:', error);
        alert('Failed to download PDF. Please try again.');
    }
}
