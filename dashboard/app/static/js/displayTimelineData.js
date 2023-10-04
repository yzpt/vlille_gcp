function displayTimelineData(labels, values) {
    var ctx = document.getElementById('canvas-timeline-nbvelos').getContext('2d');
    lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'nb_velos_dispo',
                    fill: false,
                    data: values,
                    stepped: true,
                    backgroundColor: window.chartColors.green,
                    borderColor: window.chartColors.green,
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
                        callback: function(value, index) {
                            if (index % 100 === 0) {
                                return value;
                            }
                        }
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
                    enabled: false
                }
            }
        }
    });
}
