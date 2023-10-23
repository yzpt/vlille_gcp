function initMap() {
    // Create a map centered on a default location (e.g., Paris)
    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 50.62338, lng: 3.051565 },
        zoom: 12 // Adjust the zoom level as needed
    });

    // Add markers to the map
    for (var i = 0; i < stations.length; i++) {
        var station = stations[i];
        addMarker(station, map);
    }
}
