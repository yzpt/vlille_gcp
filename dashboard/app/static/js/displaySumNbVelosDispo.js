
function isSameDay(dateString1, dateString2) {
    const date1 = new Date(dateString1);
    const date2 = new Date(dateString2);
    return (
        date1.getDate() === date2.getDate() &&
        date1.getMonth() === date2.getMonth() &&
        date1.getFullYear() === date2.getFullYear()
    );
}


function displaySumNbVelosDispo(labels, values, span) {
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
                        callback: function(value, index, values) {

                            const currentLabel = this.getLabelForValue(value);
                            
                            // example : "Fri, 20 Oct 2023 00:00:00 GMT"
                            const dateObj = new Date(currentLabel);
                            // labels shifted by 2 hours
                            dateObj.setHours(dateObj.getHours() - 2 );

                            const month = (dateObj.getMonth() + 1 < 10) ? `0${dateObj.getMonth() + 1}` : `${dateObj.getMonth() + 1}`;
                            const day = (dateObj.getDate() < 10) ? `0${dateObj.getDate()}` : `${dateObj.getDate()}`;
                            const hour = (dateObj.getHours() < 10) ? `0${dateObj.getHours()}` : `${dateObj.getHours()}`;
                            const minute = (dateObj.getMinutes() < 10) ? `0${dateObj.getMinutes()}` : `${dateObj.getMinutes()}`;

                            
                            // const timeSpan = document.getElementById('timeline_sum_span').value;
                            const timeSpan = span;
                            if (timeSpan === 'today' || timeSpan === '24h') {
                                if (minute === '00') {
                                    if (hour == '00' || hour == '03' || hour == '06' || hour == '09' || hour == '12' || hour == '15' || hour == '18' || hour == '21') {
                                        return `${hour}h`;
                                    }
                                }
                            } else if (timeSpan === '7d') {
                                if (minute === '00') {
                                    if (hour == '00') {
                                        return `${dateObj.getDate()}/${month}`;
                                    }
                                }
                            }
                        }
                    },
                    // grid: {
                    //     callback: function(value, index, values) {
                    //         const currentLabel = this.getLabelForValue(value);
                    //         const prevLabel = this.getLabelForValue(values[index - 1]);
                            
                    //         // Check if the current label is from a new day (or if it's the first label)
                    //         if (!prevLabel || !isSameDay(currentLabel, prevLabel)) {
                    //             return true; // Display grid line for the first timestamp of the day
                    //         } else {
                    //             return false; // Hide grid line for other timestamps in the same day
                    //         }
                    //     }
                    // }
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
