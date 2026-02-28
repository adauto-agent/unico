const API_URL = window.location.origin;

let selectedFile = null;
let downloadUrl = null;

// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const extractBtn = document.getElementById('extractBtn');
const extractionRequest = document.getElementById('extractionRequest');
const selectedFileText = document.getElementById('selectedFileText');
const processingSection = document.getElementById('processingSection');
const previewSection = document.getElementById('previewSection');
const errorSection = document.getElementById('errorSection');
const configSection = document.getElementById('configSection');
const uploadSection = document.querySelector('.upload-section');
const savedConfigs = document.getElementById('savedConfigs');
const configName = document.getElementById('configName');
const logBox = document.getElementById('logBox');

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
        handleFileSelect(files[0]);
    }
});

// File input handler
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Handle file selection
function handleFileSelect(file) {
    if (file.type !== 'application/pdf') {
        showError('Vui lòng chọn file PDF');
        return;
    }

    selectedFile = file;
    selectedFileText.textContent = `📁 File đã chọn: ${file.name}`;
    checkExtractReady();
}

// Extraction request handler
extractionRequest.addEventListener('input', checkExtractReady);

function checkExtractReady() {
    if (selectedFile && extractionRequest.value.trim() !== '') {
        extractBtn.disabled = false;
    } else {
        extractBtn.disabled = true;
    }
}

// Execute extraction
async function extractData() {
    if (!selectedFile) return;

    // Show processing
    configSection.style.display = 'none';
    uploadSection.style.display = 'none';
    processingSection.style.display = 'block';
    errorSection.style.display = 'none';
    previewSection.style.display = 'none';

    // Clear logs
    logBox.innerHTML = '';
    updateProgress(0);
    
    addLog('info', `Bắt đầu xử lý file: ${selectedFile.name}`);
    addLog('info', `Yêu cầu: "${extractionRequest.value.trim()}"`);
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('request', extractionRequest.value.trim());

    try {
        updateProgress(10);
        addLog('info', '📤 Đang gửi yêu cầu lên server...');
        
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Xử lý thất bại');
        }

        updateProgress(50);
        addLog('success', '✓ Server đã nhận file và đang xử lý...');
        
        const data = await response.json();
        
        updateProgress(80);
        addLog('info', `🔍 Đã trích xuất ${data.items_count} dòng dữ liệu.`);
        
        // Setup download
        downloadUrl = `${API_URL}/download/${data.filename}`;
        
        // Show preview
        displayPreview(data.preview_data);
        
        updateProgress(100);
        addLog('success', '🎉 Hoàn tất! Bạn có thể xem trước kết quả bên dưới.');
        
        setTimeout(() => {
            processingSection.style.display = 'none';
            previewSection.style.display = 'block';
        }, 1000);

    } catch (error) {
        addLog('error', `❌ Lỗi: ${error.message}`);
        setTimeout(() => showError(error.message), 1000);
    }
}

// Display Preview Table
function displayPreview(previewData) {
    const tableHeader = document.getElementById('tableHeader');
    const tableBody = document.getElementById('tableBody');
    
    tableHeader.innerHTML = '';
    tableBody.innerHTML = '';

    if (!previewData || previewData.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="100%">Không có dữ liệu hiển thị</td></tr>';
        return;
    }

    // Headers
    const headers = Object.keys(previewData[0]);
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        tableHeader.appendChild(th);
    });

    // Rows (max 10)
    previewData.slice(0, 10).forEach(rowData => {
        const tr = document.createElement('tr');
        headers.forEach(header => {
            const td = document.createElement('td');
            td.textContent = rowData[header] || '';
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    });

    // Setup download button
    document.getElementById('downloadBtn').onclick = () => {
        window.location.href = downloadUrl;
    };
}

// --- Config Management ---
function saveConfig() {
    const name = configName.value.trim();
    const request = extractionRequest.value.trim();

    if (!name || !request) {
        alert('Vui lòng nhập tên và yêu cầu trích xuất');
        return;
    }

    const configs = JSON.parse(localStorage.getItem('unico_configs') || '{}');
    configs[name] = request;
    localStorage.setItem('unico_configs', JSON.stringify(configs));
    
    configName.value = '';
    loadConfigList();
    alert('Đã lưu cấu hình thành công!');
}

function loadConfigList() {
    const configs = JSON.parse(localStorage.getItem('unico_configs') || '{}');
    savedConfigs.innerHTML = '<option value="">-- Chọn cấu hình --</option>';
    
    Object.keys(configs).forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        savedConfigs.appendChild(option);
    });
}

function loadConfig() {
    const name = savedConfigs.value;
    if (!name) return;

    const configs = JSON.parse(localStorage.getItem('unico_configs') || '{}');
    extractionRequest.value = configs[name];
    checkExtractReady();
}

function deleteConfig() {
    const name = savedConfigs.value;
    if (!name) return;

    if (confirm(`Bạn có chắc muốn xóa cấu hình "${name}"?`)) {
        const configs = JSON.parse(localStorage.getItem('unico_configs') || '{}');
        delete configs[name];
        localStorage.setItem('unico_configs', JSON.stringify(configs));
        loadConfigList();
        extractionRequest.value = '';
        checkExtractReady();
    }
}

// --- Utils ---
function updateProgress(percent) {
    document.getElementById('progressFill').style.width = `${percent}%`;
    document.getElementById('progressPercent').textContent = `${percent}%`;
}

function addLog(type, message) {
    const timestamp = new Date().toLocaleTimeString('vi-VN');
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    entry.innerHTML = `<span class="log-time">[${timestamp}]</span> ${message}`;
    logBox.appendChild(entry);
    logBox.scrollTop = logBox.scrollHeight;
}

function showError(message) {
    processingSection.style.display = 'none';
    errorSection.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

// Init
loadConfigList();
