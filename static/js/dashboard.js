let cityChart = null;
let profileChart = null;
let yearChart = null;
let cityComparisonChart = null;
let ageGenderChart = null;

Chart.register(ChartDataLabels);

/* ---------- COMMON CHART OPTIONS ---------- */
function chartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: { enabled: false },
            datalabels: {
                anchor: 'end',
                align: 'top-right',
                formatter: (v) => v,
                font: { weight: 'bold', size: 14 }
            }
        },
        scales: {
            y: { beginAtZero: true }
        }
    };
}

/* ---------- SECTION CONTROL ---------- */
function showOnly(sectionId) {
    const sections = [
        "yearCharts",
        "cityComparisonSection",
        "ageGenderTrendSection",
        "mainCharts"
    ];
    sections.forEach(id => {
        document.getElementById(id).style.display = (id === sectionId) ? "block" : "none";
    });
}

/* ---------- DESTROY ALL ---------- */
function destroyAllCharts() {
    if (cityChart) cityChart.destroy();
    if (profileChart) profileChart.destroy();
    if (yearChart) yearChart.destroy();
    if (cityComparisonChart) cityComparisonChart.destroy();
    if (ageGenderChart) ageGenderChart.destroy();
}

/* ---------- LOADERS ---------- */

function loadCities(year) {
    return fetch(`/api/cities?year=${year}`)
        .then(res => res.json())
        .then(data => {
            const cityFilter = document.getElementById("cityFilter");
            cityFilter.innerHTML = `<option value="all">All</option>`;
            data.cities.forEach(c =>
                cityFilter.innerHTML += `<option value="${c}">${c}</option>`
            );
        });
}

function loadYearTrend() {
    fetch("/api/year-trend")
        .then(res => res.json())
        .then(data => {
            yearChart = new Chart(
                document.getElementById("yearTrendChart"), {
                    type: "bar",
                    data: {
                        labels: Object.keys(data),
                        datasets: [{ data: Object.values(data), borderRadius: 8, barThickness: 50 }]
                    },
                    options: chartOptions()
                }
            );
        });
}

function loadCityComparison(year) {
    fetch(`/api/city-comparison?year=${year}`)
        .then(res => res.json())
        .then(data => {
            cityComparisonChart = new Chart(
                document.getElementById("cityComparisonChart"), {
                    type: "bar",
                    data: {
                        labels: Object.keys(data),
                        datasets: [{ data: Object.values(data), borderRadius: 8, barThickness: 40 }]
                    },
                    options: chartOptions()
                }
            );
        });
}

function loadGenderCityComparison(gender) {
    fetch(`/api/gender-city-comparison?gender=${gender}`)
        .then(res => res.json())
        .then(data => {
            cityComparisonChart = new Chart(
                document.getElementById("cityComparisonChart"), {
                    type: "bar",
                    data: {
                        labels: Object.keys(data),
                        datasets: [{ data: Object.values(data), borderRadius: 8, barThickness: 40 }]
                    },
                    options: chartOptions()
                }
            );
        });
}

function loadAgeGenderTrend(age, gender) {
    fetch(`/api/age-gender-trend?age=${age}&gender=${gender}`)
        .then(res => res.json())
        .then(data => {
            ageGenderChart = new Chart(
                document.getElementById("ageGenderTrendChart"), {
                    type: "bar",
                    data: {
                        labels: Object.keys(data),
                        datasets: [{ data: Object.values(data), borderRadius: 8, barThickness: 60 }]
                    },
                    options: chartOptions()
                }
            );
        });
}

function loadPie(grand, filtered) {

    let labels = [];
    let values = [];

    // If both numbers are equal → show only ONE bar
    if (grand === filtered) {
        labels = ["Total Arrested"];
        values = [grand];
    } else {
        labels = ["Total Arrested", "Filtered Arrested"];
        values = [grand, filtered];
    }

    cityChart = new Chart(
        document.getElementById("cityChart"),
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
            options: chartOptions()
        }
    );
}


function loadCityProfile(year, city, age, gender) {
    fetch(`/api/city-profile?year=${year}&city=${city}&age=${age}&gender=${gender}`)
        .then(res => res.json())
        .then(data => {
            profileChart = new Chart(
                document.getElementById("profileChart"), {
                    type: "bar",
                    data: {
                        labels: Object.keys(data),
                        datasets: [{ data: Object.values(data), borderRadius: 8, barThickness: 35 }]
                    },
                    options: chartOptions()
                }
            );
        });
}

/* ---------- APPLY FILTERS (CORE LOGIC) ---------- */

