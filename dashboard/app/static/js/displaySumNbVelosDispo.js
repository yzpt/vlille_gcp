function displaySumNbVelosDispo(labels, values) {
    var ctx = document.getElementById('canvas-sum-nbvelosdispo').getContext('2d');
    sumNbVelosDispoChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total vélos disponibles',
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
            // maintainAspectRatio: false,
            // aspectRatio: 3,
            scales: {
                x: {
                    ticks: {
                        // callback: function(value, index, values) {
                        //     if ((value % 180 === 0) || (index === value.length - 1)) {
                        //         const hours = Math.floor(value / 60);
                        //         const minutes = value % 60;
                        //         const formattedHours = hours < 10 ? `0${hours}` : `${hours}`;
                        //         if (value % 180 === 0) {
                        //             return `${formattedHours}h`;
                        //         } else if (index === value.length - 1) {
                        //             const formattedMinutes = minutes < 10 ? `0${minutes}` : `${minutes}`;
                        //             return `${formattedHours}h ${formattedMinutes}`;
                        //         }
                        //     }
                        // },
                        callback: function(value, index, values) {
                            // if (value % 180 === 0 || index === values.length - 1) {
                            if (value % 180 === 0) {
                                const hours = Math.floor(value / 60);
                                const formattedHours = hours < 10 ? `0${hours}` : `${hours}`;
                                return `${formattedHours}h`;
                            }
                        },
                        maxRotation: 45
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
                    beginAtZero: false
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
