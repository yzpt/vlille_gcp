function calculateMarkerColor(tauxVelosDispo) {
    // Interpolate the color based on tauxVelosDispo value
    var red = 255 * (1 - tauxVelosDispo);
    var green = 255 * tauxVelosDispo;
    var blue = 0; // Assuming no blue component for this gradient

    // Return the RGB color as a string
    return 'rgb(' + red + ',' + green + ',' + blue + ')';
}


function initMap() {
    // Create a map centered on a default location (e.g., Paris)
    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 50.62338, lng: 3.051565 },
        zoom: 12 // Adjust the zoom level as needed
    });

    fetch('data.json')
    .then(response => response.json())
    .then(data => {
        data = data['2023-10-20 00:00'];
        console.log(data);
        // {latitude: Array(257), longitude: Array(257), taux_velos_dispo: Array(257)}

        var markers = [];
        var infowindows = [];

        for (var i = 0; i < data['latitude'].length; i++) {
            var markerColor = calculateMarkerColor(data['taux_velos_dispo'][i]);

            var marker = new google.maps.Marker({
                position: { lat: data['latitude'][i], lng: data['longitude'][i] },
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 10,
                    fillColor: markerColor, // Use the dynamically calculated color
                    fillOpacity: 0.8,
                    strokeWeight: 0
                },
                map: map
            });
            markers.push(marker);

            var infowindow = new google.maps.InfoWindow({
                content: "Taux de vélos disponibles : " + data['taux_velos_dispo'][i]
            });
            infowindows.push(infowindow);
        }

    })
}

