// Main JavaScript file for Secure File Transfer Application

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApplication();
});

/**
 * Initialize the application
 */
function initializeApplication() {
    setupFileUploadHandlers();
    setupFormValidation();
    setupTooltips();
    setupAutoHideAlerts();
}

/**
 * Setup file upload handlers with drag and drop
 */
function setupFileUploadHandlers() {
    const fileInput = document.getElementById('file');
    if (!fileInput) return;

    const uploadForm = document.getElementById('uploadForm');
    if (!uploadForm) return;

    // Create drag and drop zone
    createDragDropZone(fileInput);
    
    // File input change handler
    fileInput.addEventListener('change', handleFileSelection);
    
    // Form submission handler
    uploadForm.addEventListener('submit', handleFormSubmission);
}

/**
 * Create drag and drop functionality
 */
function createDragDropZone(fileInput) {
    const dropZone = document.createElement('div');
    dropZone.className = 'file-drop-zone mt-3';
    dropZone.innerHTML = `
        <div>
            <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
            <p class="mb-2">Drag and drop your file here</p>
            <p class="text-muted small">or click to browse</p>
        </div>
    `;
    
    // Insert after file input
    fileInput.parentNode.insertBefore(dropZone, fileInput.nextSibling);
    
    // Event listeners
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('drop', handleDrop);
    dropZone.addEventListener('dragleave', handleDragLeave);

    function handleDragOver(e) {
        e.preventDefault();
        dropZone.classList.add('dragover');
    }

    function handleDrop(e) {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelection({ target: fileInput });
        }
    }

    function handleDragLeave(e) {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    }
}

/**
 * Handle file selection
 */
function handleFileSelection(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
        showAlert('File size exceeds 50MB limit. Please choose a smaller file.', 'error');
        e.target.value = '';
        return;
    }

    // Update UI with file info
    updateFileInfo(file);
}

/**
 * Update file information display
 */
function updateFileInfo(file) {
    const fileSize = (file.size / 1024 / 1024).toFixed(2);
    const fileType = file.type || 'Unknown';
    
    // Create or update file info display
    let fileInfo = document.getElementById('file-info');
    if (!fileInfo) {
        fileInfo = document.createElement('div');
        fileInfo.id = 'file-info';
        fileInfo.className = 'alert alert-info mt-3';
        
        const fileInput = document.getElementById('file');
        fileInput.parentNode.appendChild(fileInfo);
    }
    
    fileInfo.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-file me-3"></i>
            <div>
                <strong>${file.name}</strong><br>
                <small class="text-muted">Size: ${fileSize} MB | Type: ${fileType}</small>
            </div>
        </div>
    `;
}

/**
 * Handle form submission
 */
function handleFormSubmission(e) {
    const fileInput = document.getElementById('file');
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        e.preventDefault();
        showAlert('Please select a file to upload.', 'error');
        return;
    }
    
    // Show loading state
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Uploading...';
        submitBtn.classList.add('btn-loading');
    }
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                showAlert('Please fill in all required fields correctly.', 'error');
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Setup tooltips
 */
function setupTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup auto-hide alerts
 */
function setupAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
            setTimeout(() => {
                fadeOut(alert);
            }, 5000);
        }
    });
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main container
    const main = document.querySelector('main.container');
    if (main) {
        main.insertBefore(alertContainer, main.firstChild);
    }
    
    // Auto-hide success and info alerts
    if (type === 'success' || type === 'info') {
        setTimeout(() => fadeOut(alertContainer), 5000);
    }
}

/**
 * Get appropriate icon for alert type
 */
function getAlertIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Fade out element
 */
function fadeOut(element) {
    element.style.transition = 'opacity 0.5s ease';
    element.style.opacity = '0';
    setTimeout(() => {
        if (element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }, 500);
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy to clipboard:', err);
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

/**
 * Fallback copy to clipboard for older browsers
 */
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showAlert('Copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy to clipboard:', err);
        showAlert('Failed to copy to clipboard', 'error');
    }
    
    document.body.removeChild(textArea);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Loading state utilities
 */
const LoadingState = {
    show: function(element, text = 'Loading...') {
        if (element) {
            element.disabled = true;
            element.dataset.originalText = element.innerHTML;
            element.innerHTML = `<i class="fas fa-spinner fa-spin me-1"></i>${text}`;
            element.classList.add('btn-loading');
        }
    },
    
    hide: function(element) {
        if (element && element.dataset.originalText) {
            element.disabled = false;
            element.innerHTML = element.dataset.originalText;
            element.classList.remove('btn-loading');
            delete element.dataset.originalText;
        }
    }
};

// Global utilities
window.showAlert = showAlert;
window.copyToClipboard = copyToClipboard;
window.formatFileSize = formatFileSize;
window.formatDate = formatDate;
window.LoadingState = LoadingState;
