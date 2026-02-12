let trendChart = null;
Chart.register(ChartDataLabels);

/* ---------------- LOAD CRIMES ---------------- */
function loadCrimes(year) {

    if (year === "all") return;   // ❗ Don't load crimes for all

    fetch(`/api/gov-crimes?year=${year}`)
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

    fetch(`/api/gov-data?year=${year}&crime=${crime}`)
        .then(res => res.json())
        .then(data => {

            const table = document.getElementById("govTable");
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

    fetch("/api/highest-crime-trend")
        .then(res => res.json())
        .then(data => {

            const labels = Object.keys(data);
            const values = labels.map(y => data[y].value);
            const crimes = labels.map(y => data[y].crime);

            document.getElementById("trendSection").style.display = "block";

            if (trendChart) trendChart.destroy();

            trendChart = new Chart(
                document.getElementById("crimeTrendChart"),
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
                                font: { weight: 'bold', size: 13 },
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

/* ---------------- HIDE TREND ---------------- */
function hideTrend() {
    document.getElementById("trendSection").style.display = "none";
    if (trendChart) {
        trendChart.destroy();
        trendChart = null;
    }
}

/* ---------------- TOGGLE CRIME FILTER ---------------- */
function toggleCrimeFilter(year) {

    const crimeWrapper = document.getElementById("crimeFilterWrapper");
    const crimeFilter  = document.getElementById("crimeFilter");

    if (year === "all") {
        crimeWrapper.style.display = "none";
        crimeFilter.value = "all";
    } else {
        crimeWrapper.style.display = "block";
    }
}

/* ---------------- APPLY ---------------- */
function applyFilters() {

    const year  = document.getElementById("yearFilter").value;
    const crime = document.getElementById("crimeFilter").value;

    const trendSection = document.getElementById("trendSection");
    const tableSection = document.querySelector(".table-section");

    // If both ALL → show trend only
    if (year === "all" && crime === "all") {

        tableSection.style.display = "none";
        trendSection.style.display = "block";
        loadTrendChart();
        return;
    }

    // Otherwise → show table
    trendSection.style.display = "none";
    tableSection.style.display = "block";
    loadTable(year, crime);
}


/* ---------------- RESET ---------------- */
function resetFilters() {

    const yearFilter  = document.getElementById("yearFilter");
    const crimeFilter = document.getElementById("crimeFilter");

    const trendSection = document.getElementById("trendSection");
    const tableSection = document.querySelector(".table-section");

    // 1️⃣ Reset dropdowns
    yearFilter.value  = "all";
    crimeFilter.value = "all";

    // 2️⃣ Hide crime filter wrapper (if exists)
    const crimeWrapper = document.getElementById("crimeFilterWrapper");
    if (crimeWrapper) crimeWrapper.style.display = "none";

    // 3️⃣ Destroy old chart
    if (trendChart) {
        trendChart.destroy();
        trendChart = null;
    }

    // 4️⃣ Hide table section
    if (tableSection) {
        tableSection.style.display = "none";
    }

    // 5️⃣ Show trend section
    trendSection.style.display = "block";

    // 6️⃣ Reload trend chart
    loadTrendChart();
}


/* ---------------- DOM READY ---------------- */
document.addEventListener("DOMContentLoaded", () => {

    const yearFilter = document.getElementById("yearFilter");

    // Initial state
    toggleCrimeFilter("all");
    loadTable("all", "all");
    loadTrendChart();

    document.getElementById("applyBtn")
        .addEventListener("click", applyFilters);

    document.getElementById("resetBtn")
        .addEventListener("click", resetFilters);

    yearFilter.addEventListener("change", (e) => {

        const selectedYear = e.target.value;

        toggleCrimeFilter(selectedYear);

        if (selectedYear !== "all") {
            loadCrimes(selectedYear);
        }
        
    });
});
