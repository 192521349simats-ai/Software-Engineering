
const ctx = document.getElementById('costChart');

new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
            label: 'Cloud Spending ($)',
            data: [18000, 21000, 19500, 23000, 22000, 24850],
            borderColor: '#5279d8',
            backgroundColor: 'rgba(82, 121, 216, 0.12)',
            fill: true,
            tension: 0.4,
            borderWidth: 3
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
