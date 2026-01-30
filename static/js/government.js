function loadCrimes(year) {
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

function loadTable(year, crime) {
    fetch(`/api/gov-data?year=${year}&crime=${crime}`)
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("govTable");
            table.innerHTML = "";

            // Header
            let header = "<tr>";
            data.columns.forEach(col => {
                header += `<th>${col}</th>`;
            });
            header += "</tr>";
            table.innerHTML += header;

            // Rows
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
    loadCrimes("2020");
    loadTable("2020", "all");

    document.getElementById("applyBtn").addEventListener("click", () => {
        const year = document.getElementById("yearFilter").value;
        const crime = document.getElementById("crimeFilter").value;
        loadTable(year, crime);
    });

    document.getElementById("yearFilter").addEventListener("change", (e) => {
        loadCrimes(e.target.value);
    });
});
