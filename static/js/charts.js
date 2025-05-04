// SmartSpend Charts JavaScript

/**
 * Create a pie chart
 * @param {string} elementId - The canvas element ID
 * @param {object} data - Chart data object
 * @param {string} title - Chart title
 */
function createPieChart(elementId, data, title) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    return new Chart(ctx, {
        type: 'pie',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: title ? true : false,
                    text: title || '',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed !== null) {
                                label += '$' + context.parsed.toFixed(2);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create a bar chart
 * @param {string} elementId - The canvas element ID
 * @param {object} data - Chart data object
 * @param {string} title - Chart title
 */
function createBarChart(elementId, data, title) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: title ? true : false,
                    text: title || '',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += '$' + context.parsed.y.toFixed(2);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create a line chart
 * @param {string} elementId - The canvas element ID
 * @param {object} data - Chart data object
 * @param {string} title - Chart title
 */
function createLineChart(elementId, data, title) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                },
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                        tooltipFormat: 'MMM d, yyyy',
                        displayFormats: {
                            day: 'MMM d'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: title ? true : false,
                    text: title || '',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += '$' + context.parsed.y.toFixed(2);
                            }
                            return label;
                        }
                    }
                }
            },
            elements: {
                line: {
                    tension: 0.3
                }
            }
        }
    });
}

/**
 * Create a doughnut chart
 * @param {string} elementId - The canvas element ID
 * @param {object} data - Chart data object
 * @param {string} title - Chart title
 */
function createDoughnutChart(elementId, data, title) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: title ? true : false,
                    text: title || '',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed !== null) {
                                label += '$' + context.parsed.toFixed(2);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create a radar chart
 * @param {string} elementId - The canvas element ID
 * @param {object} data - Chart data object
 * @param {string} title - Chart title
 */
function createRadarChart(elementId, data, title) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    return new Chart(ctx, {
        type: 'radar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: title ? true : false,
                    text: title || '',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

/**
 * Create a stacked bar chart
 * @param {string} elementId - The canvas element ID
 * @param {object} data - Chart data object
 * @param {string} title - Chart title
 */
function createStackedBarChart(elementId, data, title) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: title ? true : false,
                    text: title || '',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += '$' + context.parsed.y.toFixed(2);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Update chart data
 * @param {Chart} chart - The chart instance
 * @param {Array} labels - New labels
 * @param {Array} data - New data
 */
function updateChartData(chart, labels, data) {
    if (!chart) return;
    
    chart.data.labels = labels;
    
    if (Array.isArray(data)) {
        // For single dataset
        chart.data.datasets[0].data = data;
    } else if (typeof data === 'object') {
        // For multiple datasets
        Object.keys(data).forEach((key, index) => {
            if (chart.data.datasets[index]) {
                chart.data.datasets[index].data = data[key];
            }
        });
    }
    
    chart.update();
}

/**
 * Create progress chart (semi-circle)
 * @param {string} elementId - The canvas element ID
 * @param {number} percentage - Percentage value (0-100)
 * @param {string} label - Chart label
 */
function createProgressChart(elementId, percentage, label) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    // Ensure percentage is between 0 and 100
    const value = Math.min(Math.max(percentage, 0), 100);
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [
                    value < 50 ? '#e74a3b' : value < 75 ? '#f6c23e' : '#1cc88a',
                    '#eaecf4'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '85%',
            circumference: 180,
            rotation: 270,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        },
        plugins: [{
            id: 'progressLabel',
            afterDraw: function(chart) {
                const width = chart.width;
                const height = chart.height;
                const ctx = chart.ctx;
                
                ctx.restore();
                ctx.font = '1.5rem sans-serif';
                ctx.textBaseline = 'middle';
                ctx.textAlign = 'center';
                
                // Draw percentage
                ctx.fillStyle = value < 50 ? '#e74a3b' : value < 75 ? '#f6c23e' : '#1cc88a';
                ctx.fillText(value.toFixed(0) + '%', width / 2, height - 30);
                
                // Draw label
                if (label) {
                    ctx.font = '1rem sans-serif';
                    ctx.fillStyle = '#858796';
                    ctx.fillText(label, width / 2, height - 10);
                }
                
                ctx.save();
            }
        }]
    });
}
