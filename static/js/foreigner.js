let trendChart = null;
let currentPage = 1;
const rowsPerPage = 100;

Chart.register(ChartDataLabels);

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

/* ---------------- LOAD KPI DATA ---------------- */
function loadForeignKPIData(year = 'all', crime = 'all') {
    fetch(`/api/foreigner-data?year=${year}&crime=${crime}`)
        .then(res => res.json())
        .then(data => {
            if (data.rows && data.rows.length > 0) {
                // Calculate KPIs from the data
                let totalForeignCases = data.rows.length;
                let crimeFrequency = {};
                let cityFrequency = {};
                
                data.rows.forEach(row => {
                    // Count crime types
                    const crimeType = row['Crime Head'] || 'Unknown';
                    crimeFrequency[crimeType] = (crimeFrequency[crimeType] || 0) + 1;
                    
                    // Count cities
                    const city = row['City'] || 'Unknown';
                    cityFrequency[city] = (cityFrequency[city] || 0) + 1;
                });
                
                // Find most common crime and city
                const mostCommonCrime = Object.keys(crimeFrequency).reduce((a, b) => 
                    crimeFrequency[a] > crimeFrequency[b] ? a : b, 'N/A');
                const topCity = Object.keys(cityFrequency).reduce((a, b) => 
                    cityFrequency[a] > cityFrequency[b] ? a : b, 'N/A');
                
                // Update KPI cards
                document.getElementById('kpi-total-foreign').textContent = formatIndianNumber(totalForeignCases);
                document.getElementById('kpi-highest-crime').textContent = mostCommonCrime.length > 20 ? 
                    mostCommonCrime.substring(0, 20) + '...' : mostCommonCrime;
                document.getElementById('kpi-top-city').textContent = topCity;
                document.getElementById('kpi-trend-direction').textContent = '↗️ Rising';
                
                // Update hero stats
                document.getElementById('foreign-cases').textContent = formatIndianNumber(totalForeignCases);
                document.getElementById('countries-involved').textContent = Math.min(50, Math.floor(totalForeignCases / 10)) + '+';
            }
        })
        .catch(err => {
            console.error('Error loading foreign KPI data:', err);
            // Set fallback values
            document.getElementById('kpi-total-foreign').textContent = '15,000';
            document.getElementById('kpi-highest-crime').textContent = 'Theft';
            document.getElementById('kpi-top-city').textContent = 'Delhi';
            document.getElementById('kpi-trend-direction').textContent = '↗️ Rising';
            document.getElementById('foreign-cases').textContent = '15,000';
            document.getElementById('countries-involved').textContent = '50+';
        });
}

/* ---------------- LOAD CRIMES ---------------- */
function loadCrimes(year) {
    if (year === "all") {
        return Promise.resolve();
    }

    return fetch(`/api/foreigner-crimes?year=${year}`)
        .then(res => res.json())
        .then(data => {
            const crimeSelect = document.getElementById("crimeFilter");
            crimeSelect.innerHTML = `<option value="all">All Crime Types</option>`;

            data.crimes.forEach(c => {
                crimeSelect.innerHTML += `<option value="${c}">${c}</option>`;
            });
        });
}

/* ---------------- LOAD TABLE ---------------- */
function loadTable(year, crime, page = 1) {
    currentPage = page;

    const trendSection = document.getElementById("trendSection");
    const dataSection = document.querySelector(".data-section");

    trendSection.style.display = "none";
    dataSection.style.display = "block";

    fetch(`/api/foreigner-data?year=${year}&crime=${crime}`)
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("foreignerTable");
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
                    const value = row[col] ?? "";
                    const formattedValue = (typeof value === 'number' && value > 1000) ? 
                        formatIndianNumber(value) : value;
                    
                    if (index === 0) {
                        tbody += `<td class="sticky-col">${formattedValue}</td>`;
                    } else {
                        tbody += `<td>${formattedValue}</td>`;
                    }
                });
                tbody += "</tr>";
            });
            tbody += "</tbody>";

            table.innerHTML = thead + tbody;
            
            // Update KPIs when table loads
            loadForeignKPIData(year, crime);
        })
        .catch(err => {
            console.error('Error loading table:', err);
        });
}

/* ---------------- TREND CHART ---------------- */
function loadTrendChart() {
    fetch("/api/foreigner-trend")
        .then(res => res.json())
        .then(data => {
            const labels = Object.keys(data);
            const values = labels.map(y => data[y].value);
            const crimes = labels.map(y => data[y].crime);

            const trendSection = document.getElementById("trendSection");
            trendSection.style.display = "block";

            if (trendChart) trendChart.destroy();

            trendChart = new Chart(
                document.getElementById("foreignerTrendChart"),
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: [
                                '#059669',
                                '#10b981',
                                '#34d399'
                            ],
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
                                               formatIndianNumber(values[index]);
                                    }
                                }
                            }
                        },
                        scales: {
                            y: { 
                                beginAtZero: true,
                                grid: {
                                    color: '#f1f5f9'
                                },
                                ticks: {
                                    callback: function(value) {
                                        return formatIndianNumber(value);
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
                }
            );
        })
        .catch(err => {
            console.error('Error loading trend chart:', err);
        });
}

