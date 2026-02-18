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

        layout: {
            padding: {
                top: 30   // 🔥 prevents label from going out of scale
            }
        },

        plugins: {
            legend: { display: false },
            tooltip: { enabled: false },
            datalabels: {
                anchor: 'end',
                align: 'top',
                offset: 2,
                formatter: (v) => v,
                font: { weight: 'bold', size: 14 }
            }
        },

        scales: {
            y: {
                beginAtZero: true
            }
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

            const labels = Object.keys(data);
            const values = Object.values(data);

            const maxValue = Math.max(...values);

            // Professional color palette for other bars
            const colorPalette = [
                "#91a7eb", "#92f3cf", "#83e1f0",
                "#f3d381", "#858796", "#95a1f6",
                "#7deccb", "#a77eeb"
            ];

            let colorIndex = 0;

            const backgroundColors = values.map(value => {
                if (value === maxValue) {
                    return "#ff0000"; // Extreme Red for highest
                } else {
                    const color = colorPalette[colorIndex % colorPalette.length];
                    colorIndex++;
                    return color;
                }
            });

            yearChart = new Chart(
                document.getElementById("yearTrendChart"),
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: backgroundColors,
                            borderRadius: 8,
                            barThickness: 50
                        }]
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

            const labels = Object.keys(data);
            const values = Object.values(data);

            const maxValue = Math.max(...values);

            const colorPalette = [
                "#8fa7ee", "#8bf2cc", "#92e7f5",
                "#ffeab6", "#b292ec", "#a1fadf",
                "#be9676", "#be98fd", "#78aab2"
            ];

            let colorIndex = 0;

            const backgroundColors = values.map(value => {
                if (value === maxValue) {
                    return "#ff0000"; // 🔴 Extreme Red for highest
                } else {
                    const color = colorPalette[colorIndex % colorPalette.length];
                    colorIndex++;
                    return color;
                }
            });

            cityComparisonChart = new Chart(
                document.getElementById("cityComparisonChart"),
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: backgroundColors,
                            borderRadius: 8,
                            barThickness: 40
                        }]
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

            const labels = Object.keys(data);
            const values = Object.values(data);

            const maxValue = Math.max(...values);
            const maxIndex = values.indexOf(maxValue);

            const colorPalette = [
                "#c7d2fe",
                "#bbf7d0",
                "#bae6fd",
                "#fde68a",
                "#e9d5ff",
                "#a7f3d0",
                "#fed7aa",
                "#ddd6fe",
                "#bfdbfe"
            ];

            const backgroundColors = values.map((value, index) =>
                index === maxIndex
                    ? "#ff0000"
                    : colorPalette[index % colorPalette.length]
            );

            if (cityComparisonChart) cityComparisonChart.destroy();

            cityComparisonChart = new Chart(
                document.getElementById("cityComparisonChart"),
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: backgroundColors,
                            borderRadius: 8,
                            barThickness: 40
                        }]
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

            const labels = Object.keys(data);
            const values = Object.values(data);

            const maxValue = Math.max(...values);

            // 🌈 Light professional palette
            const colorPalette = [
                "#9db4f0", "#8cf0d0", "#8ee6f5",
                "#ffe8a3", "#c5a3f7", "#a8f5df",
                "#f7c59f", "#c7b6ff", "#9ed0d6"
            ];

            let colorIndex = 0;

            const backgroundColors = values.map(value => {
                if (value === maxValue) {
                    return "#ff0000"; // 🔴 Extreme Red for highest
                } else {
                    const color = colorPalette[colorIndex % colorPalette.length];
                    colorIndex++;
                    return color;
                }
            });

            ageGenderChart = new Chart(
                document.getElementById("ageGenderTrendChart"),
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: backgroundColors,
                            borderRadius: 8,
                            barThickness: 60
                        }]
                    },
                    options: chartOptions()
                }
            );
        });
}


