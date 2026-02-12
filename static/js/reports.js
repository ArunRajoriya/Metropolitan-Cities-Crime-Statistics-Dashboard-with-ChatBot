document.addEventListener("DOMContentLoaded", () => {

    fetch("/api/reports-summary")
        .then(res => res.json())
        .then(data => {

            document.getElementById("totalArrestsText").innerHTML =
                `Total recorded arrests across years: <strong>${data.total_arrests.toLocaleString()}</strong>`;

            document.getElementById("urbanConcentrationText").innerHTML =
                `<strong>${data.top10_concentration}%</strong> of total arrests are concentrated in the top 10 cities`;

            document.getElementById("juvenileText").innerHTML =
                `Juveniles account for only <strong>${data.juvenile_pct}%</strong> of total arrests`;

            document.getElementById("genderText").innerHTML =
                `Male arrests are <strong>${data.gender_ratio}×</strong> higher than female arrests`;
        });

});
