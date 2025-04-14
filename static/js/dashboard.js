/**
 * Dashboard JavaScript for ATS Resume Checker
 * This file handles the visualization and interactive elements on the dashboard page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Adjust score circle colors based on values
    const scoreElements = document.querySelectorAll('[id$="-score-circle"]');
    scoreElements.forEach(function(element) {
        const score = parseInt(element.textContent.trim());
        updateScoreColor(element, score);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    if (popoverTriggerList.length > 0) {
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl, {
                trigger: 'focus'
            });
        });
    }
});

/**
 * Updates the color of a score element based on the score value
 * @param {HTMLElement} element - The score element to update
 * @param {number} score - The score value
 */
function updateScoreColor(element, score) {
    if (score >= 80) {
        element.classList.add('bg-success-subtle', 'text-success', 'border-success');
    } else if (score >= 60) {
        element.classList.add('bg-warning-subtle', 'text-warning', 'border-warning');
    } else {
        element.classList.add('bg-danger-subtle', 'text-danger', 'border-danger');
    }
}

/**
 * Toggles the visibility of keyword details
 * @param {string} type - The type of keywords (matched or missing)
 */
function toggleKeywords(type) {
    const container = document.getElementById(`${type}-keywords-container`);
    const button = document.getElementById(`${type}-keywords-toggle`);
    
    if (container.style.display === 'none') {
        container.style.display = 'block';
        button.textContent = `Hide ${type === 'matched' ? 'Matched' : 'Missing'} Keywords`;
    } else {
        container.style.display = 'none';
        button.textContent = `Show ${type === 'matched' ? 'Matched' : 'Missing'} Keywords`;
    }
}

/**
 * Handles print preparation by expanding all collapsed elements
 */
function preparePrint() {
    // Expand all collapsed elements for printing
    document.querySelectorAll('.collapse').forEach(function(el) {
        const bsCollapse = new bootstrap.Collapse(el, {
            toggle: false
        });
        bsCollapse.show();
    });
    
    // Wait for animations to complete
    setTimeout(function() {
        window.print();
    }, 500);
}
