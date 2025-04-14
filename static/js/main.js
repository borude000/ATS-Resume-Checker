/**
 * Main JavaScript for ATS Resume Checker
 */

document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    setupThemeToggle();
    
    // Enhanced file upload and form submission
    setupEnhancedFileUpload();
    setupFormSubmission();
    
    // Job description form validation
    const analyzeForm = document.querySelector('form[action="/analyze"]');
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', function(e) {
            const jobDescription = document.getElementById('job_description').value.trim();
            
            if (jobDescription.length < 50) {
                e.preventDefault();
                showToast('Warning', 'Please enter a more detailed job description (at least 50 characters).', 'warning');
                return false;
            }
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
                submitButton.disabled = true;
                
                // Add a subtle pulsing effect to the button
                submitButton.classList.add('pulse-animation');
            }
            
            return true;
        });
    }
    
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
 * Enhance file input appearance
 * @param {HTMLElement} inputElement - The file input element
 */
function enhanceFileInput(inputElement) {
    const parentElement = inputElement.parentElement;
    
    if (parentElement && !parentElement.classList.contains('custom-file-upload')) {
        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'custom-file-upload mb-3';
        wrapper.innerHTML = `
            <div class="text-center">
                <i class="fas fa-file-pdf fa-2x mb-2 text-primary"></i>
                <p class="custom-file-label mb-0">Choose your resume (PDF)</p>
                <small class="form-text text-muted">Drag & drop or click to select</small>
            </div>
        `;
        
        // Setup drag and drop
        wrapper.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('border-primary');
        });
        
        wrapper.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('border-primary');
        });
        
        wrapper.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('border-primary');
            
            if (e.dataTransfer.files.length) {
                inputElement.files = e.dataTransfer.files;
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                inputElement.dispatchEvent(event);
            }
        });
        
        wrapper.addEventListener('click', function() {
            inputElement.click();
        });
        
        // Hide original input
        inputElement.style.display = 'none';
        
        // Insert wrapper before input
        parentElement.insertBefore(wrapper, inputElement);
    }
}

/**
 * Display a toast notification
 * @param {string} title - Toast title
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, danger, warning, info)
 */
function showToast(title, message, type) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // Create toast content
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}:</strong> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toastEl);
    
    // Initialize and show toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 5000
    });
    toast.show();
    
    // Remove toast element after it's hidden
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}
