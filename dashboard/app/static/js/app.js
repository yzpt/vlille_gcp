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

// displayBarChartData([0,0],[0,0]);
// displayTimelineData([0,0],[0,0]);
displayBarChartData([],[]);
displayTimelineData([],[]);


bq_loading_sumnbvelos.style.display = 'block';
fetch('/get_timeline_sum/today')
	.then(function(response) {
		return response.json();
	})
	.then(function(jsonResponse) {
		bq_loading_sumnbvelos.style.display = 'none';
		displaySumNbVelosDispo(jsonResponse.labels, jsonResponse.values, 'today');
	}
);

bq_loading_todays_transactions.style.display = 'block';
fetch('/get_transactions_count')
    .then(function(response) {
        return response.json();
    })
    .then(function(jsonResponse) {
		bq_loading_todays_transactions.style.display = 'none';
        displayTransactionsCount(jsonResponse.labels, jsonResponse.values, jsonResponse.values2);
    });
    
// Event listener for the timeline_sum_span dropdown change event
document.getElementById("timeline_sum_span").addEventListener("change", () => {
	bq_loading_sumnbvelos.style.display = 'block';
	fetchDataForSumNbVelosDispo(document.getElementById("timeline_sum_span").value);
});


// Event listener for the weekday dropdown change event
document.getElementById("weekday_form").addEventListener("change", () => {
	bq_loading_avg_hours.style.display = 'block';
    fetchDataForWeekday(selectedStation, document.getElementById("weekday_form").value);
});

// Event listener for the timeline span dropdown change event
document.getElementById("timeline_span_nbvelosdispo_form").addEventListener("change", () => {
	bq_loading_timeline_nbvelos.style.display = 'block';
    fetchDataForTimelineSpan(selectedStation, document.getElementById("timeline_span_nbvelosdispo_form").value);
});



// ======================= timespan buttons management =======================
// Get the buttons
const buttons = document.querySelectorAll('.btn-timespan-group .btn-timespan');

// Function to handle button clicks
function handleButtonClick(event) {
	bq_loading_sumnbvelos.style.display = 'block';
	fetchDataForSumNbVelosDispo(event.target.getAttribute('data-value'));

    // Remove the 'selected' class from all buttons
    buttons.forEach(button => {
        button.classList.remove('selected');
    });

    // Add the 'selected' class to the clicked button
    event.target.classList.add('selected');

    // Get the selected value and store it in local storage
    const selectedValue = event.target.getAttribute('data-value');
    localStorage.setItem('selectedTimeline', selectedValue);

    // Perform actions based on the selected value (you can add your logic here)
    console.log('Selected value:', selectedValue);
}

// Attach click event listeners to the buttons
buttons.forEach(button => {
    button.addEventListener('click', handleButtonClick);
});

// Check if there's a selected value in local storage and apply the 'selected' class
const storedValue = localStorage.getItem('selectedTimeline');
if (storedValue) {
    const selectedButton = document.querySelector(`[data-value="${storedValue}"]`);
    if (selectedButton) {
        selectedButton.classList.add('selected');
    }
}
