/**
 * Privacy Query Interface - Frontend JavaScript
 * Handles form submission, API calls, UI updates, and interactions
 */

// =====================================================================
// CONSTANTS
// =====================================================================

const API_TIMEOUT = 60000; // 60 seconds timeout for Ollama API

// =====================================================================
// INITIALIZATION
// =====================================================================

document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadQueryHistory();
});

function setupEventListeners() {
    // Form submission
    const queryForm = document.getElementById('query-form');
    if (queryForm) {
        queryForm.addEventListener('submit', handleQuerySubmit);
    }

    // Input type radio buttons
    const textRadio = document.getElementById('text-input');
    const fileRadio = document.getElementById('file-input');
    if (textRadio && fileRadio) {
        textRadio.addEventListener('change', toggleInputType);
        fileRadio.addEventListener('change', toggleInputType);
    }

    // Tab navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

// =====================================================================
// INPUT TYPE TOGGLE
// =====================================================================

function toggleInputType() {
    const textSection = document.getElementById('text-input-section');
    const fileSection = document.getElementById('file-input-section');
    const textRadio = document.getElementById('text-input');
    const fileRadio = document.getElementById('file-input');
    const textArea = document.getElementById('query-input');
    const fileInput = document.getElementById('file-input-field');
    
    if (textRadio.checked) {
        textSection.style.display = 'block';
        fileSection.style.display = 'none';
        textArea.required = true;
        fileInput.required = false;
    } else {
        textSection.style.display = 'none';
        fileSection.style.display = 'block';
        textArea.required = false;
        fileInput.required = true;
    }
}

// =====================================================================
// TAB SWITCHING
// =====================================================================

function switchTab(tabName) {
    // Hide all tabs
    document.getElementById('query-tab').style.display = 'none';
    document.getElementById('history-tab').style.display = 'none';
    document.getElementById('guide-tab').style.display = 'none';

    // Remove active class from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName + '-tab').style.display = 'block';

    // Add active class to clicked nav link
    event.target.classList.add('active');

    // Load history if switching to history tab
    if (tabName === 'history') {
        loadQueryHistory();
    }
}

// =====================================================================
// QUERY SUBMISSION & PROCESSING
// =====================================================================

async function handleQuerySubmit(e) {
    e.preventDefault();

    const textRadio = document.getElementById('text-input');
    const isTextInput = textRadio.checked;
    
    let requestBody;
    let headers = {};

    if (isTextInput) {
        // Text input
        const queryText = document.getElementById('query-input').value.trim();
        
        // Validation
        if (!queryText || queryText.length < 3) {
            showToast('Query must be at least 3 characters', 'danger');
            return;
        }
        
        headers['Content-Type'] = 'application/json';
        requestBody = JSON.stringify({ query: queryText });
    } else {
        // File input
        const fileInput = document.getElementById('file-input-field');
        const file = fileInput.files[0];
        
        // Validation
        if (!file) {
            showToast('Please select a file to upload', 'danger');
            return;
        }
        
        const allowedTypes = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.txt') && !file.name.toLowerCase().endsWith('.pdf') && !file.name.toLowerCase().endsWith('.docx')) {
            showToast('Unsupported file type. Please upload TXT, PDF, or DOCX files.', 'danger');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        requestBody = formData;
        // Don't set Content-Type header for FormData - let browser set it with boundary
    }

    // Show loading spinner
    showLoadingSpinner(true);

    try {
        // Submit query to API
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: headers,
            body: requestBody
        });

        const data = await response.json();

        // Process response
        if (data.success) {
            displayResults(data);
            showToast('Query processed successfully!', 'success');
        } else {
            showToast(`Error: ${data.error}`, 'danger');
            displayPartialResults(data);
        }

    } catch (error) {
        console.error('Error:', error);
        showToast(`Network error: ${error.message}`, 'danger');
    } finally {
        showLoadingSpinner(false);
    }
}

// =====================================================================
// RESULTS DISPLAY
// =====================================================================

