// File upload handling
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');
const reportSection = document.getElementById('reportSection');
const generateReportBtn = document.getElementById('generateReportBtn');
const createSamplesBtn = document.getElementById('createSamplesBtn');
const clearSessionBtn = document.getElementById('clearSessionBtn');
const reportStatus = document.getElementById('reportStatus');

// Drag and drop
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});
uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Handle file upload and analysis
async function handleFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Show loading
    resultsContainer.innerHTML = '<div class="loading">Analyzing file</div>';
    resultsSection.style.display = 'block';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displayResults(data.analysis);
            reportSection.style.display = 'block';
        } else {
            resultsContainer.innerHTML = `<div class="error-message">Error: ${data.error || 'Analysis failed'}</div>`;
        }
    } catch (error) {
        resultsContainer.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
    }
}

// Display analysis results
function displayResults(analysis) {
    const fileType = analysis.image_info ? 'image' : 
                     analysis.audio_info ? 'audio' : 
                     analysis.video_info ? 'video' : 'unknown';

    let html = `
        <div class="result-card">
            <div class="result-header">
                <div class="result-title">📄 ${analysis.original_filename || 'File'}</div>
            </div>
            <div class="file-info">
    `;

    // File info
    if (analysis.image_info) {
        html += `
            <p><strong>Type:</strong> Image</p>
            <p><strong>Dimensions:</strong> ${analysis.image_info.width} × ${analysis.image_info.height}</p>
            <p><strong>Channels:</strong> ${analysis.image_info.channels}</p>
            <p><strong>Format:</strong> ${analysis.image_info.format || 'N/A'}</p>
        `;
    } else if (analysis.audio_info) {
        html += `
            <p><strong>Type:</strong> Audio</p>
            <p><strong>Sample Rate:</strong> ${analysis.audio_info.sample_rate} Hz</p>
            <p><strong>Channels:</strong> ${analysis.audio_info.channels}</p>
            <p><strong>Duration:</strong> ${analysis.audio_info.duration.toFixed(2)} seconds</p>
        `;
    } else if (analysis.video_info) {
        html += `
            <p><strong>Type:</strong> Video</p>
            <p><strong>Dimensions:</strong> ${analysis.video_info.width} × ${analysis.video_info.height}</p>
            <p><strong>FPS:</strong> ${analysis.video_info.fps}</p>
            <p><strong>Duration:</strong> ${analysis.video_info.duration.toFixed(2)} seconds</p>
        `;
    }

    html += `</div>`;

    // Detection results
    html += `<h3 style="margin-top: 20px; color: #667eea;">Detection Results</h3>`;

    // LSB Detection
    if (analysis.lsb_detection) {
        const lsb = analysis.lsb_detection;
        const status = lsb.detected ? 'detected' : 'not-detected';
        const statusText = lsb.detected ? '✓ DETECTED' : '✗ NOT DETECTED';
        html += `
            <div class="detection-result">
                <div class="detection-method">${lsb.method}</div>
                <div class="status ${status}">${statusText}</div>
                ${lsb.detected ? `<div class="confidence">Confidence: ${lsb.confidence.toFixed(2)}%</div>` : ''}
                ${lsb.details ? formatDetails(lsb.details) : ''}
            </div>
        `;
    }

    // DCT Detection
    if (analysis.dct_detection) {
        const dct = analysis.dct_detection;
        const status = dct.detected ? 'detected' : 'not-detected';
        const statusText = dct.detected ? '✓ DETECTED' : '✗ NOT DETECTED';
        html += `
            <div class="detection-result">
                <div class="detection-method">${dct.method}</div>
                <div class="status ${status}">${statusText}</div>
                ${dct.detected ? `<div class="confidence">Confidence: ${dct.confidence.toFixed(2)}%</div>` : ''}
                ${dct.details ? formatDetails(dct.details) : ''}
            </div>
        `;
    }

    // Phase Detection
    if (analysis.phase_detection) {
        const phase = analysis.phase_detection;
        const status = phase.detected ? 'detected' : 'not-detected';
        const statusText = phase.detected ? '✓ DETECTED' : '✗ NOT DETECTED';
        html += `
            <div class="detection-result">
                <div class="detection-method">${phase.method}</div>
                <div class="status ${status}">${statusText}</div>
                ${phase.detected ? `<div class="confidence">Confidence: ${phase.confidence.toFixed(2)}%</div>` : ''}
                ${phase.details ? formatDetails(phase.details) : ''}
            </div>
        `;
    }

    // Frame Analysis
    if (analysis.frame_analysis) {
        const frame = analysis.frame_analysis;
        const status = frame.detected ? 'detected' : 'not-detected';
        const statusText = frame.detected ? '✓ DETECTED' : '✗ NOT DETECTED';
        html += `
            <div class="detection-result">
                <div class="detection-method">${frame.method}</div>
                <div class="status ${status}">${statusText}</div>
                ${frame.detected ? `<div class="confidence">Confidence: ${frame.confidence.toFixed(2)}%</div>` : ''}
                ${frame.details ? formatDetails(frame.details) : ''}
            </div>
        `;
    }

    // Extraction results
    if (analysis.extraction && Object.keys(analysis.extraction).length > 0) {
        html += `<h3 style="margin-top: 20px; color: #667eea;">Extraction Results</h3>`;
        for (const [method, result] of Object.entries(analysis.extraction)) {
            if (result.extracted) {
                html += `
                    <div class="extraction-result">
                        <div class="detection-method">${result.method}</div>
                        <p><strong>Extracted:</strong> Yes</p>
                        ${result.data ? `<div class="extracted-data">${escapeHtml(result.data)}</div>` : ''}
                        ${result.details ? formatDetails(result.details) : ''}
                    </div>
                `;
            }
        }
    }

    html += `</div>`;
    resultsContainer.innerHTML = html;
}

