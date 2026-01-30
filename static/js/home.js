document.addEventListener("DOMContentLoaded", () => {

    fetch("/api/home-kpis")
        .then(res => res.json())
        .then(data => {

            // ---- Population KPIs ----
            document.getElementById("kpi-total").innerText =
                data.total_population.toLocaleString();

            document.getElementById("kpi-male-pop").innerText =
                data.male_population.toLocaleString();

            document.getElementById("kpi-female-pop").innerText =
                data.female_population.toLocaleString();

            // ---- Crime KPI ----
            document.getElementById("kpi-concentration").innerText =
                data.crime_concentration + "%";
        })
        .catch(err => console.error("Home KPI error:", err));
});