function displayResults(data) {
    // Show results section
    document.getElementById('results-section').style.display = 'block';
    document.getElementById('risk-card').style.display = 'block';
    document.getElementById('entities-card').style.display = 'block';

    // Display original query
    document.getElementById('original-query').textContent = data.original_query;

    // Display masked query
    document.getElementById('masked-query').textContent = data.masked_query;

    // Display risk score
    updateRiskScore(data.risk_score, data.risk_color);

    // Display detected entities
    displayDetectedEntities(data.detected_entities);

    // Display AI response
    document.getElementById('ai-response').textContent = data.ai_response;

    // Display unmasked response
    document.getElementById('unmasked-response').textContent = data.unmasked_response;

    // Scroll to results
    setTimeout(() => {
        document.getElementById('results-section').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }, 100);
}

function displayPartialResults(data) {
    // Show results section (even with error)
    document.getElementById('results-section').style.display = 'block';
    document.getElementById('risk-card').style.display = 'block';
    document.getElementById('entities-card').style.display = 'block';

    // Display available data
    document.getElementById('original-query').textContent = data.original_query || 'N/A';
    document.getElementById('masked-query').textContent = data.masked_query || 'N/A';

    // Display risk score
    updateRiskScore(data.risk_score, data.risk_color);

    // Display detected entities
    displayDetectedEntities(data.detected_entities || {});

    // Display error message
    document.getElementById('ai-response').textContent = `Error: ${data.error}`;
    document.getElementById('unmasked-response').textContent = 'Unable to process due to API error.';
}

// =====================================================================
// RISK SCORE VISUALIZATION
// =====================================================================

function updateRiskScore(score, color) {
    const scoreDisplay = document.getElementById('risk-score-display');
    const scoreBar = document.getElementById('risk-bar');
    const riskLevel = document.getElementById('risk-level');

    // Update circle value
    scoreDisplay.querySelector('.risk-value').textContent = score.toFixed(0);

    // Update circle color
    scoreDisplay.classList.remove('risk-low', 'risk-medium', 'risk-high');
    if (color === 'green') {
        scoreDisplay.classList.add('risk-low');
        riskLevel.innerHTML = '<span class="badge bg-success">Low Risk</span>';
    } else if (color === 'yellow') {
        scoreDisplay.classList.add('risk-medium');
        riskLevel.innerHTML = '<span class="badge bg-warning">Medium Risk</span>';
    } else {
        scoreDisplay.classList.add('risk-high');
        riskLevel.innerHTML = '<span class="badge bg-danger">High Risk</span>';
    }

    // Update progress bar
    scoreBar.style.width = score + '%';
    scoreBar.className = 'progress-bar bg-' + (
        color === 'green' ? 'success' :
        color === 'yellow' ? 'warning' :
        'danger'
    );
    scoreBar.setAttribute('aria-valuenow', score);
}

// =====================================================================
// ENTITY DISPLAY
// =====================================================================

function displayDetectedEntities(entities) {
    const entitiesContainer = document.getElementById('entities-list');
    entitiesContainer.innerHTML = '';

    // Count total entities
    let totalCount = 0;
    for (const key in entities) {
        if (Array.isArray(entities[key])) {
            totalCount += entities[key].length;
        }
    }

    if (totalCount === 0) {
        entitiesContainer.innerHTML = '<p class="text-muted">✅ No PII detected in your query</p>';
        return;
    }

    // Create entity sections
    let html = `<p class="text-muted mb-3">🔍 Detected ${totalCount} PII item(s):</p>`;

    for (const [entityType, items] of Object.entries(entities)) {
        if (Array.isArray(items) && items.length > 0) {
            html += '<div class="entity-section">';
            html += `<h6><i class="fas fa-circle-exclamation me-2"></i>${entityType}</h6>`;

            items.forEach(item => {
                html += `<div class="entity-item">
                    • <code>${escapeHtml(item.text)}</code>
                </div>`;
            });

            html += '</div>';
        }
    }

    entitiesContainer.innerHTML = html;
}

