// Global state
let currentColumns = [];
let isDataLoaded = false;

// Navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tool-section').forEach(s => s.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(btn.dataset.tool).classList.add('active');
    });
});

// Tabs
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const parent = btn.closest('.tool-section');
        parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        parent.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
    });
});

// Utility functions
function showLoading() {
    document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');
    
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}

async function apiCall(url, method = 'GET', data = null) {
    showLoading();
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        const result = await response.json();
        
        hideLoading();
        return result;
    } catch (error) {
        hideLoading();
        showNotification('Error: ' + error.message, 'error');
        return { success: false, error: error.message };
    }
}

function updateColumnSelects() {
    const selects = [
        'eda-column-select',
        'chart-x',
        'chart-y',
        'chart-color'
    ];
    
    selects.forEach(id => {
        const select = document.getElementById(id);
        if (select) {
            const currentValue = select.value;
            select.innerHTML = id === 'chart-color' ? '<option value="">None</option>' : '<option value="">Select a column...</option>';
            
            currentColumns.forEach(col => {
                const option = document.createElement('option');
                option.value = col;
                option.textContent = col;
                select.appendChild(option);
            });
            
            if (currentColumns.includes(currentValue)) {
                select.value = currentValue;
            }
        }
    });
}

function displayDataPreview(data, columns) {
    const preview = document.getElementById('data-preview');
    const thead = document.querySelector('#preview-table thead');
    const tbody = document.querySelector('#preview-table tbody');
    
    document.getElementById('row-count').textContent = `${data.length} rows (showing first 100)`;
    document.getElementById('col-count').textContent = `${columns.length} columns`;
    
    thead.innerHTML = '<tr>' + columns.map(col => `<th>${col}</th>`).join('') + '</tr>';
    
    tbody.innerHTML = data.slice(0, 100).map(row => 
        '<tr>' + columns.map(col => `<td>${row[col] !== null ? row[col] : ''}</td>`).join('') + '</tr>'
    ).join('');
    
    preview.classList.remove('hidden');
    currentColumns = columns;
    isDataLoaded = true;
    updateColumnSelects();
}

// File Upload
const fileInput = document.getElementById('file-input');
const dropzone = document.getElementById('dropzone');

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadDataFile(files[0]);
    }
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        uploadDataFile(fileInput.files[0]);
    }
});

async function uploadDataFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading();
    try {
        const response = await fetch('/api/data/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            showNotification(result.message, 'success');
            displayDataPreview(result.data, result.columns);
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showNotification('Upload failed: ' + error.message, 'error');
    }
}

// Snowflake
document.getElementById('snowflake-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    const result = await apiCall('/api/snowflake/connect', 'POST', data);
    const status = document.getElementById('snowflake-status');
    
    if (result.success) {
        status.className = 'status-message success';
        status.textContent = result.message;
        document.getElementById('snowflake-query-section').classList.remove('hidden');
    } else {
        status.className = 'status-message error';
        status.textContent = result.error || result.message;
    }
});

async function executeSnowflakeQuery() {
    const query = document.getElementById('snowflake-query').value;
    if (!query.trim()) {
        showNotification('Please enter a query', 'error');
        return;
    }
    
    const result = await apiCall('/api/snowflake/query', 'POST', { query });
    
    if (result.success) {
        showNotification(result.message, 'success');
        displayDataPreview(result.data, result.columns);
    } else {
        showNotification(result.error, 'error');
    }
}

// SQL Server
document.getElementById('sqlserver-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    const result = await apiCall('/api/sqlserver/connect', 'POST', data);
    const status = document.getElementById('sqlserver-status');
    
    if (result.success) {
        status.className = 'status-message success';
        status.textContent = result.message;
        document.getElementById('sqlserver-query-section').classList.remove('hidden');
    } else {
        status.className = 'status-message error';
        status.textContent = result.error || result.message;
    }
});

async function executeSQLServerQuery() {
    const query = document.getElementById('sqlserver-query').value;
    if (!query.trim()) {
        showNotification('Please enter a query', 'error');
        return;
    }
    
    const result = await apiCall('/api/sqlserver/query', 'POST', { query });
    
    if (result.success) {
        showNotification(result.message, 'success');
        displayDataPreview(result.data, result.columns);
    } else {
        showNotification(result.error, 'error');
    }
}

// PDF Upload
const pdfInput = document.getElementById('pdf-input');
const pdfDropzone = document.getElementById('pdf-dropzone');

pdfDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    pdfDropzone.classList.add('dragover');
});

pdfDropzone.addEventListener('dragleave', () => {
    pdfDropzone.classList.remove('dragover');
});

pdfDropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    pdfDropzone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    for (let file of files) {
        if (file.type === 'application/pdf') {
            uploadPDF(file);
        }
    }
});

pdfInput.addEventListener('change', () => {
    for (let file of pdfInput.files) {
        uploadPDF(file);
    }
});

