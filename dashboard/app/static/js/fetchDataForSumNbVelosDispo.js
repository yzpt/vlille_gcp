
async function fetchDataForSumNbVelosDispo() {

    // API endpoint URL with selected weekday value
    const apiUrl = `/get_timeline_sum`;

    try {
        fetch(apiUrl)
            .then(function (response) {
                return response.json();
            })
            .then(function (jsonResponse) {
                // Update the chart with the new data
                sumNbVelosDispoChart.data.labels = jsonResponse.labels;
                sumNbVelosDispoChart.data.datasets[0].data = jsonResponse.values;
                sumNbVelosDispoChart.update();
                loadingIndicator.style.display = 'none';

            });
        sumNbVelosDispoChart.update();
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}
