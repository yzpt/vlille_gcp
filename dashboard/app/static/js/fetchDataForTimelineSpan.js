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
                bq_loading_timeline_nbvelos.style.display = 'none';
                })
                lineChart.update();
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

