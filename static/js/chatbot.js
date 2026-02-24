function toggleAssistant(event){
    if(event) event.preventDefault();

    const panel = document.getElementById("assistant-panel");
    const overlay = document.getElementById("assistant-overlay");

    panel.classList.toggle("active");
    overlay.classList.toggle("active");
}

async function sendAssistantQuery(){
    const input = document.getElementById("assistantInput");
    const message = input.value.trim();
    if(!message) return;

    // Show user message
    const body = document.getElementById("assistantBody");

    const userDiv = document.createElement("div");
    userDiv.className = "assistant-user";
    userDiv.innerText = message;
    body.appendChild(userDiv);

    input.value = "";

    // Optional typing indicator
    const typing = document.createElement("div");
    typing.className = "assistant-typing";
    typing.innerText = "Analyzing NCRB dataset...";
    body.appendChild(typing);
    body.scrollTop = body.scrollHeight;

    try{
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await res.json();

        body.removeChild(typing);  // remove typing indicator

        appendAssistantResponse(data);

    } catch(err){
        body.removeChild(typing);

        const errorDiv = document.createElement("div");
        errorDiv.className = "assistant-error";
        errorDiv.innerText = "Unable to process request.";
        body.appendChild(errorDiv);
    }

    body.scrollTop = body.scrollHeight;
}


function appendAssistantResponse(payload){
    const body = document.getElementById("assistantBody");

    if(payload.type === "error"){
        const div = document.createElement("div");
        div.className = "assistant-error";
        div.innerText = payload.summary || payload.message || "Error";
        body.appendChild(div);
        body.scrollTop = body.scrollHeight;
        return;
    }

    const card = document.createElement("div");
    card.className = "assistant-card";

    // Build context text (city / year / years array)
    let contextText = "";
    if(payload.context){
        if(payload.context.city && payload.context.year){
            contextText = `${payload.context.city} | ${payload.context.year}`;
        } else if(payload.context.city){
            contextText = `${payload.context.city}`;
        } else if(payload.context.year){
            contextText = `${payload.context.year}`;
        }
    } else if(Array.isArray(payload.data) && payload.data.length){
        contextText = "";
    }

    // Helper: convert object -> HTML list / table
    function renderValue(key, val){
        // If primitive -> simple metric
        if(val === null || val === undefined) return `<div class="assistant-metric"><span>${key}</span><strong>—</strong></div>`;

        if(typeof val === "number" || typeof val === "string"){
            return `<div class="assistant-metric"><span>${key}</span><strong>${val}</strong></div>`;
        }

        // If it's an object (e.g. { "2016": 86241, "2020": 106503 })
        if(typeof val === "object"){
            // If the object looks like a year->value map, render a small list
            const rows = Object.entries(val).map(([k,v]) => {
                return `<div class="assistant-metric nested"><span>${k}</span><strong>${v}</strong></div>`;
            }).join("");
            return `<div class="assistant-metric-group"><div class="assistant-metric-group-title">${key}</div>${rows}</div>`;
        }

        // fallback stringify
        return `<div class="assistant-metric"><span>${key}</span><strong>${JSON.stringify(val)}</strong></div>`;
    }

    // Special-case: matrix_comparison -> render table
    if(payload.type === "matrix_comparison" && payload.data && typeof payload.data === "object"){
        // gather years (columns) union
        const cities = Object.keys(payload.data);
        const yearSet = new Set();
        cities.forEach(city => {
            const row = payload.data[city];
            Object.keys(row || {}).forEach(y => yearSet.add(y));
        });
        const years = Array.from(yearSet).sort();

        // build table
        let tableHTML = `<div class="assistant-table-wrap"><table class="assistant-table"><thead><tr><th>City</th>${years.map(y=>`<th>${y}</th>`).join("")}</tr></thead><tbody>`;
        for(const city of cities){
            tableHTML += `<tr><td class="city-cell">${city}</td>`;
            for(const y of years){
                const v = (payload.data[city] && payload.data[city][y]) ?? "—";
                tableHTML += `<td>${v}</td>`;
            }
            tableHTML += `</tr>`;
        }
        tableHTML += `</tbody></table></div>`;

        card.innerHTML = `
            <div class="assistant-card-title">${payload.title}</div>
            <div class="assistant-card-sub">${contextText}</div>
            <div class="assistant-divider"></div>
            ${tableHTML}
            <div class="assistant-summary">${payload.summary || ""}</div>
            <div class="assistant-source">${payload.source || ""}</div>
        `;
        body.appendChild(card);
        body.scrollTop = body.scrollHeight;
        return;
    }

    // Generic rendering for other types (multi_city, multi_year_city, comparison, city_profile etc.)
    let dataHTML = "";
    if(payload.data && typeof payload.data === "object"){
        // If top-level data keys map to primitive values, render them as metrics
        // If any value is an object, use renderValue for nested rendering
        for(const key of Object.keys(payload.data)){
            const val = payload.data[key];
            dataHTML += renderValue(key, val);
        }
    } else if(Array.isArray(payload.data)){
        dataHTML = payload.data.map(d => `<div class="assistant-metric"><span>${d}</span></div>`).join("");
    } else {
        dataHTML = `<div class="assistant-metric"><span>Info</span><strong>${JSON.stringify(payload.data)}</strong></div>`;
    }

    card.innerHTML = `
        <div class="assistant-card-title">${payload.title}</div>
        <div class="assistant-card-sub">${contextText}</div>
        <div class="assistant-divider"></div>
        ${dataHTML}
        <div class="assistant-summary">${payload.summary || ""}</div>
        <div class="assistant-source">${payload.source || ""}</div>
    `;

    body.appendChild(card);
    body.scrollTop = body.scrollHeight;

    if (data.type === "questions") {
    const card = document.createElement("div");
    card.className = "assistant-card";

    let listHTML = "<ul class='assistant-questions'>";

    data.data.forEach(q => {
        listHTML += `<li onclick="autoFillQuestion('${q}')">${q}</li>`;
    });

    listHTML += "</ul>";

    card.innerHTML = `
        <div class="assistant-card-title">${data.title}</div>
        <div class="assistant-divider"></div>
        ${listHTML}
        <div class="assistant-source">${data.source}</div>
    `;

    body.appendChild(card);
    body.scrollTop = body.scrollHeight;
    return;
}
}

function autoFillQuestion(text) {
    document.getElementById("assistantInput").value = text;
}