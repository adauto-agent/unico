const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : window.location.origin + '/api';

let selectedFile = null;

// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const processingSection = document.getElementById('processingSection');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const resultInfo = document.getElementById('resultInfo');
const errorMessage = document.getElementById('errorMessage');
const downloadBtn = document.getElementById('downloadBtn');

let downloadUrl = null;

// Drag and drop handlers
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('dragover');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('dragover');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// File input handler
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Handle selected file
function handleFile(file) {
    if (file.type !== 'application/pdf') {
        showError('Vui lòng chọn file PDF');
        return;
    }

    selectedFile = file;
    uploadFile(file);
}

// Upload file to backend
async function uploadFile(file) {
    // Show processing
    uploadBox.parentElement.style.display = 'none';
    processingSection.style.display = 'block';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Upload failed');
        }

        const data = await response.json();

        // Show success
        processingSection.style.display = 'none';
        resultSection.style.display = 'block';

        resultInfo.textContent = `Đã trích xuất ${data.items_count} dòng từ file "${file.name}"`;

        // Setup download
        downloadUrl = `${API_URL}/download/${data.filename}`;
        downloadBtn.onclick = () => {
            window.location.href = downloadUrl;
        };

    } catch (error) {
        showError(error.message || 'Có lỗi xảy ra khi xử lý file. Vui lòng thử lại.');
    }
}

// Show error
function showError(message) {
    uploadBox.parentElement.style.display = 'none';
    processingSection.style.display = 'none';
    resultSection.style.display = 'none';
    errorSection.style.display = 'block';

    errorMessage.textContent = message;
}

// Health check
async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (!response.ok) {
            console.warn('Backend health check failed');
        }
    } catch (error) {
        console.warn('Cannot connect to backend');
    }
}

// Check health on load
checkHealth();
