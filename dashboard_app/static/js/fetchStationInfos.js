async function fetchStationInfos(station) {
    const apiUrl = `/get_station_infos/${station.libelle}`;

    try {
        fetch(apiUrl)
            .then(function(response) {
                return response.json();
            })
            .then(function(jsonResponse) {
                
            })
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}