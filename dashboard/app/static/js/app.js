// ================== template script =================================
'use strict';

window.chartColors = {
	blue:  '#4285F4',
	blue2: '#76A7FA',
	blue3: '#A0C3FF',
	
	red:  '#DB4437',
	red2: '#E57368',
	red3: 'ED9D97',

	green:  '#0F9D58',
	green2: '#33B679',
	green3: '#7BCFA9',

	yellow: '#F4B400',
	yellow2: '#FBCB43',
	yellow3: '#FFE168',

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

