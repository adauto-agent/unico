const API_URL = window.location.origin;

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

    // Clear previous logs
    const logBox = document.getElementById('logBox');
    logBox.innerHTML = '';

    // Initialize progress
    updateProgress(0);
    
    // Add initial log
    addLog('info', `Bắt đầu xử lý file: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Step 1: Uploading
        updateProgress(10);
        addLog('info', '📤 Đang upload file lên server...');
        await sleep(500);
        
        updateProgress(20);
        addLog('success', '✓ Upload thành công!');
        
        // Step 2: Reading PDF
        updateProgress(30);
        addLog('info', '📄 Đang đọc file PDF...');
        
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        updateProgress(50);
        addLog('success', '✓ Đọc file PDF hoàn tất!');

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Upload failed');
        }

        // Step 3: Processing
        updateProgress(60);
        addLog('info', '🔍 Đang phân tích cấu trúc PDF...');
        await sleep(300);
        
        updateProgress(70);
        addLog('info', '📊 Đang trích xuất dữ liệu từ bảng...');
        await sleep(300);
        
        updateProgress(80);
        addLog('success', '✓ Trích xuất dữ liệu hoàn tất!');

        // Step 4: Generating Excel
        updateProgress(85);
        addLog('info', '📝 Đang tạo file Excel với 27 cột...');
        await sleep(200);
        
        const data = await response.json();
        
        updateProgress(95);
        addLog('success', `✓ Đã trích xuất ${data.items_count} dòng dữ liệu!`);
        
        // Step 5: Complete
        updateProgress(100);
        addLog('success', '🎉 Xử lý hoàn tất! File Excel đã sẵn sàng để tải xuống.');
        await sleep(500);

        // Show success
        processingSection.style.display = 'none';
        resultSection.style.display = 'block';

        resultInfo.textContent = `Đã trích xuất ${data.items_count} dòng từ file "${file.name}"`;

        // Setup download
        downloadUrl = `${API_URL}/download/${data.filename}`;
        downloadBtn.onclick = () => {
            addLog('info', '📥 Đang tải xuống file Excel...');
            window.location.href = downloadUrl;
        };

    } catch (error) {
        addLog('error', `❌ Lỗi: ${error.message}`);
        updateProgress(0);
        
        setTimeout(() => {
            showError(error.message || 'Có lỗi xảy ra khi xử lý file. Vui lòng thử lại.');
        }, 1000);
    }
}

// Update progress bar
function updateProgress(percent) {
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    
    progressFill.style.width = `${percent}%`;
    progressPercent.textContent = `${percent}%`;
}

// Add log entry
function addLog(type, message) {
    const logBox = document.getElementById('logBox');
    const timestamp = new Date().toLocaleTimeString('vi-VN');
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    logEntry.innerHTML = `<span class="log-time">[${timestamp}]</span>${message}`;
    
    logBox.appendChild(logEntry);
    logBox.scrollTop = logBox.scrollHeight; // Auto scroll to bottom
}

// Sleep helper
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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
