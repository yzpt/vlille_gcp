function displayTotalBikesTimeline(labels, values, span) {
    var ctx = document.getElementById('canvas-total-bikes-timeline').getContext('2d');
    sumNbVelosDispoChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total bikes available',
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
                        callback: function(value, index, values) {
                            const currentLabel = this.getLabelForValue(value);
                            const dateObj = new Date(currentLabel);
                            // labels shifted by 2 hours
                            dateObj.setHours(dateObj.getHours() - 2 );

                            const month = (dateObj.getMonth() + 1 < 10) ? `0${dateObj.getMonth() + 1}` : `${dateObj.getMonth() + 1}`;
                            const day = (dateObj.getDate() < 10) ? `0${dateObj.getDate()}` : `${dateObj.getDate()}`;
                            const hour = (dateObj.getHours() < 10) ? `0${dateObj.getHours()}` : `${dateObj.getHours()}`;
                            const minute = (dateObj.getMinutes() < 10) ? `0${dateObj.getMinutes()}` : `${dateObj.getMinutes()}`;

                            if (span === 'today' || span === '24h') {
                                if (minute === '00') {
                                    if (hour == '00' || hour == '03' || hour == '06' || hour == '09' || hour == '12' || hour == '15' || hour == '18' || hour == '21') {
                                        return `${hour}h`;
                                    }
                                }
                            } else if (span === '7d') {
                                if (minute === '00') {
                                    if (hour == '00') {
                                        return `${day}/${month}`;
                                    }
                                }
                            }
                        }
                    },
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
