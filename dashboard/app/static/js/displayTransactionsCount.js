function displayTransactionsCount(labels, values, values2) {
    var ctx = document.getElementById('canvas-transactions-count').getContext('2d');
    trasnsactionsCountChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'pos',
                    data: values,
                    backgroundColor: window.chartColors.green,
                    borderColor: window.chartColors.green,
                    borderWidth: 1
                },
                {
                    label: 'neg',
                    data: values2,
                    backgroundColor: window.chartColors.green,
                    borderColor: window.chartColors.green,
                    borderWidth: 1
                }
            ]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,
            aspectRatio: 3,
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
