function displayDoughnutChartData() {
    var ctx = document.getElementById('canvas-doughnut').getContext('2d');
    doughnutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [
                    189,
                    32,
                    5,
                    1
                ],
                backgroundColor: [
                    window.chartColors.green2,
                    window.chartColors.red2,
                    window.chartColors.blue2,
                    window.chartColors.purple,
                ],
                label: 'Dataset 1'
            }],
            labels: [
                'Disponibles',
                'Vides',
                'Pleines',
                'En maintenance'
            ]
        },
        // overrides[type].plugins.legend
        plugins: {
            legend: {
                display: true,
                position: 'right',
            },
        },
        options: {
            radius: '50%',
            responsive: true,
        }
    });
}
