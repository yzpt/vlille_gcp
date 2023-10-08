new Chart(
    document.getElementById('doughnut-chart'),
    {
        type: "doughnut",
        data: {
            "labels":["Red","Blue","Yellow"],
            "datasets":[{
                "label":"My First Dataset",
                "data":[300,50,100],
                "backgroundColor":["rgb(255, 99, 132)","rgb(54, 162, 235)","rgb(255, 205, 86)"]
            }]
        },
        options: {
            aspectRatio: 2,
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'Chart.js Doughnut Chart'
                }
            }
        }
    }
)