let trendChart = null;
let currentPage = 1;
const rowsPerPage = 10;

Chart.register(ChartDataLabels);

/* ---------------- LOAD CRIMES ---------------- */
function loadCrimes(year) {

    if (year === "all") {
        return Promise.resolve(); // important for .then()
    }

    return fetch(`/api/gov-crimes?year=${year}`)
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
function loadTable(year, crime, page = 1) {

    currentPage = page;

    fetch(`/api/gov-data?year=${year}&crime=${crime}&page=${page}&per_page=${rowsPerPage}`)
        .then(res => res.json())
        .then(data => {

            const table = document.getElementById("govTable");
            table.innerHTML = "";

            /* ---------- HEADER ---------- */
            let thead = "<thead><tr>";
            data.columns.forEach((col, index) => {
                if (index === 0) {
                    thead += `<th class="sticky-col">${col}</th>`;
                } else {
                    thead += `<th>${col}</th>`;
                }
            });
            thead += "</tr></thead>";

            /* ---------- BODY ---------- */
            let tbody = "<tbody>";
            data.rows.forEach(row => {
                tbody += "<tr>";

                data.columns.forEach((col, index) => {
                    if (index === 0) {
                        tbody += `<td class="sticky-col">${row[col] ?? ""}</td>`;
                    } else {
                        tbody += `<td>${row[col] ?? ""}</td>`;
                    }
                });

                tbody += "</tr>";
            });
            tbody += "</tbody>";

            table.innerHTML = thead + tbody;

            createPagination(data.total_rows, year, crime);
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

            const trendSection = document.getElementById("trendSection");
            trendSection.style.display = "block";

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

/* ---------------- PAGINATION ---------------- */
function createPagination(totalRows, year, crime) {

    const totalPages = Math.ceil(totalRows / rowsPerPage);
    const pagination = document.getElementById("pagination");

    if (!pagination) return;

    pagination.innerHTML = "";

    for (let i = 1; i <= totalPages; i++) {
        pagination.innerHTML += `
            <button class="page-btn ${i === currentPage ? 'active' : ''}"
                onclick="loadTable('${year}', '${crime}', ${i})">
                ${i}
            </button>
        `;
    }
}

/* ---------------- RESET ---------------- */
function resetFilters() {

    const yearFilter  = document.getElementById("yearFilter");
    const crimeFilter = document.getElementById("crimeFilter");

    const trendSection = document.getElementById("trendSection");
    const tableSection = document.querySelector(".table-section");
    const pagination   = document.getElementById("pagination");

    yearFilter.value  = "all";
    crimeFilter.value = "all";

    const crimeWrapper = document.getElementById("crimeFilterWrapper");
    if (crimeWrapper) crimeWrapper.style.display = "none";

    if (trendChart) {
        trendChart.destroy();
        trendChart = null;
    }

    if (pagination) pagination.innerHTML = "";

    tableSection.style.display = "none";
    trendSection.style.display = "block";

    loadTrendChart();
}

/* ---------------- TOGGLE CRIME FILTER ---------------- */
function toggleCrimeFilter(year) {

    const crimeWrapper = document.getElementById("crimeFilterWrapper");
    if (!crimeWrapper) return;

    if (year === "all") {
        crimeWrapper.style.display = "none";
    } else {
        crimeWrapper.style.display = "block";
    }
}

/* ---------------- DOM READY ---------------- */
document.addEventListener("DOMContentLoaded", () => {

    const yearFilter  = document.getElementById("yearFilter");
    const crimeFilter = document.getElementById("crimeFilter");

    const trendSection = document.getElementById("trendSection");
    const tableSection = document.querySelector(".table-section");
    const pagination   = document.getElementById("pagination");

    // Initial State → Show Trend Only
    toggleCrimeFilter("all");
    trendSection.style.display = "block";
    tableSection.style.display = "none";
    loadTrendChart();

    /* YEAR CHANGE */
    yearFilter.addEventListener("change", (e) => {

        const selectedYear = e.target.value;
        toggleCrimeFilter(selectedYear);

        if (selectedYear === "all") {

            tableSection.style.display = "none";
            trendSection.style.display = "block";
            if (pagination) pagination.innerHTML = "";
            loadTrendChart();
            return;
        }

        trendSection.style.display = "none";
        tableSection.style.display = "block";

        loadCrimes(selectedYear).then(() => {
            crimeFilter.value = "all";
            loadTable(selectedYear, "all", 1);
        });
    });

    /* CRIME CHANGE */
    crimeFilter.addEventListener("change", () => {

        const year  = yearFilter.value;
        const crime = crimeFilter.value;

        if (year !== "all") {
            loadTable(year, crime, 1);
        }
    });

    /* RESET BUTTON */
    document.getElementById("resetBtn")
        .addEventListener("click", resetFilters);
});
