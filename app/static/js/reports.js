let trendChart = null;
let categoryChart = null;

function initTrendChart() {
    const canvas = document.getElementById('trendChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const data = window.reportsData || {};
    
    if (trendChart) {
        trendChart.destroy();
    }
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.monthlyLabels || ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr'],
            datasets: [
                {
                    label: 'Income',
                    data: data.monthlyIncome || [5000, 5000, 5000, 5000, 5000, 5000],
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2
                },
                {
                    label: 'Expenses',
                    data: data.monthlySpending || [4200, 3800, 3433, 3100, 2950, 2800],
                    borderColor: '#fd7e14',
                    backgroundColor: 'rgba(253, 126, 20, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.raw.toFixed(2);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}


function initCategoryChart() {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const data = window.reportsData || {};
    
    const categoryLabels = data.categoryLabels || ['Food', 'Transportation', 'Entertainment', 'Health', 'Software', 'Utilities'];
    const categoryValues = data.categoryValues || [258.57, 65.00, 34.00, 49.99, 30.98, 180.00];
    const colors = ['#0d6efd', '#20c997', '#0dcaf0', '#fd7e14', '#6c757d', '#d63384'];
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categoryLabels,
            datasets: [{
                data: categoryValues,
                backgroundColor: colors.slice(0, categoryLabels.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: $${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}


async function refreshData() {
    try {
        const response = await fetch('/reports/api/monthly-trend');
        if (response.ok) {
            const data = await response.json();
            if (trendChart) {
                trendChart.data.datasets[0].data = data.income;
                trendChart.data.datasets[1].data = data.spending;
                trendChart.update();
            }
        }
    } catch (error) {
        console.error('Error refreshing data:', error);
    }
}


function init() {
    initTrendChart();
    initCategoryChart();
}

document.addEventListener('DOMContentLoaded', init);