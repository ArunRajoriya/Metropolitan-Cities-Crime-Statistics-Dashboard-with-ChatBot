let trendChart = null;
Chart.register(ChartDataLabels);

/* ---------------- LOAD CRIMES ---------------- */
function loadCrimes(year) {
    return fetch(`/api/foreigner-crimes?year=${year}`)
        .then(res => res.json())
        .then(data => {
            const crimeSelect = document.getElementById("crimeFilter");
            crimeSelect.innerHTML = `<option value="all">All</option>`;
            data.crimes.forEach(c => {
                crimeSelect.innerHTML += `<option value="${c}">${c}</option>`;
            });
        });
}

/* ---------------- LOAD TABLE ---------------- */
function loadTable(year, crime) {

    const tableSection = document.querySelector(".table-section");
    tableSection.style.display = "block";

    fetch(`/api/foreigner-data?year=${year}&crime=${crime}`)
        .then(res => res.json())
        .then(data => {

            const table = document.getElementById("foreignerTable");
            table.innerHTML = "";

            let header = "<tr>";
            data.columns.forEach(col => {
                header += `<th>${col}</th>`;
            });
            header += "</tr>";
            table.innerHTML += header;

            data.rows.forEach(row => {
                let tr = "<tr>";
                data.columns.forEach(col => {
                    tr += `<td>${row[col]}</td>`;
                });
                tr += "</tr>";
                table.innerHTML += tr;
            });
        });
}

/* ---------------- TREND CHART ---------------- */
function loadTrendChart() {

    const trendSection = document.getElementById("trendSection");
    const tableSection = document.querySelector(".table-section");

    trendSection.style.display = "block";
    tableSection.style.display = "none";

    fetch("/api/foreigner-trend")
        .then(res => res.json())
        .then(data => {

            const labels = Object.keys(data);
            const values = labels.map(y => data[y].value);
            const crimes = labels.map(y => data[y].crime);

            if (trendChart) trendChart.destroy();

            trendChart = new Chart(
                document.getElementById("foreignerTrendChart"),
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
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
                                align: 'top',
                                font: { weight: 'bold', size: 12 },
                                formatter: function(value, context) {
                                    const index = context.dataIndex;
                                    return value.toLocaleString() +
                                           "\n(" + crimes[index] + ")";
                                }
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

/* ---------------- APPLY ---------------- */
function applyFilters() {

    const year  = document.getElementById("yearFilter").value;
    const crime = document.getElementById("crimeFilter").value;

    if (year === "all" && crime === "all") {
        loadTrendChart();
    } else {
        document.getElementById("trendSection").style.display = "none";
        loadTable(year, crime);
    }
}

/* ---------------- RESET ---------------- */
function resetFilters() {

    document.getElementById("yearFilter").value  = "all";
    document.getElementById("crimeFilter").value = "all";

    toggleCrimeFilter("all");

    loadCrimes("all").then(() => {
        loadTrendChart();
    });
}


/* ---------------- DOM READY ---------------- */
document.addEventListener("DOMContentLoaded", () => {

    const yearFilter = document.getElementById("yearFilter");

    // Initial state
    toggleCrimeFilter(yearFilter.value);

    loadCrimes(yearFilter.value).then(() => {
        if (yearFilter.value === "all") {
            loadTrendChart();
        } else {
            loadTable(yearFilter.value, "all");
        }
    });

    document.getElementById("applyBtn")
        .addEventListener("click", applyFilters);

    document.getElementById("resetBtn")
        .addEventListener("click", resetFilters);

    yearFilter.addEventListener("change", (e) => {

        const year = e.target.value;

        toggleCrimeFilter(year);

        loadCrimes(year).then(() => {

            if (year === "all") {
                loadTrendChart();
            } else {
                loadTable(year, "all");
            }
        });
    });
});



function toggleCrimeFilter(year) {

    const wrapper = document.getElementById("crimeFilterWrapper");

    if (year === "all") {
        wrapper.style.display = "none";
        document.getElementById("crimeFilter").value = "all";
    } else {
        wrapper.style.display = "block";
    }
}
