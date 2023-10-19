
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
                    const prevLabel = this.getValue(values[index - 1]);
                    const currentLabel = this.getLabelForValue(value);

                    // console.log(prevLabel ? prevLabel.substring(0,5) : null);
                    console.log(formattedDate(currentLabel));

                    if (!prevLabel || formattedDate(prevLabel) !== formattedDate(currentLabel)) {
                        return formattedDatetime(currentLabel);
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