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
                        callback: function(value, index, values) {
                            const label = this.getLabelForValue(value);

                            
                            if (
                                ( typeof label === 'string' 
                                &&(label.includes(' 00:00') 
                                || label.includes(' 03:00')
                                || label.includes(' 06:00')
                                || label.includes(' 09:00')
                                || label.includes(' 12:00')
                                || label.includes(' 15:00')
                                || label.includes(' 18:00')
                                || label.includes(' 21:00'))
                            ) 
                                || (index == values.length - 1)
                            )
                            {  
                                // Parse the label as a Date object
                                const dateObj = new Date(label);

                                // Extract month, day, hours, and minutes
                                const month = String(dateObj.getMonth() + 1).padStart(2, '0'); // Months are 0-based
                                const day = String(dateObj.getDate()).padStart(2, '0');
                                const hours = String(dateObj.getUTCHours()).padStart(2, '0');
                                const minutes = String(dateObj.getUTCMinutes()).padStart(2, '0');

                                // Format the date as MM/DD and the time as HH:MM
                                const formattedDate = `${month}/${day}`;
                                const formattedTime = `${hours}:${minutes}`;
                                
                                return formattedTime;
                            }

                        },
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        callback: function(value, index, values) {
                            const label = this.getLabelForValue(value);
                            if ( typeof label === 'string' 
                                &&(label.includes(' 00:00')
                                || label.includes(' 03:00')
                                || label.includes(' 06:00')
                                || label.includes(' 09:00')
                                || label.includes(' 12:00')
                                || label.includes(' 15:00')
                                || label.includes(' 18:00')
                                || label.includes(' 21:00'))
                            ) {
                                return true;
                            }
                            return false;
                        },
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
