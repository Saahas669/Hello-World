// State management
let currentJobId = null;
let isPolling = false;

// DOM elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const selectBtn = document.getElementById('selectBtn');
const uploadSection = document.getElementById('uploadSection');
const progressSection = document.getElementById('progressSection');
const completionSection = document.getElementById('completionSection');
const errorSection = document.getElementById('errorSection');
const downloadBtn = document.getElementById('downloadBtn');
const convertAnotherBtn = document.getElementById('convertAnotherBtn');
const retryBtn = document.getElementById('retryBtn');

// Event listeners
uploadBox.addEventListener('click', () => fileInput.click());
uploadBox.addEventListener('dragover', handleDragOver);
uploadBox.addEventListener('dragleave', handleDragLeave);
uploadBox.addEventListener('drop', handleDrop);

selectBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);

downloadBtn.addEventListener('click', downloadFile);
convertAnotherBtn.addEventListener('click', resetForm);
retryBtn.addEventListener('click', resetForm);

// File upload handling
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadBox.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadBox.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadBox.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleFileSelect();
    }
}

function handleFileSelect() {
    const file = fileInput.files[0];
    
    if (!file) return;
    
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Please select a PDF file');
        return;
    }
    
    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showError('File is too large. Maximum size is 5MB');
        return;
    }
    
    uploadFile(file);
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Show progress section
    uploadSection.style.display = 'none';
    progressSection.style.display = 'flex';
    errorSection.style.display = 'none';
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Upload failed');
            });
        }
        return response.json();
    })
    .then(data => {
        currentJobId = data.job_id;
        startPolling();
    })
    .catch(error => {
        console.error('Upload error:', error);
        showError(error.message || 'Failed to upload file');
    });
}

function startPolling() {
    if (isPolling) return;
    isPolling = true;
    
    const pollInterval = setInterval(() => {
        fetchProgress(currentJobId)
            .then(data => {
                updateProgress(data);
                
                if (data.status === 'completed') {
                    clearInterval(pollInterval);
                    isPolling = false;
                    showCompletion();
                } else if (data.status === 'error') {
                    clearInterval(pollInterval);
                    isPolling = false;
                    showError(data.error || 'An error occurred during conversion');
                }
            })
            .catch(error => {
                console.error('Polling error:', error);
            });
    }, 500); // Poll every 500ms
}

function fetchProgress(jobId) {
    return fetch(`/progress/${jobId}`)
        .then(response => response.json());
}

function updateProgress(data) {
    // Update status text
    const statusMap = {
        'queued': 'Queued',
        'extracting': 'Extracting text from PDF...',
        'chunking': 'Preparing text chunks...',
        'converting': 'Converting to brainrot...',
        'generating': 'Generating PDF...',
        'completed': 'Conversion complete!',
        'error': 'Error occurred'
    };
    
    document.getElementById('statusText').textContent = statusMap[data.status] || data.status;
    document.getElementById('progressText').textContent = `${data.progress}%`;
    document.getElementById('progressFill').style.width = `${data.progress}%`;
    
    // Update chunk info if converting
    if (data.total_chunks > 0) {
        document.getElementById('chunkInfo').style.display = 'block';
        document.getElementById('chunkText').textContent = `${data.current_chunk}/${data.total_chunks}`;
    }
    
    // Update time estimate
    if (data.estimated_remaining > 0) {
        document.getElementById('timeInfo').style.display = 'block';
        document.getElementById('timeText').textContent = formatTime(data.estimated_remaining);
    }
    
    // Update details
    const detailsText = `${data.status} • ${data.progress}%`;
    document.getElementById('detailsText').textContent = detailsText;
}

function formatTime(seconds) {
    if (seconds < 60) {
        return `${Math.round(seconds)}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${minutes}m ${secs}s`;
}

function showCompletion() {
    progressSection.style.display = 'none';
    completionSection.style.display = 'flex';
    uploadSection.style.display = 'none';
    errorSection.style.display = 'none';
}

function showError(message) {
    progressSection.style.display = 'none';
    completionSection.style.display = 'none';
    uploadSection.style.display = 'none';
    errorSection.style.display = 'flex';
    
    document.getElementById('errorText').textContent = message;
}

function downloadFile() {
    if (!currentJobId) return;
    
    const link = document.createElement('a');
    link.href = `/download/${currentJobId}`;
    link.download = true;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function resetForm() {
    currentJobId = null;
    isPolling = false;
    fileInput.value = '';
    
    uploadSection.style.display = 'flex';
    progressSection.style.display = 'none';
    completionSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Reset progress elements
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('progressText').textContent = '0%';
    document.getElementById('statusText').textContent = 'Initializing...';
    document.getElementById('chunkInfo').style.display = 'none';
    document.getElementById('timeInfo').style.display = 'none';
    document.getElementById('detailsText').textContent = 'Starting conversion...';
}

// Initialize
console.log('Brainrot Converter loaded and ready!');