// =====================================================================
// QUERY HISTORY
// =====================================================================

function loadQueryHistory(page = 1) {
    const historyList = document.getElementById('history-list');

    fetch(`/api/history?page=${page}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.history && data.history.length > 0) {
                displayHistory(data.history);
            } else {
                historyList.innerHTML = '<p class="text-muted text-center py-4">No queries found</p>';
            }
        })
        .catch(error => {
            console.error('Error loading history:', error);
            historyList.innerHTML = '<p class="text-danger">Error loading history</p>';
        });
}

function displayHistory(history) {
    const historyList = document.getElementById('history-list');
    let html = '<table class="table table-hover">';
    html += `<thead>
        <tr>
            <th>Query</th>
            <th>Risk Score</th>
            <th>Date</th>
            <th>Actions</th>
        </tr>
    </thead><tbody>`;

    history.forEach(query => {
        const date = new Date(query.timestamp).toLocaleString();
        const riskClass = query.risk_score <= 30 ? 'success' : 
                         query.risk_score <= 70 ? 'warning' : 'danger';
        
        html += `<tr>
            <td><strong>${escapeHtml(query.original_query)}</strong></td>
            <td><span class="badge bg-${riskClass}">${query.risk_score.toFixed(1)}</span></td>
            <td>${date}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewQueryDetail(${query.id})">
                    <i class="fas fa-eye me-1"></i>View
                </button>
            </td>
        </tr>`;
    });

    html += '</tbody></table>';
    historyList.innerHTML = html;
}

function viewQueryDetail(queryId) {
    fetch(`/api/query/${queryId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display in main query section
                document.getElementById('query-input').value = data.original_query;

                // Hide risk and entity cards temporarily
                document.getElementById('risk-card').style.display = 'none';
                document.getElementById('entities-card').style.display = 'none';

                // Display results
                displayResults({
                    success: true,
                    original_query: data.original_query,
                    masked_query: data.masked_query,
                    risk_score: data.risk_score,
                    risk_color: data.risk_score <= 30 ? 'green' :
                               data.risk_score <= 70 ? 'yellow' : 'red',
                    detected_entities: data.detected_entities,
                    ai_response: data.ai_response,
                    unmasked_response: data.unmasked_response
                });

                // Switch to query tab
                switchTab('query');
            }
        })
        .catch(error => console.error('Error loading query detail:', error));
}

// =====================================================================
// UTILITY FUNCTIONS
// =====================================================================

function showLoadingSpinner(show) {
    const spinner = document.getElementById('loading-spinner');
    if (show) {
        spinner.style.display = 'flex';
    } else {
        spinner.style.display = 'none';
    }
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    
    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' :
                   type === 'danger' ? 'bg-danger' :
                   type === 'warning' ? 'bg-warning' : 'bg-info';
    
    const toastHTML = `
        <div id="${toastId}" class="toast show" role="alert">
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">
                    ${type === 'success' ? '✓' : type === 'danger' ? '✕' : 'ℹ'}
                    ${capitalizeFirst(type)}
                </strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${escapeHtml(message)}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // Auto-remove toast after 5 seconds
    setTimeout(() => {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.remove();
        }
    }, 5000);
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;

    // Use modern Clipboard API if available
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy:', err);
            fallbackCopy(text);
        });
    } else {
        fallbackCopy(text);
    }
}

function fallbackCopy(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    try {
        document.execCommand('copy');
        showToast('Copied to clipboard!', 'success');
    } catch (err) {
        showToast('Failed to copy', 'danger');
    }
    document.body.removeChild(textarea);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// =====================================================================
// KEYBOARD SHORTCUTS (Optional)
// =====================================================================

document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Enter to submit query
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        const queryForm = document.getElementById('query-form');
        if (queryForm && document.activeElement.id === 'query-input') {
            queryForm.dispatchEvent(new Event('submit'));
        }
    }
});

// =====================================================================
// INITIALIZE TOOLTIPS (Bootstrap)
// =====================================================================

window.addEventListener('load', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
