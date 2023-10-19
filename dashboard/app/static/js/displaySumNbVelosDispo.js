
function isSameDay(dateString1, dateString2) {
    const date1 = new Date(dateString1);
    const date2 = new Date(dateString2);
    return (
        date1.getDate() === date2.getDate() &&
        date1.getMonth() === date2.getMonth() &&
        date1.getFullYear() === date2.getFullYear()
    );
}


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
                    // ticks: {
                    //     callback: function(value, index, values) {
                    //         const currentLabel = this.getLabelForValue(value);
                    //         const prevLabel = this.getLabelForValue(values[index - 1]);
                            
                    //         // Check if the current label is from a new day (or if it's the first label)
                    //         if (!prevLabel || !isSameDay(currentLabel, prevLabel)) {
                    //             const dateObj = new Date(currentLabel);
                    //             const month = String(dateObj.getMonth() + 1).padStart(2, '0');
                    //             const day = String(dateObj.getDate()).padStart(2, '0');
                    //             const hour = String(dateObj.getHours()).padStart(2, '0');
                    //             const formattedDate = `${month}/${day} ${hour}:00`;
                    //             return formattedDate;
                    //         }
                    //     }
                    // },
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
