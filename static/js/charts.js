$(document).ready(function() {
    var labels = JSON.parse("{{ labels|escapejs }}");
    var counts = JSON.parse("{{ counts|escapejs }}");

    console.log(labels);  // Verificar los valores de labels en la consola
    console.log(counts);  // Verificar los valores de counts en la consola

    var ctx = document.getElementById('donutChart').getContext('2d');
    var donutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Usuarios por Grupo',
                data: counts,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            legend: {
                display: true,
                position: 'bottom'
            }
        }
    });
});