function loadPie(grand, filtered) {

    const year   = document.getElementById("yearFilter").value;
    const city   = document.getElementById("cityFilter").value;
    const age    = document.getElementById("ageFilter").value;
    const gender = document.getElementById("genderFilter").value;

    const isFiltered =
        year !== "all" ||
        city !== "all" ||
        age !== "all" ||
        gender !== "all";

    let labels = [];
    let values = [];
    let colors = [];

    if (grand === filtered) {
        labels = ["Total Arrested"];
        values = [grand];
        colors = [isFiltered ? "#ff6b6b" : "#92a6e3"];
    } else {
        labels = ["Total Arrested", "Filtered Arrested"];
        values = [grand, filtered];
        colors = [
            "#8399dc",              // Total → default blue
            isFiltered ? "#ff6b6b"  // Filtered → red if filtered
                       : "#8ea5ec"
        ];
    }

    cityChart = new Chart(
        document.getElementById("cityChart"),
        {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderRadius: 8,
                    barThickness: 40
                    
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

            const labels = Object.keys(data);
            const values = Object.values(data);

            const ageMap = {
                "18-30": "18 and above and below 30 years",
                "30-45": "30 and above and below 45 years",
                "45-60": "45 and above and below 60 years",
                "60 years and above": "60 years and above"
            };

            let colors = [];

            labels.forEach(label => {

                let color = "#a1b6f6"; // default blue

                // 🔴 AGE + GENDER
                if (age !== "all" && gender !== "all") {
                    if (
                        label.startsWith(ageMap[age]) &&
                        label.includes(gender.charAt(0).toUpperCase())
                    ) {
                        color = "#e74a3b";
                    }
                }

                // 🟡 AGE only
                else if (age !== "all" && gender === "all") {
                    if (
                        label.startsWith(ageMap[age]) &&
                        label.includes("Total")
                    ) {
                        color = "#f32222";
                    }
                }

                // 🟢 GENDER only
                else if (age === "all" && gender !== "all") {
                    if (
                        label.endsWith(`- ${gender.charAt(0).toUpperCase() + gender.slice(1)}`)
                    ) {
                        color = "#8bf3cd";
                    }
                }

                colors.push(color);
            });

            if (profileChart) profileChart.destroy();

            profileChart = new Chart(
                document.getElementById("profileChart"),
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: colors,
                            borderRadius: 10,
                            
                        }]
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

    const warning = document.getElementById("filterWarning");

const isFiltered =
    year !== "all" ||
    city !== "all" ||
    age !== "all" ||
    gender !== "all";

if (isFiltered) {
    warning.classList.add("active");
} else {
    warning.classList.remove("active");
}


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

    const yearFilter   = document.getElementById("yearFilter");
    const cityFilter   = document.getElementById("cityFilter");
    const ageFilter    = document.getElementById("ageFilter");
    const genderFilter = document.getElementById("genderFilter");
    const resetBtn     = document.getElementById("resetBtn");

    // 🔥 AUTO APPLY ON CHANGE
    yearFilter.addEventListener("change", () => {
        loadCities(yearFilter.value).then(applyFilters);
    });

    cityFilter.addEventListener("change", applyFilters);
    ageFilter.addEventListener("change", applyFilters);
    genderFilter.addEventListener("change", applyFilters);

    // RESET
    resetBtn.addEventListener("click", () => {
        yearFilter.value = "all";
        cityFilter.value = "all";
        ageFilter.value = "all";
        genderFilter.value = "all";
        loadCities("all").then(applyFilters);
    });

    // Initial load
    loadCities("all").then(applyFilters);
});

function loadAgeTrend(age) {

    fetch(`/api/age-trend?age=${age}`)
        .then(res => res.json())
        .then(data => {

            const labels = Object.keys(data);
            const values = Object.values(data);

            const maxValue = Math.max(...values);

            // 🌈 Light dashboard color palette
            const colorPalette = [
                "#9db4f0", "#8cf0d0", "#8ee6f5",
                "#ffe8a3", "#c5a3f7", "#a8f5df",
                "#f7c59f", "#c7b6ff", "#9ed0d6"
            ];

            let colorIndex = 0;

            const backgroundColors = values.map(value => {
                if (value === maxValue) {
                    return "#ff0000"; // 🔴 Extreme Red
                } else {
                    const color = colorPalette[colorIndex % colorPalette.length];
                    colorIndex++;
                    return color;
                }
            });

            ageGenderChart = new Chart(
                document.getElementById("ageGenderTrendChart"),
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: backgroundColors,
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

            const labels = Object.keys(data);
            const values = Object.values(data);

            const maxValue = Math.max(...values);
            const maxIndex = values.indexOf(maxValue);

            const colorPalette = [
                "#c7d2fe",
                "#bbf7d0",
                "#bae6fd",
                "#fde68a",
                "#e9d5ff",
                "#a7f3d0",
                "#fed7aa",
                "#ddd6fe",
                "#bfdbfe"
            ];

            const backgroundColors = values.map((value, index) =>
                index === maxIndex
                    ? "#ff0000"   // 🔴 Extreme red for highest
                    : colorPalette[index % colorPalette.length]
            );

            if (cityComparisonChart) cityComparisonChart.destroy();

            cityComparisonChart = new Chart(
                document.getElementById("cityComparisonChart"),
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: backgroundColors,
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

            const labels = Object.keys(data);
            const values = Object.values(data);

            const maxValue = Math.max(...values);
            const maxIndex = values.indexOf(maxValue); // only first highest

            // 🌈 Light pastel palette
            const colorPalette = [
                "#c7d2fe",
                "#bbf7d0",
                "#bae6fd",
                "#fde68a",
                "#e9d5ff",
                "#a7f3d0",
                "#fed7aa",
                "#ddd6fe",
                "#bfdbfe"
            ];

            const backgroundColors = values.map((value, index) =>
                index === maxIndex
                    ? "#ff0000"   // 🔴 Extreme Red for highest
                    : colorPalette[index % colorPalette.length]
            );

            if (cityComparisonChart) cityComparisonChart.destroy();

            cityComparisonChart = new Chart(
                document.getElementById("cityComparisonChart"),
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: backgroundColors,
                            borderRadius: 8,
                            barThickness: 40
                        }]
                    },
                    options: chartOptions()
                }
            );
        });
}

