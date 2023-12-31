function displayTimelineData(labels, values) {
    var ctx = document.getElementById('canvas-timeline-bike-count').getContext('2d');
    lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Bike count',
                    fill: false,
                    data: values,
                    stepped: true,
                    backgroundColor: window.chartColors.blue2,
                    borderColor: window.chartColors.blue2,
                    pointStyle: false,
                    borderWidth: 1.5
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
                        display: true,
                    },
                    grid: {
                        display: true,
                        drawBorder: true
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
