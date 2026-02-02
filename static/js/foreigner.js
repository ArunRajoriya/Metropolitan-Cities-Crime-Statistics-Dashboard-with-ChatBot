function loadCrimes(year) {
    return fetch(`/api/foreigner-crimes?year=${year}`)
        .then(res => res.json())
        .then(data => {
            const crimeSelect = document.getElementById("crimeFilter");
            crimeSelect.innerHTML = `<option value="all">All</option>`;

            data.crimes.forEach(c => {
                crimeSelect.innerHTML += `<option value="${c}">${c}</option>`;
            });
        });
}

function loadTable(year, crime) {
    fetch(`/api/foreigner-data?year=${year}&crime=${crime}`)
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("foreignerTable");
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

document.addEventListener("DOMContentLoaded", () => {

    const yearSelect = document.getElementById("yearFilter");
    const crimeSelect = document.getElementById("crimeFilter");
    const applyBtn = document.getElementById("applyBtn");

    // Initial load
    loadCrimes("2020").then(() => {
        loadTable("2020", "all");
    });

    // When year changes → reload crimes AND reset to "all"
    yearSelect.addEventListener("change", () => {
        loadCrimes(yearSelect.value).then(() => {
            crimeSelect.value = "all";
        });
    });

    // Apply button
    applyBtn.addEventListener("click", () => {
        const year = yearSelect.value;
        const crime = crimeSelect.value || "all";
        loadTable(year, crime);
    });
});
