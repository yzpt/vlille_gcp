
async function fetchDataForSumNbVelosDispo(span) {

    // API endpoint URL with selected weekday value
    const apiUrl = `/get_timeline_sum/${span}`;

    try {
        fetch(apiUrl)
            .then(function (response) {
                return response.json();
            })
            .then(function (jsonResponse) {
                // Update the chart with the new data
                sumNbVelosDispoChart.data.labels = jsonResponse.labels;
                sumNbVelosDispoChart.data.datasets[0].data = jsonResponse.values;


                sumNbVelosDispoChart.options.scales.x.ticks.callback = function(value, index, values) {
                        const currentLabel = this.getLabelForValue(value);
                                
                        // example : "Fri, 20 Oct 2023 00:00:00 GMT"
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
                                    return `${dateObj.getDate()}/${month}`;
                                }
                            }
                        }
                    }
                

                sumNbVelosDispoChart.update();
                bq_loading_sumnbvelos.style.display = 'none';
            });
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function formattedDatetime(date) {
    const dateObj = new Date(date);
    const month = (dateObj.getMonth() + 1 < 10) ? `0${dateObj.getMonth() + 1}` : `${dateObj.getMonth() + 1}`;
    const day = (dateObj.getDate() < 10) ? `0${dateObj.getDate()}` : `${dateObj.getDate()}`;
    const hour = (dateObj.getHours() < 10) ? `0${dateObj.getHours()}` : `${dateObj.getHours()}`;
    const minute = (dateObj.getMinutes() < 10) ? `0${dateObj.getMinutes()}` : `${dateObj.getMinutes()}`;

    return `${day}/${month} ${hour}:${minute}`;
}

function formattedDate(date) {
    const dateObj = new Date(date);
    const month = (dateObj.getMonth() + 1 < 10) ? `0${dateObj.getMonth() + 1}` : `${dateObj.getMonth() + 1}`;
    const day = (dateObj.getDate() < 10) ? `0${dateObj.getDate()}` : `${dateObj.getDate()}`;

    return `${day}/${month}`;
}