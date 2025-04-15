// Dashboard charts and statistics

/**
 * Initialize the application status chart
 */
function initStatusChart() {
    // Get chart element
    var canvas = document.getElementById("statusChart");
    if (!canvas) return;
    
    // Get chart data from DOM
    var dataElement = document.getElementById("chartData");
    if (!dataElement) return;
    
    try {
        // Parse the JSON data from the data-chart attribute
        var chartData = JSON.parse(dataElement.getAttribute("data-chart"));
        
        // Create chart
        new Chart(canvas, {
            type: "doughnut",
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.data,
                    backgroundColor: [
                        "rgba(13, 110, 253, 0.7)",  // Applied - primary
                        "rgba(13, 202, 240, 0.7)",  // Interview - info
                        "rgba(25, 135, 84, 0.7)",   // Offer - success
                        "rgba(220, 53, 69, 0.7)",   // Rejected - danger
                        "rgba(108, 117, 125, 0.7)"  // Saved - secondary
                    ],
                    borderColor: [
                        "rgba(13, 110, 253, 1)",
                        "rgba(13, 202, 240, 1)",
                        "rgba(25, 135, 84, 1)",
                        "rgba(220, 53, 69, 1)",
                        "rgba(108, 117, 125, 1)"
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "right"
                    }
                }
            }
        });
    } catch (e) {
        console.error("Error initializing chart:", e);
    }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function() {
    initStatusChart();
});
