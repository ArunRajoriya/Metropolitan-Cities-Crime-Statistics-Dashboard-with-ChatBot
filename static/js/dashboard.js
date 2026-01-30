let cityChart;
let profileChart;

/* ---------------- LOAD CITIES ---------------- */
function loadCities(year) {
    fetch(`/api/cities?year=${year}`)
        .then(res => res.json())
        .then(data => {
            const citySelect = document.getElementById("cityFilter");
            citySelect.innerHTML = `<option value="all">All</option>`;

            data.cities.forEach(city => {
                const opt = document.createElement("option");
                opt.value = city;
                opt.textContent = city;
                citySelect.appendChild(opt);
            });
        });
}

/* ---------------- PIE CHART (Total vs Filtered) ---------------- */
function loadPie(grand, filtered) {

    if (cityChart) cityChart.destroy();

    cityChart = new Chart(
    document.getElementById("cityChart"),
    {
        type: "doughnut",
        data: {
            labels: ["Total Arrested", "Filtered Arrested"],
            datasets: [{
                data: [grand, filtered],
                backgroundColor: ['#0c0c0e', '#f40a0a']
            }]
        },
        options: {
            cutout: "45%",
            plugins: {
                legend: { position: "right" }
            }
        }
    }
);
}

/* ---------------- CITY PROFILE BAR CHART ---------------- */
function loadCityProfile(year, city) {

    fetch(`/api/city-profile?year=${year}&city=${city}`)
        .then(res => res.json())
        .then(data => {

            const labels = Object.keys(data);
            const values = Object.values(data);

            if (profileChart) profileChart.destroy();

            profileChart = new Chart(
                document.getElementById("profileChart"),
                {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            label: "Arrest Count",
                            data: values,
                            backgroundColor: '#339ee5'
                        }]
                    },
                    options: {
                        responsive: true,
                        indexAxis: 'y',
                        plugins: { legend: { display: false } }
                    }
                }
            );
        });
}

/* ---------------- APPLY FILTERS ---------------- */
function applyFilters() {

    const year   = yearFilter.value;
    const city   = cityFilter.value;
    const age    = ageFilter.value;
    const gender = genderFilter.value;

    fetch(`/api/filter?year=${year}&city=${city}&age=${age}&gender=${gender}`)
        .then(res => res.json())
        .then(data => {
            loadPie(data.grand_total, data.filtered_total);
        });

    if (city !== "all") {
        loadCityProfile(year, city);
    }
}

/* ---------------- DOM READY ---------------- */
document.addEventListener("DOMContentLoaded", () => {

    // Initial cities
    loadCities("2020");

    // Initial empty pie
    loadPie(0, 0);

    // Events
    yearFilter.addEventListener("change", () => {
        loadCities(yearFilter.value);
    });

    document.getElementById("applyBtn")
        .addEventListener("click", applyFilters);
});
