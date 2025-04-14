/**
 * Main JavaScript for ATS Resume Checker
 */

document.addEventListener('DOMContentLoaded', function() {
    // File upload validation
    const resumeInput = document.getElementById('resume');
    if (resumeInput) {
        resumeInput.addEventListener('change', function() {
            const fileSize = this.files[0].size / 1024 / 1024; // in MB
            const fileType = this.files[0].type;
            
            // Check file size (max 16MB)
            if (fileSize > 16) {
                alert('File size exceeds 16MB. Please upload a smaller file.');
                this.value = '';
                return;
            }
            
            // Check file type
            if (fileType !== 'application/pdf') {
                alert('Please upload a PDF file.');
                this.value = '';
                return;
            }
        });
    }
    
    // Job description form validation
    const analyzeForm = document.querySelector('form[action="/analyze"]');
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', function(e) {
            const jobDescription = document.getElementById('job_description').value.trim();
            
            if (jobDescription.length < 50) {
                e.preventDefault();
                alert('Please enter a more detailed job description (at least 50 characters).');
                return false;
            }
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
                submitButton.disabled = true;
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
