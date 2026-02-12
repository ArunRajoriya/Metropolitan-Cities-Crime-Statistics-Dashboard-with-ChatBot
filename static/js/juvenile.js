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
                        formatter: (v) => v.toLocaleString()
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
            document.getElementById("kpiTotal").innerText = data.total.toLocaleString();
            document.getElementById("kpiBoys").innerText  = data.boys.toLocaleString();
            document.getElementById("kpiGirls").innerText = data.girls.toLocaleString();
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
                                formatter: v => v.toLocaleString()
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
