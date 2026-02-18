let trendChart = null;
Chart.register(ChartDataLabels);

/* ---------------- LOAD CRIMES ---------------- */
function loadCrimes(year) {

    if (year === "all") {
        return Promise.resolve();
    }

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

    const trendSection = document.getElementById("trendSection");
    const tableSection = document.querySelector(".table-section");

    trendSection.style.display = "none";
    tableSection.style.display = "block";

    fetch(`/api/foreigner-data?year=${year}&crime=${crime}`)
        .then(res => res.json())
        .then(data => {

            const table = document.getElementById("foreignerTable");
            table.innerHTML = "";

            let thead = "<thead><tr>";
            data.columns.forEach(col => {
                thead += `<th>${col}</th>`;
            });
            thead += "</tr></thead>";

            let tbody = "<tbody>";
            data.rows.forEach(row => {
                tbody += "<tr>";
                data.columns.forEach(col => {
                    tbody += `<td>${row[col] ?? ""}</td>`;
                });
                tbody += "</tr>";
            });
            tbody += "</tbody>";

            table.innerHTML = thead + tbody;
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
                            tooltip: {
                                enabled: true,
                                callbacks: {
                                    label: function(context) {
                                        const index = context.dataIndex;
                                        return crimes[index] + " : " +
                                               values[index].toLocaleString();
                                    }
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

/* ---------------- TOGGLE CRIME FILTER ---------------- */
function toggleCrimeFilter(year) {

    const wrapper = document.getElementById("crimeFilterWrapper");
    const crimeFilter = document.getElementById("crimeFilter");

    if (year === "all") {
        wrapper.style.display = "none";
        crimeFilter.value = "all";
    } else {
        wrapper.style.display = "block";
    }
}

/* ---------------- RESET ---------------- */
function resetFilters() {

    const yearFilter  = document.getElementById("yearFilter");
    const crimeFilter = document.getElementById("crimeFilter");

    yearFilter.value  = "all";
    crimeFilter.value = "all";

    toggleCrimeFilter("all");
    loadTrendChart();
}

/* ---------------- DOM READY ---------------- */
document.addEventListener("DOMContentLoaded", () => {

    const yearFilter  = document.getElementById("yearFilter");
    const crimeFilter = document.getElementById("crimeFilter");

    toggleCrimeFilter("all");

    // Initial state → Trend only
    loadTrendChart();

    /* 🔥 YEAR CHANGE AUTO APPLY */
    yearFilter.addEventListener("change", (e) => {

        const year = e.target.value;
        toggleCrimeFilter(year);

        if (year === "all") {
            loadTrendChart();
        } else {
            loadCrimes(year).then(() => {
                crimeFilter.value = "all";
                loadTable(year, "all");
            });
        }
    });

    /* 🔥 CRIME CHANGE AUTO APPLY */
    crimeFilter.addEventListener("change", () => {

        const year  = yearFilter.value;
        const crime = crimeFilter.value;

        if (year !== "all") {
            loadTable(year, crime);
        }
    });

    /* RESET BUTTON */
    document.getElementById("resetBtn")
        .addEventListener("click", resetFilters);
});
