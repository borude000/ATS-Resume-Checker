/**
 * Main JavaScript for ATS Resume Checker
 */

document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    setupThemeToggle();
    
    // Enhanced file upload and form submission
    setupEnhancedFileUpload();
    setupFormSubmission();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

/**
 * Setup theme toggle functionality
 */
function setupThemeToggle() {
    // Check for saved theme preference or use device preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const defaultTheme = savedTheme || (prefersDark ? 'dark' : 'light');
    
    // Apply the theme
    document.documentElement.setAttribute('data-bs-theme', defaultTheme);
    
    // Add the theme toggle to the navbar
    const navbarNav = document.querySelector('.navbar-nav');
    if (navbarNav) {
        const themeToggleLi = document.createElement('li');
        themeToggleLi.className = 'nav-item ms-2 d-flex align-items-center';
        
        const themeToggle = document.createElement('div');
        themeToggle.className = 'theme-toggle';
        themeToggle.innerHTML = defaultTheme === 'dark' ? 
            '<i class="fas fa-sun text-warning"></i>' : 
            '<i class="fas fa-moon text-white"></i>';
        themeToggle.setAttribute('title', defaultTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode');
        themeToggle.setAttribute('data-bs-toggle', 'tooltip');
        themeToggle.setAttribute('data-bs-placement', 'bottom');
        
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Update the theme
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update the icon
            this.innerHTML = newTheme === 'dark' ? 
                '<i class="fas fa-sun text-warning"></i>' : 
                '<i class="fas fa-moon text-white"></i>';
            this.setAttribute('title', newTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode');
            
            // Update the tooltip
            const tooltip = bootstrap.Tooltip.getInstance(this);
            if (tooltip) {
                tooltip.dispose();
            }
            new bootstrap.Tooltip(this);
        });
        
        themeToggleLi.appendChild(themeToggle);
        navbarNav.appendChild(themeToggleLi);
        
        // Initialize tooltip
        new bootstrap.Tooltip(themeToggle);
    }
}

/**
 * Setup enhanced file upload with visual feedback
 */
function setupEnhancedFileUpload() {
    const fileInput = document.getElementById('resume');
    if (!fileInput) return;
    
    const filePlaceholder = document.getElementById('file-placeholder');
    const filePreview = document.getElementById('file-preview');
    const fileName = document.getElementById('file-name');
    const fileUpload = document.querySelector('.custom-file-upload');
    
    if (!filePlaceholder || !filePreview || !fileName || !fileUpload) return;
    
    // Handle file selection
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            
            // Check if it's a PDF
            if (file.type === 'application/pdf') {
                // Show selected file name
                fileName.textContent = file.name;
                
                // Switch from placeholder to preview
                filePlaceholder.classList.add('d-none');
                filePreview.classList.remove('d-none');
                
                // Show feedback
                document.getElementById('submit-status').innerHTML = 
                    `<span class="text-success">✓ File selected: ${file.name}</span>`;
                
                // Show toast
                showToast('File Selected', `${file.name} selected successfully`, 'success');
            } else {
                // Reset if not PDF
                this.value = '';
                showToast('Invalid File', 'Please select a PDF file', 'danger');
                document.getElementById('submit-status').innerHTML = 
                    '<span class="text-danger">⚠️ Please select a PDF file</span>';
            }
        }
    });
    
    // Setup drag and drop
    fileUpload.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.style.borderColor = 'var(--green-primary)';
        this.style.backgroundColor = 'rgba(46, 204, 113, 0.1)';
    });
    
    fileUpload.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.style.borderColor = 'var(--green-light)';
        this.style.backgroundColor = 'rgba(46, 204, 113, 0.05)';
    });
    
    fileUpload.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        this.style.borderColor = 'var(--green-light)';
        this.style.backgroundColor = 'rgba(46, 204, 113, 0.05)';
        
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            
            // Trigger change event
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    });
    
    // Make the custom upload clickable
    fileUpload.addEventListener('click', function() {
        fileInput.click();
    });
}

/**
 * Setup form submission with loading indicators
 */
function setupFormSubmission() {
    const form = document.querySelector('form[action="/analyze"]');
    if (!form) return;
    
    const submitBtn = document.getElementById('submit-btn');
    const submitText = document.getElementById('submit-text');
    const loadingSpinner = document.getElementById('loading-spinner');
    const submitStatus = document.getElementById('submit-status');
    
    if (!submitBtn || !submitText || !loadingSpinner) return;
    
    form.addEventListener('submit', function(e) {
        // Validate file input
        const fileInput = document.getElementById('resume');
        if (!fileInput.files || !fileInput.files[0]) {
            e.preventDefault();
            showToast('Error', 'Please select a resume file', 'danger');
            submitStatus.innerHTML = '<span class="text-danger">⚠️ Please select a resume file</span>';
            return false;
        }
        
        // Validate job description
        const jobDescription = document.getElementById('job_description');
        if (!jobDescription.value.trim()) {
            e.preventDefault();
            showToast('Error', 'Please enter a job description', 'danger');
            submitStatus.innerHTML = '<span class="text-danger">⚠️ Please enter a job description</span>';
            return false;
        }
        
        // If validation passes, show loading state
        submitBtn.disabled = true;
        submitText.textContent = 'Analyzing...';
        loadingSpinner.classList.remove('d-none');
        submitStatus.innerHTML = '<span class="text-primary">⏳ Analyzing your resume, please wait...</span>';
        
        return true;
    });
}

/**
 * Display a toast notification
 * @param {string} title - Toast title
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, danger, warning, info)
 */
function showToast(title, message, type) {
    // Try to use existing toast if available
    let toastEl = document.getElementById('notificationToast');
    
    if (toastEl) {
        // Update existing toast
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');
        const toastTime = document.getElementById('toastTime');
        
        if (toastTitle) toastTitle.textContent = title;
        if (toastMessage) toastMessage.textContent = message;
        if (toastTime) toastTime.textContent = 'Just now';
        
        // Update toast color
        toastEl.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info');
        toastEl.classList.add(`bg-${type}`);
    } else {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        toastEl = document.createElement('div');
        toastEl.id = 'notificationToast';
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        // Create toast content
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <span id="toastTitle" class="fw-bold">${title}:</span> 
                    <span id="toastMessage">${message}</span>
                    <small id="toastTime" class="d-none">Just now</small>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add toast to container
        toastContainer.appendChild(toastEl);
    }
    
    // Initialize and show toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 5000
    });
    toast.show();
}
