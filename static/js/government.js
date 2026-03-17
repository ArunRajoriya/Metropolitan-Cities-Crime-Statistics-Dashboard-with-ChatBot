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

/* ---------------- LOAD CRIMES ---------------- */
function loadCrimes(year) {

    if (year === "all") {
        return Promise.resolve(); // important for .then()
    }

    return fetch(`/api/gov-crimes?year=${year}`)
        .then(res => res.json())
        .then(data => {

            const crimeSelect = document.getElementById("crimeFilter");
            crimeSelect.innerHTML = `<option value="all">All Categories</option>`;

            data.crimes.forEach(c => {
                crimeSelect.innerHTML += `<option value="${c}">${c}</option>`;
            });
        });
}

/* ---------------- LOAD TABLE ---------------- */
function loadTable(year, crime, page = 1) {
    currentPage = page;
    
    // Show loading state
    const table = document.getElementById("govTable");
    table.innerHTML = '<div class="table-loading">Loading government crime data...</div>';

    fetch(`/api/gov-data?year=${year}&crime=${crime}&page=${page}&per_page=${rowsPerPage}`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            table.innerHTML = "";

            if (!data.rows || data.rows.length === 0) {
                table.innerHTML = '<div class="table-empty">No data found for the selected criteria.</div>';
                return;
            }

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

            createPagination(data.total_rows, year, crime);
        })
        .catch(error => {
            console.error('Error loading table:', error);
            table.innerHTML = `<div class="table-error">Error loading data: ${error.message}</div>`;
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
                            backgroundColor: [
                                '#3b82f6',
                                '#10b981', 
                                '#f59e0b'
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
        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            
            // Debounce search to avoid too many operations
            searchTimeout = setTimeout(() => {
                const searchTerm = e.target.value.toLowerCase().trim();
                const tableRows = document.querySelectorAll('#govTable tbody tr');
                let visibleCount = 0;
                
                tableRows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    const isVisible = searchTerm === '' || text.includes(searchTerm);
                    row.style.display = isVisible ? '' : 'none';
                    if (isVisible) visibleCount++;
                });
                
                // Update search results indicator
                updateSearchResults(visibleCount, tableRows.length, searchTerm);
            }, 300);
        });
        
        // Clear search functionality
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                searchInput.value = '';
                const tableRows = document.querySelectorAll('#govTable tbody tr');
                tableRows.forEach(row => row.style.display = '');
                updateSearchResults(tableRows.length, tableRows.length, '');
            }
        });
    }
}

function updateSearchResults(visible, total, searchTerm) {
    let indicator = document.getElementById('search-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'search-indicator';
        indicator.className = 'search-indicator';
        const searchBox = document.querySelector('.search-box');
        if (searchBox) {
            searchBox.appendChild(indicator);
        }
    }
    
    if (searchTerm) {
        indicator.textContent = `Showing ${visible} of ${total} results`;
        indicator.style.display = 'block';
    } else {
        indicator.style.display = 'none';
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
            const table = document.getElementById('govTable');
            const rows = Array.from(table.querySelectorAll('tr'));
            const csv = rows.map(row => {
                const cells = Array.from(row.querySelectorAll('th, td'));
                return cells.map(cell => `"${cell.textContent}"`).join(',');
            }).join('\n');
            
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `government_crime_data_${year}_${crime}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
        });
    }
}

/* ---------------- RESET ---------------- */
function resetFilters() {

    const yearFilter  = document.getElementById("yearFilter");
    const crimeFilter = document.getElementById("crimeFilter");

    const trendSection = document.getElementById("trendSection");
    const dataSection = document.querySelector(".data-section");
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

    dataSection.style.display = "none";
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
    const dataSection = document.querySelector(".data-section");
    const pagination   = document.getElementById("pagination");

    // Initialize additional features
    initializeSearch();
    initializeExport();

    // Initial State → Show Trend Only
    toggleCrimeFilter("all");
    trendSection.style.display = "block";
    dataSection.style.display = "none";
    loadTrendChart();

    /* YEAR CHANGE */
    yearFilter.addEventListener("change", (e) => {

        const selectedYear = e.target.value;
        toggleCrimeFilter(selectedYear);

        if (selectedYear === "all") {

            dataSection.style.display = "none";
            trendSection.style.display = "block";
            if (pagination) pagination.innerHTML = "";
            loadTrendChart();
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
