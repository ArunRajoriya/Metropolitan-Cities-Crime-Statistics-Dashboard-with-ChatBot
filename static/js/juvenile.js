Chart.register(ChartDataLabels);
let citiesBarChart;

/* ---------------- INIT CHART ---------------- */
function initCharts() {
    citiesBarChart = new Chart(
        document.getElementById("citiesBarChart"),
        {
            type: "bar",
            data: {
                labels: [],
                datasets: [{
                    label: "Juveniles",
                    data: [],
                    backgroundColor: '#cc1c1c'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: { display: false },

                    // 👇 THIS IS THE MAGIC
                    datalabels: {
                        anchor: 'end',
                        align: 'end',
                        color: '#b81414',
                        font: {
                            weight: 'bold',
                            size: 16
                        },
                        formatter: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    );
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

/* ---------------- LOAD KPIs ---------------- */
function loadKPIs() {
    fetch("/api/juvenile-kpis")
        .then(res => res.json())
        .then(data => {
            document.getElementById("total2019").innerText = data.total2019.toLocaleString();
            document.getElementById("boys2019").innerText = data.boys2019.toLocaleString();
            document.getElementById("girls2019").innerText = data.girls2019.toLocaleString();

            document.getElementById("total2020").innerText = data.total2020.toLocaleString();
            document.getElementById("boys2020").innerText = data.boys2020.toLocaleString();
            document.getElementById("girls2020").innerText = data.girls2020.toLocaleString();
        });
}

/* ---------------- DOM READY ---------------- */
document.addEventListener("DOMContentLoaded", () => {

    initCharts();
    loadKPIs();

    // Default load
    loadBar("2019");

    document.getElementById("yearFilter").addEventListener("change", (e) => {
        loadBar(e.target.value);
    });

});
