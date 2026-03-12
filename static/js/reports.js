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

document.addEventListener("DOMContentLoaded", () => {

    fetch("/api/reports-summary")
        .then(res => res.json())
        .then(data => {

            document.getElementById("totalArrestsText").innerHTML =
                `Total recorded arrests across years: <strong>${formatIndianNumber(data.total_arrests)}</strong>`;

            document.getElementById("urbanConcentrationText").innerHTML =
                `<strong>${data.top10_concentration}%</strong> of total arrests are concentrated in the top 10 cities`;

            document.getElementById("juvenileText").innerHTML =
                `Juveniles account for only <strong>${data.juvenile_pct}%</strong> of total arrests`;

            document.getElementById("genderText").innerHTML =
                `Male arrests are <strong>${data.gender_ratio}×</strong> higher than female arrests`;
        });

});
