// Function to fetch data based on selected weekday
async function fetchDataForTimelineSpan(station, selectedSpan) {
    
    // API endpoint URL with selected weekday value
    const apiUrl = `/get_timeline_nbvelos/${station.id}/${selectedSpan}`;  
    
    try {
        fetch(apiUrl)
            .then(function(response) {
                return response.json();
            })
            .then(function(jsonResponse) {
                // Update the chart with the new data
                lineChart.data.labels = jsonResponse.labels;
                lineChart.data.datasets[0].data = jsonResponse.values;

                // Update the chart's ticks according to the selected span
                lineChart.options.scales.x.ticks.callback = function(value, index, values) {
                    const currentLabel = this.getLabelForValue(value);
                    const dateObj = new Date(currentLabel);
                    // labels shifted by 2 hours
                    dateObj.setHours(dateObj.getHours() - 2 );
                    const month = (dateObj.getMonth() + 1 < 10) ? `0${dateObj.getMonth() + 1}` : `${dateObj.getMonth() + 1}`;
                    const day = (dateObj.getDate() < 10) ? `0${dateObj.getDate()}` : `${dateObj.getDate()}`;
                    const hour = (dateObj.getHours() < 10) ? `0${dateObj.getHours()}` : `${dateObj.getHours()}`;
                    const minute = (dateObj.getMinutes() < 10) ? `0${dateObj.getMinutes()}` : `${dateObj.getMinutes()}`;
                    
                    if (selectedSpan === 'today' || selectedSpan === '24h') {
                        if (minute === '00') {
                            if (hour == '00' || hour == '03' || hour == '06' || hour == '09' || hour == '12' || hour == '15' || hour == '18' || hour == '21') {
                                return `${hour}h`;
                            }
                        }
                    } else if (selectedSpan === '7d') {
                        if (minute === '00') {
                            if (hour == '00') {
                                return `${day}/${month}`;
                            }
                        }
                    }
                }

                lineChart.update();
                bq_loading_timeline_bike_count.style.display = 'none';
                })
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

