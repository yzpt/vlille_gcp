function displayBarChartData(labels, values) {
    var ctx = document.getElementById('canvas-avg-hours').getContext('2d');
    avgBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'avg_nbvelosdispo',
                    data: values,
                    backgroundColor: window.chartColors.blue2,
                    borderColor: window.chartColors.blue2,
                    borderWidth: 2
                }
            ]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,
            aspectRatio: 5,
            scales: {
                x: {
                    ticks: {
                        callback: function(value, index, values) {
                            // Display labels only for specific hours
                            if ([0, 3, 6, 9, 12, 15, 18, 21].includes(value)) {
                                return value + "h";
                            }
                            // Hide labels for other hours
                            // return '';
                        },
                        maxRotation: 0
                    },
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                },
                y: {
                    ticks: {
                        display: true
                    },
                    grid: {
                        display: true,
                        drawBorder: true
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true
                }
            }
        }
    });
}
