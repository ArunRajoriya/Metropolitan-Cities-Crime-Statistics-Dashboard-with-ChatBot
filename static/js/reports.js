document.addEventListener("DOMContentLoaded", () => {

    fetch("/api/home-kpis")
        .then(res => res.json())
        .then(d => {

            // 1. Trend
            const trend =
                d.yoy_change >= 0
                ? `National crime increased by ${d.yoy_change}% between 2019 and 2020. 
                   This indicates rising pressure on law enforcement resources.`
                : `National crime declined by ${Math.abs(d.yoy_change)}% between 2019 and 2020, 
                   suggesting improvements in crime prevention or reporting.`;

            document.getElementById("trendText").innerText = trend;

            // 2. Concentration
            document.getElementById("concentrationText").innerText =
                `${d.top10_concentration}% of all arrests are concentrated in the top 10 cities, 
                 highlighting the need for targeted urban policing strategies.`;

            // 3. Juveniles
            document.getElementById("juvenileText").innerText =
                `Juveniles account for ${d.juvenile_share}% of total arrests. 
                 This underscores the importance of early intervention, education, and rehabilitation programs.`;

            // 4. Foreign nationals
            document.getElementById("foreignText").innerText =
                `Crimes involving foreign nationals constitute ${d.foreign_share}% of total arrests. 
                 This data should be interpreted in context and does not indicate disproportionate involvement.`;
        })
        .catch(err => {
            console.error("Report load failed:", err);
        });
});
