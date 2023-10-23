// Function to add a marker for a station
function addMarker(station, map) {
    var markerColor = ''; // Initialize the marker color

    // Determine the marker color based on nb_available_bikes
    if (station.operational_state === 'RÉFORMÉ') {
        markerColor = 'black';
    } else if (station.operational_state === 'IN_MAINTENANCE') {
        markerColor = 'purple';
    } else if (station.nb_available_bikes === 0) {
        markerColor = '#DB4437';
    } else if (station.nb_available_bikes >= 1 && station.nb_available_bikes <= 4) {
        markerColor = '#F4B400';
    } else if (station.nb_places_dispo == 0) {
        markerColor = '#4285F4';
    } else {
        markerColor = '#0F9D58';
    }

    // Create a custom marker icon with the determined color
    var markerIcon = {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: markerColor,
        fillOpacity: 0.8,
        strokeWeight: 0,
        scale: 10 // Adjust the scale as needed
    };

    var marker = new google.maps.Marker({
        position: { lat: station.latitude, lng: station.longitude },
        map: map,
        title: station.name,
        icon: markerIcon // Set the custom marker icon
    });

    // Add information as a content string to the marker
    var contentString = '<div><strong>' + station.name + '</strong><br>' +
        'Adress: ' + station.adress + '<br>' +
        'City: ' + station.city + '<br>' +
        'Op. state: ' + station.operational_state + '<br>' +
        'Connexion: ' + station.connexion + '<br>' +
        'Bikes: ' + station.nb_available_bikes + '<br>' +
        'Places: ' + station.nb_places_dispo + '<br>' +
        'Updated: ' + station.last_update + '</div>';

    var infowindow = new google.maps.InfoWindow({
        content: contentString
    });

    // Add a click event listener to display the information when the marker is clicked
    marker.addListener('click', function() {
        
        selectedStation = station;

        const selectedWeekday = document.getElementById("weekday_form").value;
        bq_loading_avg_hours.style.display = 'block';
        fetchDataForWeekday(station, selectedWeekday);

        const selectedSpan = document.getElementById("timeline_span_nbvelosdispo_form").value;
        bq_loading_timeline_nbvelos.style.display = 'block';
        fetchDataForTimelineSpan(station, selectedSpan);

        // Close the currently open info window, if any
        if (currentInfoWindow) {
            currentInfoWindow.close();
        }

        // Open the clicked marker's info window
        infowindow.open(map, marker);

        // Set the current info window to the clicked info window
        currentInfoWindow = infowindow;

        // remove 'hidden' class for station infos divs
        document.getElementById('graphs-indiv').classList.remove('hidden');

        // add 'hidden' class to the #div_infos_generales div
        document.getElementById('div_infos_generales').classList.add('hidden');
        document.getElementById('graphs-general').classList.add('hidden');

        // when windows is closed, add hidden class for #graphs-indiv        
        infowindow.addListener('closeclick', function() {
            document.getElementById('graphs-indiv').classList.add('hidden');
            document.getElementById('div_infos_generales').classList.remove('hidden');
            document.getElementById('graphs-general').classList.remove('hidden');
        });


            
    });
}
