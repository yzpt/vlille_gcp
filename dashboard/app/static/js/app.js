// ================== template script =================================
'use strict';

window.chartColors = {
    green: '#75c181',
    gray: '#a9b5c9',
    text: '#252930',
    border: '#e7e9ed'
};


/* ===== Enable Bootstrap Popover (on element  ====== */
const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

/* ==== Enable Bootstrap Alert ====== */
//var alertList = document.querySelectorAll('.alert')
//alertList.forEach(function (alert) {
//  new bootstrap.Alert(alert)
//});

const alertList = document.querySelectorAll('.alert')
const alerts = [...alertList].map(element => new bootstrap.Alert(element))

// ====================================================================
// ====================================================================

let currentInfoWindow = null;
let selectedStation = stations[0];

displayBarChartData([0,0],[0,0]);
displayTimelineData([0,0],[0,0]);

fetch('/get_transactions_count')
    .then(function(response) {
        return response.json();
    })
    .then(function(jsonResponse) {
        displayTransactionsCount(jsonResponse.labels, jsonResponse.values, jsonResponse.values2);
    });

fetch('/get_nbvelosdispo')
    .then(function(response) {
        return response.json();
    })
    .then(function(jsonResponse) {
        displaySumNbVelosDispo(jsonResponse.labels, jsonResponse.values);
    });

// Event listener for the weekday dropdown change event
document.getElementById("weekday_form").addEventListener("change", () => {
    fetchDataForWeekday(selectedStation, document.getElementById("weekday_form").value);
});

// Event listener for the timeline span dropdown change event
document.getElementById("timeline_span_nbvelosdispo_form").addEventListener("change", () => {
    fetchDataForTimelineSpan(selectedStation, document.getElementById("timeline_span_nbvelosdispo_form").value);
});

