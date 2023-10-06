function displayTransactionsCount(labels, values, values2) {
    var ctx = document.getElementById('canvas-transactions-count').getContext('2d');
    trasnsactionsCountChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Vélos pris',
                    data: values2,
                    backgroundColor: window.chartColors.green2,
                    borderColor: window.chartColors.green2,
                    borderWidth: 1
                },
                {
                    label: 'Vélos retournés',
                    data: values,
                    backgroundColor: window.chartColors.blue2,
                    borderColor: window.chartColors.blue2,
                    borderWidth: 1
                }
            ]
        },

        options: {
            responsive: true,
            // maintainAspectRatio: false,
            // aspectRatio: 3,
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
                    display: true, // Set to true to display the legend
                    position: 'bottom', // You can also set the position to 'bottom', 'left', or 'right'
                },
                tooltip: {
                    enabled: true
                }
            }
        }
    });
}