async function uploadPDF(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading();
    try {
        const response = await fetch('/api/pdf/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            showNotification(result.message, 'success');
            refreshPDFList();
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showNotification('Upload failed: ' + error.message, 'error');
    }
}

async function refreshPDFList() {
    const result = await apiCall('/api/pdf/list');
    const list = document.getElementById('pdf-list');
    
    if (result.success) {
        list.innerHTML = result.documents.map(doc => 
            `<li>${doc} <button onclick="removePDF('${doc}')">&times;</button></li>`
        ).join('');
    }
}

async function clearPDFs() {
    const result = await apiCall('/api/pdf/clear', 'POST');
    if (result.success) {
        showNotification(result.message, 'success');
        refreshPDFList();
    }
}

async function setContext() {
    const result = await apiCall('/api/pdf/context');
    const status = document.getElementById('context-status');
    
    if (result.success) {
        status.className = 'status-message success';
        status.textContent = `Context set from ${result.documents_included.length} documents (${result.character_count} characters)`;
    } else {
        status.className = 'status-message error';
        status.textContent = result.error;
    }
}

// EDA Functions
async function getDataInfo() {
    if (!isDataLoaded) {
        showNotification('Please load data first', 'error');
        return;
    }
    
    const result = await apiCall('/api/eda/info');
    displayEDAResults('Dataset Information', result);
}

async function getStatistics() {
    if (!isDataLoaded) {
        showNotification('Please load data first', 'error');
        return;
    }
    
    const result = await apiCall('/api/eda/statistics');
    displayEDAResults('Statistical Summary', result);
}

async function getCorrelations() {
    if (!isDataLoaded) {
        showNotification('Please load data first', 'error');
        return;
    }
    
    const result = await apiCall('/api/eda/correlations');
    displayEDAResults('Correlation Analysis', result);
}

async function getDataQuality() {
    if (!isDataLoaded) {
        showNotification('Please load data first', 'error');
        return;
    }
    
    const result = await apiCall('/api/eda/quality');
    displayEDAResults('Data Quality Report', result);
}

async function getFullEDAReport() {
    if (!isDataLoaded) {
        showNotification('Please load data first', 'error');
        return;
    }
    
    const result = await apiCall('/api/eda/full_report');
    displayEDAResults('Full EDA Report', result);
}

async function getValueCounts() {
    const column = document.getElementById('eda-column-select').value;
    if (!column) {
        showNotification('Please select a column', 'error');
        return;
    }
    
    const result = await apiCall(`/api/eda/value_counts?column=${column}&top_n=20`);
    displayEDAResults(`Value Counts: ${column}`, result);
}

async function detectOutliers() {
    const column = document.getElementById('eda-column-select').value;
    if (!column) {
        showNotification('Please select a column', 'error');
        return;
    }
    
    const result = await apiCall(`/api/eda/outliers?column=${column}`);
    displayEDAResults(`Outlier Detection: ${column}`, result);
}

function displayEDAResults(title, result) {
    const container = document.getElementById('eda-results');
    
    if (result.success) {
        let content = `<h4>${title}</h4>`;
        content += `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        container.innerHTML = content;
    } else {
        container.innerHTML = `<div class="status-message error">${result.error}</div>`;
    }
}

// Chart Functions
async function createChart() {
    if (!isDataLoaded) {
        showNotification('Please load data first', 'error');
        return;
    }
    
    const chartType = document.getElementById('chart-type').value;
    const title = document.getElementById('chart-title').value || `${chartType} Chart`;
    const x = document.getElementById('chart-x').value;
    const y = document.getElementById('chart-y').value;
    const color = document.getElementById('chart-color').value;
    
    let data = { type: chartType, title };
    
    if (chartType === 'histogram') {
        data.column = x;
    } else if (chartType === 'heatmap') {
        // No additional params needed
    } else {
        data.x = x;
        data.y = y;
    }
    
    if (color) {
        data.color = color;
    }
    
    const result = await apiCall('/api/chart/create', 'POST', data);
    
    if (result.success && result.chart_json) {
        const chartData = JSON.parse(result.chart_json);
        Plotly.newPlot('chart-container', chartData.data, chartData.layout);
        showNotification(result.message, 'success');
    } else {
        showNotification(result.error || 'Failed to create chart', 'error');
    }
}

// Report Functions
async function generatePDFReport() {
    if (!isDataLoaded) {
        showNotification('Please load data first', 'error');
        return;
    }
    
    const title = document.getElementById('pdf-report-title').value;
    const includeData = document.getElementById('pdf-include-data').checked;
    const includeStats = document.getElementById('pdf-include-stats').checked;
    
    const result = await apiCall('/api/report/pdf', 'POST', {
        title,
        include_data: includeData,
        include_stats: includeStats
    });
    
    if (result.success) {
        showNotification(result.message, 'success');
        refreshReportsList();
    } else {
        showNotification(result.error, 'error');
    }
}

async function generateExcelReport() {
    if (!isDataLoaded) {
        showNotification('Please load data first', 'error');
        return;
    }
    
    const title = document.getElementById('excel-report-title').value;
    
    const result = await apiCall('/api/report/excel', 'POST', { title });
    
    if (result.success) {
        showNotification(result.message, 'success');
        refreshReportsList();
    } else {
        showNotification(result.error, 'error');
    }
}

async function exportCSV() {
    if (!isDataLoaded) {
        showNotification('Please load data first', 'error');
        return;
    }
    
    const result = await apiCall('/api/report/csv', 'POST', {});
    
    if (result.success) {
        showNotification(result.message, 'success');
        refreshReportsList();
    } else {
        showNotification(result.error, 'error');
    }
}

async function exportJSON() {
    if (!isDataLoaded) {
        showNotification('Please load data first', 'error');
        return;
    }
    
    const result = await apiCall('/api/report/json', 'POST', {});
    
    if (result.success) {
        showNotification(result.message, 'success');
        refreshReportsList();
    } else {
        showNotification(result.error, 'error');
    }
}

async function refreshReportsList() {
    const result = await apiCall('/api/report/list');
    const list = document.getElementById('reports-list');
    
    if (result.success) {
        list.innerHTML = result.reports.map(report => 
            `<li>
                <a href="/api/report/download/${report.filename}" download>${report.filename}</a>
                <span>${(report.size / 1024).toFixed(1)} KB</span>
            </li>`
        ).join('');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    refreshPDFList();
    refreshReportsList();
});
