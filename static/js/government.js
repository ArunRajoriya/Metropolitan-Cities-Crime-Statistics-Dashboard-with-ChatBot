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
    const pagination   = document.getElementById("pagination");

    // 🔥 CASE 1: Both ALL → Show Trend Only
    if (year === "all" && crime === "all") {

        tableSection.style.display = "none";
        trendSection.style.display = "block";

        if (pagination) pagination.innerHTML = "";   // clear pagination

        loadTrendChart();
        return;
    }

    // 🔥 CASE 2: Otherwise → Show Table + Pagination
    trendSection.style.display = "none";
    tableSection.style.display = "block";

    loadTable(year, crime, 1);   // always reset to page 1
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


let currentPage = 1;
const rowsPerPage = 10;

function createPagination(totalRows, year, crime) {

    const totalPages = Math.ceil(totalRows / rowsPerPage);
    const pagination = document.getElementById("pagination");
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

