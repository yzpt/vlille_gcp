// Function to fetch data based on selected weekday
async function fetchDataForTimelineSpan(station, selectedSpan) {
    
    // API endpoint URL with selected weekday value
    const apiUrl = `/get_timeline_nbvelos/${station.libelle}/${selectedSpan}`;  
    
    try {
        fetch(apiUrl)
            .then(function(response) {
                return response.json();
            })
            .then(function(jsonResponse) {
                // Update the chart with the new data
                lineChart.data.labels = jsonResponse.labels;
                lineChart.data.datasets[0].data = jsonResponse.values;
                lineChart.update();

                interval = Math.floor((jsonResponse.labels.length - 1) * 0.25);
                // interval = 100;
                console.log(jsonResponse);
                console.log('interval: ' + interval);
                console.log('Math.round(interval): ' + Math.round(interval));
                console.log('Math.round(interval * 2): ' + Math.round(interval * 2));
                console.log('Math.round(interval * 3): ' + Math.round(interval * 3));
                console.log('jsonResponse.labels.length - 1: ' + (jsonResponse.labels.length - 1));
                
                lineChart.options.scales.x.ticks = {
                    display: true,
                    min: 0,
                    max: jsonResponse.labels.length - 1,
                    callback: function(value,index) {
                        if (index % interval === 0) {
                            const date = new Date(this.getLabelForValue(value));
                            const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
                            const day = String(date.getDate()).padStart(2, '0');
                            return `${month}/${day}`;
                        }
                    },
                    // maxRotation: 80, // Rotates the labels to be completely horizontal
                    // minRotation: 80  // Rotates the labels to be completely horizontal
                };
                
                
                
                
                
                

                lineChart.update();
            // Perform further processing or visualization with xValues and yValues here
        })} catch (error) {
            console.error('Error fetching data:', error);
        }
    }