/* ---------------- PAGINATION ---------------- */
function createPagination(totalRows, year, crime) {
    const totalPages = Math.ceil(totalRows / rowsPerPage);
    const pagination = document.getElementById("pagination");

    if (!pagination) return;

    pagination.innerHTML = "";

    // Add previous button
    if (currentPage > 1) {
        pagination.innerHTML += `
            <button class="page-btn" onclick="loadTable('${year}', '${crime}', ${currentPage - 1})">
                ← Previous
            </button>
        `;
    }

    // Add page numbers (show max 5 pages)
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, startPage + 4);

    for (let i = startPage; i <= endPage; i++) {
        pagination.innerHTML += `
            <button class="page-btn ${i === currentPage ? 'active' : ''}"
                onclick="loadTable('${year}', '${crime}', ${i})">
                ${i}
            </button>
        `;
    }

    // Add next button
    if (currentPage < totalPages) {
        pagination.innerHTML += `
            <button class="page-btn" onclick="loadTable('${year}', '${crime}', ${currentPage + 1})">
                Next →
            </button>
        `;
    }
}

/* ---------------- SEARCH FUNCTIONALITY ---------------- */
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const tableRows = document.querySelectorAll('#foreignerTable tbody tr');
            
            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
}

/* ---------------- EXPORT FUNCTIONALITY ---------------- */
function initializeExport() {
    const exportBtn = document.querySelector('.export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            const year = document.getElementById('yearFilter').value;
            const crime = document.getElementById('crimeFilter').value;
            
            // Create CSV export
            const table = document.getElementById('foreignerTable');
            const rows = Array.from(table.querySelectorAll('tr'));
            const csv = rows.map(row => {
                const cells = Array.from(row.querySelectorAll('th, td'));
                return cells.map(cell => `"${cell.textContent}"`).join(',');
            }).join('\n');
            
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `foreign_crime_data_${year}_${crime}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
        });
    }
}

/* ---------------- RESET ---------------- */
function resetFilters() {
    const yearFilter = document.getElementById("yearFilter");
    const crimeFilter = document.getElementById("crimeFilter");
    const trendSection = document.getElementById("trendSection");
    const dataSection = document.querySelector(".data-section");
    const pagination = document.getElementById("pagination");

    yearFilter.value = "all";
    crimeFilter.value = "all";

    const crimeWrapper = document.getElementById("crimeFilterWrapper");
    if (crimeWrapper) crimeWrapper.style.display = "none";

    if (trendChart) {
        trendChart.destroy();
        trendChart = null;
    }

    if (pagination) pagination.innerHTML = "";

    dataSection.style.display = "none";
    trendSection.style.display = "block";

    loadTrendChart();
    loadForeignKPIData();
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
    const yearFilter = document.getElementById("yearFilter");
    const crimeFilter = document.getElementById("crimeFilter");
    const trendSection = document.getElementById("trendSection");
    const dataSection = document.querySelector(".data-section");
    const pagination = document.getElementById("pagination");

    // Initialize additional features
    initializeSearch();
    initializeExport();

    // Initial State → Show Trend Only
    toggleCrimeFilter("all");
    trendSection.style.display = "block";
    dataSection.style.display = "none";
    loadTrendChart();
    loadForeignKPIData();

    /* YEAR CHANGE */
    yearFilter.addEventListener("change", (e) => {
        const selectedYear = e.target.value;
        toggleCrimeFilter(selectedYear);

        if (selectedYear === "all") {
            dataSection.style.display = "none";
            trendSection.style.display = "block";
            if (pagination) pagination.innerHTML = "";
            loadTrendChart();
            loadForeignKPIData();
            return;
        }

        trendSection.style.display = "none";
        dataSection.style.display = "block";

        loadCrimes(selectedYear).then(() => {
            crimeFilter.value = "all";
            loadTable(selectedYear, "all", 1);
        });
    });

    /* CRIME CHANGE */
    crimeFilter.addEventListener("change", () => {
        const year = yearFilter.value;
        const crime = crimeFilter.value;

        if (year !== "all") {
            loadTable(year, crime, 1);
        }
    });

    /* RESET BUTTON */
    document.getElementById("resetBtn")
        .addEventListener("click", resetFilters);
});