function applyFilters() {

    const year   = document.getElementById("yearFilter").value;
    const city   = document.getElementById("cityFilter").value;
    const age    = document.getElementById("ageFilter").value;
    const gender = document.getElementById("genderFilter").value;

    destroyAllCharts();

    // 1️⃣ All all → Year trend
    if (year === "all" && city === "all" && age === "all" && gender === "all") {
        showOnly("yearCharts");
        loadYearTrend();
        return;
    }

    // 6️⃣ Year selected + City All + Age/Gender selected
if (year !== "all" && city === "all" && (age !== "all" || gender !== "all")) {
    showOnly("cityComparisonSection");
    loadYearFilteredCityComparison(year, age, gender);
    return;
}


    // 2️⃣ Year selected, city all
    if (year !== "all" && city === "all" && age === "all" && gender === "all") {
        showOnly("cityComparisonSection");
        loadCityComparison(year);
        return;
    }

    // 3️⃣ All years, gender selected
    if (year === "all" && city === "all" && age === "all" && gender !== "all") {
        showOnly("cityComparisonSection");
        loadGenderCityComparison(gender);
        return;
    }
    // 4️⃣ All years, age selected, gender all → Age trend
if (year === "all" && city === "all" && age !== "all" && gender === "all") {
    showOnly("ageGenderTrendSection");
    loadAgeTrend(age);
    return;
}

// Year selected, city all, gender selected → Gender city comparison for that year
if (year !== "all" && city === "all" && age === "all" && gender !== "all") {
    showOnly("cityComparisonSection");
    loadYearGenderCityComparison(year, gender);
    return;
}


    // 4️⃣ All years, age & gender selected
    if (year === "all" && city === "all" && age !== "all" && gender !== "all") {
        showOnly("ageGenderTrendSection");
        loadAgeGenderTrend(age, gender);
        return;
    }

    // 5️⃣ City selected → detailed
    showOnly("mainCharts");

    fetch(`/api/filter?year=${year}&city=${city}&age=${age}&gender=${gender}`)
        .then(res => res.json())
        .then(data => loadPie(data.grand_total, data.filtered_total));

    if (city !== "all") {
        loadCityProfile(year, city, age, gender);
    }
}

/* ---------- INIT ---------- */

document.addEventListener("DOMContentLoaded", () => {

    const yearFilter = document.getElementById("yearFilter");
    const applyBtn   = document.getElementById("applyBtn");
    const resetBtn   = document.getElementById("resetBtn");

    yearFilter.addEventListener("change", () => loadCities(yearFilter.value));
    applyBtn.addEventListener("click", applyFilters);

    resetBtn.addEventListener("click", () => {
        yearFilter.value = "all";
        document.getElementById("cityFilter").value = "all";
        document.getElementById("ageFilter").value = "all";
        document.getElementById("genderFilter").value = "all";
        loadCities("all").then(applyFilters);
    });

    loadCities("all").then(applyFilters);
});

function loadAgeTrend(age) {
    fetch(`/api/age-trend?age=${age}`)
        .then(res => res.json())
        .then(data => {
            ageGenderChart = new Chart(
                document.getElementById("ageGenderTrendChart"), {
                    type: "bar",
                    data: {
                        labels: Object.keys(data),
                        datasets: [{
                            data: Object.values(data),
                            borderRadius: 8,
                            barThickness: 60
                        }]
                    },
                    options: chartOptions()
                }
            );
        });
}

function loadYearGenderCityComparison(year, gender) {
    fetch(`/api/year-gender-city?year=${year}&gender=${gender}`)
        .then(res => res.json())
        .then(data => {
            cityComparisonChart = new Chart(
                document.getElementById("cityComparisonChart"), {
                    type: "bar",
                    data: {
                        labels: Object.keys(data),
                        datasets: [{
                            data: Object.values(data),
                            borderRadius: 8,
                            barThickness: 40
                        }]
                    },
                    options: chartOptions()
                }
            );
        });
}

function loadYearFilteredCityComparison(year, age, gender) {

    fetch(`/api/year-city-filter?year=${year}&age=${age}&gender=${gender}`)
        .then(res => res.json())
        .then(data => {

            if (cityComparisonChart) cityComparisonChart.destroy();

            cityComparisonChart = new Chart(
                document.getElementById("cityComparisonChart"),
                {
                    type: "bar",
                    data: {
                        labels: Object.keys(data),
                        datasets: [{
                            data: Object.values(data),
                            borderRadius: 8,
                            barThickness: 40
                        }]
                    },
                    options: chartOptions()
                }
            );
        });
}
