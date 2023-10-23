// Function to fetch data based on selected weekday
async function fetchDataForWeekday(station, selectedWeekday) {
    
    // API endpoint URL with selected weekday value
    const apiUrl = `/get_avg_bars/${station.id}/${selectedWeekday}`;  
    
    try {
        fetch(apiUrl)
            .then(function(response) {
                return response.json();
            })
            .then(function(jsonResponse) {
                // Update the chart with the new data
                avgBarChart.data.labels = jsonResponse.labels;
                avgBarChart.data.datasets[0].data = jsonResponse.values;
                avgBarChart.update();
                bq_loading_avg_hours.style.display = 'none';
            // Perform further processing or visualization with xValues and yValues here
        })} catch (error) {
            console.error('Error fetching data:', error);
        }
    }