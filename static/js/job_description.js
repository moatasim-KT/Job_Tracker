/**
 * Job description display functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Job description JS loaded");
    
    // Initialize Bootstrap tabs for job description
    // Give the DOM a moment to fully initialize with Bootstrap components
    setTimeout(function() {
        console.log("Initializing job description tabs");
        
        // Get all tab elements
        const tabNavs = document.querySelectorAll('#jobDescriptionTabs button[data-bs-toggle="tab"]');
        console.log(`Found ${tabNavs.length} tab navigation elements`);
        
        if (tabNavs.length > 0) {
            // Handle tab clicks manually
            tabNavs.forEach(tabNav => {
                console.log(`Setting up tab: ${tabNav.id} -> ${tabNav.getAttribute('data-bs-target')}`);
                
                tabNav.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Deactivate all tabs
                    tabNavs.forEach(tab => {
                        tab.classList.remove('active');
                        tab.setAttribute('aria-selected', 'false');
                    });
                    
                    // Activate current tab
                    this.classList.add('active');
                    this.setAttribute('aria-selected', 'true');
                    
                    // Hide all tab content
                    const tabContents = document.querySelectorAll('.tab-pane');
                    tabContents.forEach(content => {
                        content.classList.remove('show', 'active');
                    });
                    
                    // Show current tab content
                    const targetId = this.getAttribute('data-bs-target');
                    const targetContent = document.querySelector(targetId);
                    if (targetContent) {
                        console.log(`Activating content: ${targetId}`);
                        targetContent.classList.add('show', 'active');
                    }
                });
            });
            
            // Activate the first tab by default
            console.log("Activating first tab");
            tabNavs[0].click();
        } else {
            console.log("No tabs found to initialize");
        }
    }, 200);
    
    // Setup show more/less functionality for job descriptions
    const showMoreButtons = document.querySelectorAll('.description-toggle-more');
    const showLessButtons = document.querySelectorAll('.description-toggle-less');
    
    console.log(`Found ${showMoreButtons.length} show more buttons`);
    console.log(`Found ${showLessButtons.length} show less buttons`);
    
    // Add click handlers to Show More buttons
    showMoreButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const descriptionId = this.getAttribute('data-description-id');
            console.log(`Show more clicked for ${descriptionId}`);
            
            const shortDesc = document.getElementById(`job-description-short-${descriptionId}`);
            const fullDesc = document.getElementById(`job-description-full-${descriptionId}`);
            
            if (shortDesc && fullDesc) {
                shortDesc.classList.add('d-none');
                fullDesc.classList.remove('d-none');
                console.log("Toggled visibility");
            } else {
                console.log("Could not find elements:", {
                    shortDescId: `job-description-short-${descriptionId}`,
                    fullDescId: `job-description-full-${descriptionId}`
                });
            }
        });
    });
    
    // Add click handlers to Show Less buttons
    showLessButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const descriptionId = this.getAttribute('data-description-id');
            console.log(`Show less clicked for ${descriptionId}`);
            
            const shortDesc = document.getElementById(`job-description-short-${descriptionId}`);
            const fullDesc = document.getElementById(`job-description-full-${descriptionId}`);
            
            if (shortDesc && fullDesc) {
                shortDesc.classList.remove('d-none');
                fullDesc.classList.add('d-none');
                console.log("Toggled visibility");
            }
        });
    });
});
