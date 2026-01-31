// Visual Search Engine - JavaScript

const API_BASE = '/api';

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadStatus();
    loadDefaultDirectories();
    // Poll status every 5 seconds when indexing
    setInterval(checkIndexingStatus, 5000);
});

// Load current status
async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        updateStatusBar(data);
    } catch (error) {
        console.error('Error loading status:', error);
        document.getElementById('statusMessage').textContent = 'Error loading status';
    }
}

// Update status bar
function updateStatusBar(data) {
    const statusMessage = document.getElementById('statusMessage');
    const indexStats = document.getElementById('indexStats');
    
    if (data.indexing_status) {
        statusMessage.textContent = data.indexing_status.message;
    }
    
    if (data.index_stats) {
        indexStats.innerHTML = `
            📊 ${data.index_stats.total_images} images indexed |
            💾 ${data.index_stats.total_size_mb || 0} MB |
            📝 ${data.index_stats.unique_words || 0} unique words
        `;
    }
}

// Check indexing status
async function checkIndexingStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        if (data.indexing_status && data.indexing_status.is_indexing) {
            showProgress(data.indexing_status);
        } else {
            hideProgress();
        }
        
        updateStatusBar(data);
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// Load default directories
function loadDefaultDirectories() {
    const textarea = document.getElementById('directories');
    textarea.value = './sample_images';
}

// Build index
async function buildIndex() {
    const directoriesText = document.getElementById('directories').value;
    const directories = directoriesText.split('\n').filter(d => d.trim());
    
    if (directories.length === 0) {
        alert('Please enter at least one directory to scan');
        return;
    }
    
    const btn = document.getElementById('indexBtn');
    btn.disabled = true;
    btn.textContent = 'Indexing...';
    
    showProgress({ message: 'Starting...', progress: 0, total: 0 });
    
    try {
        const response = await fetch(`${API_BASE}/index`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ directories })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('success', `Successfully indexed ${data.indexed_images} images!`);
            loadStatus();
        } else {
            showAlert('error', `Error: ${data.error || 'Failed to build index'}`);
        }
    } catch (error) {
        console.error('Error building index:', error);
        showAlert('error', `Error: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Build Index';
        hideProgress();
    }
}

// Show progress
function showProgress(status) {
    const container = document.getElementById('indexProgress');
    const fill = document.getElementById('progressFill');
    const text = document.getElementById('progressText');
    
    container.style.display = 'block';
    
    const percent = status.total > 0 ? (status.progress / status.total * 100) : 0;
    fill.style.width = `${percent}%`;
    text.textContent = status.message || 'Processing...';
}

// Hide progress
function hideProgress() {
    const container = document.getElementById('indexProgress');
    container.style.display = 'none';
}

// Switch tabs
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}Tab`).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Preview image
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Search visual
async function searchVisual() {
    const fileInput = document.getElementById('visualImage');
    const topK = document.getElementById('visualTopK').value;
    
    if (!fileInput.files || !fileInput.files[0]) {
        alert('Please select an image');
        return;
    }
    
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('top_k', topK);
    
    await performSearch(`${API_BASE}/search/visual`, formData, 'POST');
}

// Search text
async function searchText() {
    const query = document.getElementById('textQuery').value;
    const maxResults = document.getElementById('textMaxResults').value;
    
    if (!query.trim()) {
        alert('Please enter a search query');
        return;
    }
    
    await performSearch(`${API_BASE}/search/text`, {
        query: query,
        max_results: parseInt(maxResults)
    }, 'POST', true);
}

// Search hybrid
async function searchHybrid() {
    const fileInput = document.getElementById('hybridImage');
    const query = document.getElementById('hybridQuery').value;
    const topK = document.getElementById('hybridTopK').value;
    
    if (!fileInput.files[0] && !query.trim()) {
        alert('Please provide at least an image or text query');
        return;
    }
    
    const formData = new FormData();
    if (fileInput.files[0]) {
        formData.append('image', fileInput.files[0]);
    }
    if (query.trim()) {
        formData.append('query', query);
    }
    formData.append('top_k', topK);
    
    await performSearch(`${API_BASE}/search/hybrid`, formData, 'POST');
}

// Perform search
async function performSearch(url, data, method = 'POST', isJSON = false) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsGrid = document.getElementById('resultsGrid');
    const resultsInfo = document.getElementById('resultsInfo');
    
    // Show loading
    resultsSection.style.display = 'block';
    resultsGrid.innerHTML = '<p>Searching...</p>';
    
    try {
        const options = {
            method: method,
        };
        
        if (isJSON) {
            options.headers = {
                'Content-Type': 'application/json',
            };
            options.body = JSON.stringify(data);
        } else {
            options.body = data;
        }
        
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (response.ok) {
            displayResults(result);
        } else {
            resultsGrid.innerHTML = `<p class="alert alert-error">${result.error || 'Search failed'}</p>`;
        }
    } catch (error) {
        console.error('Error performing search:', error);
        resultsGrid.innerHTML = `<p class="alert alert-error">Error: ${error.message}</p>`;
    }
}

// Display results
function displayResults(data) {
    const resultsGrid = document.getElementById('resultsGrid');
    const resultsInfo = document.getElementById('resultsInfo');
    const resultsSection = document.getElementById('resultsSection');
    
    resultsSection.style.display = 'block';
    
    if (!data.results || data.results.length === 0) {
        resultsGrid.innerHTML = '<p>No results found</p>';
        resultsInfo.innerHTML = '';
        return;
    }
    
    resultsInfo.innerHTML = `<p class="alert alert-success">Found ${data.count} results</p>`;
    
    resultsGrid.innerHTML = '';
    
    data.results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'result-item';
        
        let badges = '';
        if (result.match_type === 'visual' || result.visual_score) {
            badges += `<span class="match-badge match-visual">Visual</span>`;
        }
        if (result.match_type === 'text' || result.text_match) {
            badges += `<span class="match-badge match-text">Text</span>`;
        }
        
        const similarity = result.similarity ? 
            `<p class="result-similarity">Similarity: ${(result.similarity * 100).toFixed(1)}%</p>` : '';
        
        const ocrText = result.ocr_text ? 
            `<p class="result-text">${result.ocr_text.substring(0, 100)}${result.ocr_text.length > 100 ? '...' : ''}</p>` : '';
        
        item.innerHTML = `
            <img src="${API_BASE}/image/${encodeURIComponent(result.path)}" 
                 alt="${result.filename}" 
                 class="result-image"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22%3EImage not found%3C/text%3E%3C/svg%3E'">
            <div class="result-info">
                <p class="result-filename">${result.filename}</p>
                ${badges}
                ${similarity}
                ${ocrText}
            </div>
        `;
        
        resultsGrid.appendChild(item);
    });
}

// Show alert
function showAlert(type, message) {
    const alertClass = type === 'success' ? 'alert-success' : 
                       type === 'error' ? 'alert-error' : 'alert-info';
    
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass}`;
    alert.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alert, container.firstChild);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}
