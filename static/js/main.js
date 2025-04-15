// Main JavaScript functionality for Job Tracker application

document.addEventListener('DOMContentLoaded', function() {
    // Enable all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Job status update confirmation
    const statusSelects = document.querySelectorAll('select[name="status"]');
    statusSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            if (form && this.value) {
                form.submit();
            }
        });
    });

    // Apply date handling - show/hide based on status
    const statusSelect = document.getElementById('status');
    const dateAppliedGroup = document.getElementById('date_applied_group');
    
    if (statusSelect && dateAppliedGroup) {
        const handleStatusChange = function() {
            const status = statusSelect.value;
            if (status === 'Applied' || status === 'Phone Interview' || 
                status === 'Technical Interview' || status === 'Onsite Interview' || 
                status === 'Offer' || status === 'Rejected') {
                dateAppliedGroup.style.display = 'block';
            } else {
                dateAppliedGroup.style.display = 'none';
            }
        };
        
        statusSelect.addEventListener('change', handleStatusChange);
        // Run once on page load
        handleStatusChange();
    }

    // Handle job description formatting
    const jobDescriptionContainer = document.querySelector('.job-description');
    if (jobDescriptionContainer) {
        // Ensure proper line breaks and spacing
        const content = jobDescriptionContainer.querySelector('div');
        if (content) {
            content.style.whiteSpace = 'pre-wrap';
        }
    }
});

// Function to confirm deletion
function confirmDelete(formId) {
    if (confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        document.getElementById(formId).submit();
    }
    return false;
}

// Function to copy job URL to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('URL copied to clipboard!');
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}