function formatDetails(details) {
    if (!details || Object.keys(details).length === 0) return '';
    
    let html = '<table class="details-table">';
    for (const [key, value] of Object.entries(details)) {
        const displayValue = typeof value === 'number' ? value.toFixed(4) : value;
        html += `<tr><td>${key}</td><td>${displayValue}</td></tr>`;
    }
    html += '</table>';
    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Generate report
generateReportBtn.addEventListener('click', async () => {
    reportStatus.innerHTML = '<div class="loading">Generating report</div>';
    
    try {
        const response = await fetch('/generate_report', {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            reportStatus.innerHTML = `
                <div class="success-message">
                    Report generated successfully!
                    <br><br>
                    <a href="/download_report/${data.report_filename}" class="btn btn-primary" style="text-decoration: none; display: inline-block; margin-top: 10px;">
                        Download Report
                    </a>
                </div>
            `;
        } else {
            reportStatus.innerHTML = `<div class="error-message">Error: ${data.error || 'Report generation failed'}</div>`;
        }
    } catch (error) {
        reportStatus.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
    }
});

// Create sample files
createSamplesBtn.addEventListener('click', async () => {
    createSamplesBtn.disabled = true;
    createSamplesBtn.textContent = 'Creating samples...';
    
    try {
        const response = await fetch('/create_samples', {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            alert('Sample files created successfully! You can now analyze them.');
            // Optionally load the sample files
            window.location.reload();
        } else {
            alert(`Error: ${data.error || 'Sample creation failed'}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        createSamplesBtn.disabled = false;
        createSamplesBtn.textContent = 'Create Sample Files';
    }
});

// Clear session
clearSessionBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/clear_session', {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            resultsSection.style.display = 'none';
            reportSection.style.display = 'none';
            resultsContainer.innerHTML = '';
            reportStatus.innerHTML = '';
            alert('Session cleared successfully!');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
});

