/* ---------------- INDIAN NUMBER FORMATTING ---------------- */
function formatIndianNumber(num) {
    if (num === 0) return '0';
    
    const numStr = Math.abs(num).toString();
    const isNegative = num < 0;
    
    // For numbers less than 1000, no formatting needed
    if (numStr.length <= 3) {
        return isNegative ? '-' + numStr : numStr;
    }
    
    // Split the number into groups: first 3 digits, then groups of 2
    let result = '';
    let remaining = numStr;
    
    // Handle the rightmost 3 digits
    if (remaining.length > 3) {
        result = ',' + remaining.slice(-3) + result;
        remaining = remaining.slice(0, -3);
    } else {
        result = remaining + result;
        remaining = '';
    }
    
    // Handle groups of 2 digits from right to left
    while (remaining.length > 0) {
        if (remaining.length <= 2) {
            result = remaining + result;
            break;
        } else {
            result = ',' + remaining.slice(-2) + result;
            remaining = remaining.slice(0, -2);
        }
    }
    
    return isNegative ? '-' + result : result;
}

Chart.register(ChartDataLabels);

let citiesBarChart = null;
let juvenileTrendChart = null;



/* ---------------- INIT CHART ---------------- */
function initChart() {
    citiesBarChart = new Chart(
        document.getElementById("citiesBarChart"),
        {
            type: "bar",
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: '#cc1c1c',
                    borderRadius: 6,
                    barThickness: 24
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false },

                    // labels on bars
                    datalabels: {
                        anchor: 'end',
                        align: 'end',
                        color: '#111',
                        font: { weight: 'bold', size: 14 },
                        formatter: (v) => formatIndianNumber(v)
                    }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        }
    );
}

/* ---------------- LOAD KPI ---------------- */
function loadKPIs(year) {
    fetch(`/api/juvenile-kpis?year=${year}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("kpiTotal").innerText = formatIndianNumber(data.total);
            document.getElementById("kpiBoys").innerText  = formatIndianNumber(data.boys);
            document.getElementById("kpiGirls").innerText = formatIndianNumber(data.girls);
        });
}

/* ---------------- LOAD BAR ---------------- */
function loadBar(year) {
    fetch(`/api/juvenile-cities?year=${year}`)
        .then(res => res.json())
        .then(data => {
            citiesBarChart.data.labels = data.labels;
            citiesBarChart.data.datasets[0].data = data.values;
            citiesBarChart.update();
        });
}

/* ---------------- DOM READY ---------------- */
document.addEventListener("DOMContentLoaded", () => {

    initChart();

    const resetBtn   = document.getElementById("resetBtn");
    const yearFilter = document.getElementById("yearFilter");

    const citiesBox = document.getElementById("citiesBarChart").parentElement;
    const trendBox  = document.getElementById("juvenileTrendSection");

    /* ---------- HELPER ---------- */
    function showTrend() {
        citiesBox.style.display = "none";
        trendBox.style.display  = "block";
        loadJuvenileTrend();
    }

    function showCities(year) {
        trendBox.style.display  = "none";
        citiesBox.style.display = "block";
        loadBar(year);
    }

    /* ---------- RESET ---------- */
    resetBtn.addEventListener("click", () => {
        yearFilter.value = "all";
        loadKPIs("all");
        showTrend();
    });

    /* ---------- INITIAL LOAD ---------- */
    loadKPIs("all");
    showTrend();

    /* ---------- YEAR CHANGE ---------- */
    yearFilter.addEventListener("change", (e) => {

        const year = e.target.value;

        loadKPIs(year);

        if (year === "all") {
            showTrend();
        } else {
            showCities(year);
        }
    });

});


function loadJuvenileTrend() {

    fetch("/api/juvenile-trend")
        .then(res => res.json())
        .then(data => {

            if (juvenileTrendChart) juvenileTrendChart.destroy();

            juvenileTrendChart = new Chart(
                document.getElementById("juvenileTrendChart"), {
                    type: "bar",
                    data: {
                        labels: Object.keys(data),
                        datasets: [{
                            data: Object.values(data),
                            borderRadius: 8,
                            barThickness: 60
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: { enabled: false },
                            datalabels: {
                                anchor: 'end',
                                align: 'top-right',
                                font: { weight: 'bold', size: 14 },
                                formatter: v => formatIndianNumber(v)
                            }
                        },
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                }
            );
        });
}
