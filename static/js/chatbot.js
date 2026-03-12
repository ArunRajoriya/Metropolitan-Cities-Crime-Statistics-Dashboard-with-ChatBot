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
    userDiv.textContent = message;
    body.appendChild(userDiv);

    input.value = "";

    // Typing indicator with animation
    const typing = document.createElement("div");
    typing.className = "assistant-typing";
    typing.innerHTML = '🔍 Analyzing NCRB dataset<span class="dots"></span>';
    body.appendChild(typing);
    
    // Animate dots
    let dotCount = 0;
    const dotInterval = setInterval(() => {
        dotCount = (dotCount + 1) % 4;
        const dots = '.'.repeat(dotCount);
        typing.innerHTML = `🔍 Analyzing NCRB dataset${dots}`;
    }, 500);
    
    body.scrollTop = body.scrollHeight;

    try{
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await res.json();

        clearInterval(dotInterval);
        body.removeChild(typing);

        appendAssistantResponse(data);

    } catch(err){
        clearInterval(dotInterval);
        body.removeChild(typing);

        const errorDiv = document.createElement("div");
        errorDiv.className = "assistant-error";
        errorDiv.innerHTML = '⚠️ Unable to process request. Please try again.';
        body.appendChild(errorDiv);
    }

    body.scrollTop = body.scrollHeight;
}


function appendAssistantResponse(payload){
    const body = document.getElementById("assistantBody");

    // Handle errors with suggestions
    if(payload.type === "error" || payload.type === "clarification"){
        const card = document.createElement("div");
        card.className = "assistant-card";
        
        let html = `
            <div class="assistant-card-title">❌ ${payload.summary || payload.message || "Error"}</div>
        `;
        
        if(payload.suggestions && payload.suggestions.length > 0){
            html += `<div class="assistant-divider"></div>`;
            html += `<div style="margin-top: 0.75rem;"><strong>💡 Suggestions:</strong></div>`;
            html += `<ul class="assistant-questions">`;
            payload.suggestions.forEach(suggestion => {
                html += `<li onclick="autoFillQuestion('${suggestion.replace(/'/g, "\\'")}')">${suggestion}</li>`;
            });
            html += `</ul>`;
        }
        
        card.innerHTML = html;
        body.appendChild(card);
        body.scrollTop = body.scrollHeight;
        return;
    }

    // Handle crime suggestions
    if(payload.type === "crime_suggestions"){
        const card = document.createElement("div");
        card.className = "assistant-card";
        
        let html = `
            <div class="assistant-card-title">🔍 ${payload.title}</div>
            <div class="assistant-card-sub">${payload.summary}</div>
            <div class="assistant-divider"></div>
            <div style="margin-top: 0.75rem;"><strong>📋 Available Crimes:</strong></div>
            <ul class="assistant-questions">
        `;
        
        payload.data.forEach(crime => {
            const query = `${crime} ${payload.year}`;
            html += `<li onclick="autoFillQuestion('${query.replace(/'/g, "\\'")}')">${crime}</li>`;
        });
        
        html += `</ul>`;
        html += `<div class="assistant-source">📚 ${payload.source || ""}</div>`;
        
        card.innerHTML = html;
        body.appendChild(card);
        body.scrollTop = body.scrollHeight;
        return;
    }

    // Handle greeting responses
    if(payload.type === "greeting"){
        const card = document.createElement("div");
        card.className = "assistant-card";
        
        let html = `
            <div class="assistant-card-title">👋 Welcome to NCRB Analytics</div>
            <div class="assistant-card-sub">${payload.summary}</div>
            <div class="assistant-divider"></div>
            <div style="margin-top: 0.75rem;"><strong>🎯 I can help you with:</strong></div>
            <ul class="assistant-capabilities">
        `;
        
        payload.capabilities.forEach(capability => {
            html += `<li>${capability}</li>`;
        });
        
        html += `</ul>`;
        html += `<div class="assistant-example" style="margin-top: 1rem; padding: 0.75rem; background: #f0f9ff; border-radius: 0.375rem; font-size: 0.85rem; color: #1e40af;"><strong>💡 Example:</strong> ${payload.example}</div>`;
        
        card.innerHTML = html;
        body.appendChild(card);
        body.scrollTop = body.scrollHeight;
        return;
    }

    const card = document.createElement("div");
    card.className = "assistant-card";

    // Build context text
    let contextText = "";
    if(payload.context){
        if(payload.context.city && payload.context.year){
            contextText = `📍 ${payload.context.city} | 📅 ${payload.context.year}`;
        } else if(payload.context.city){
            contextText = `📍 ${payload.context.city}`;
        } else if(payload.context.year){
            contextText = `📅 ${payload.context.year}`;
        }
    }

    // Helper: convert object -> HTML
    function renderValue(key, val){
        if(val === null || val === undefined) return `<div class="assistant-metric"><span>${key}</span><strong>—</strong></div>`;

        if(typeof val === "number"){
            // Don't format percentages, ratios, or small decimal numbers
            const keyLower = key.toLowerCase();
            const isPercentage = keyLower.includes('percentage') || keyLower.includes('percent');
            const isRatio = keyLower.includes('ratio');
            const isSmallDecimal = val < 100 && val % 1 !== 0;
            
            let formatted;
            if (isPercentage || isRatio || isSmallDecimal) {
                // Keep as-is for percentages, ratios, and decimals
                formatted = val;
            } else {
                // Apply Indian formatting for large whole numbers (arrests, cases, etc.)
                formatted = formatIndianNumber(val);
            }
            return `<div class="assistant-metric"><span>${key}</span><strong>${formatted}</strong></div>`;
        }
        
        if(typeof val === "string"){
            return `<div class="assistant-metric"><span>${key}</span><strong>${val}</strong></div>`;
        }

        if(typeof val === "object"){
            const rows = Object.entries(val).map(([k,v]) => {
                let formattedVal = v;
                if (typeof v === 'number') {
                    const kLower = k.toLowerCase();
                    const isPercentage = kLower.includes('percentage') || kLower.includes('percent');
                    const isRatio = kLower.includes('ratio');
                    const isSmallDecimal = v < 100 && v % 1 !== 0;
                    
                    if (!isPercentage && !isRatio && !isSmallDecimal) {
                        formattedVal = formatIndianNumber(v);
                    }
                }
                return `<div class="assistant-metric nested"><span>${k}</span><strong>${formattedVal}</strong></div>`;
            }).join("");
            return `<div class="assistant-metric-group"><div class="assistant-metric-group-title">${key}</div>${rows}</div>`;
        }

        return `<div class="assistant-metric"><span>${key}</span><strong>${JSON.stringify(val)}</strong></div>`;
    }

    // Special case: matrix_comparison -> table
    if(payload.type === "matrix_comparison" && payload.data && typeof payload.data === "object"){
        const cities = Object.keys(payload.data);
        const yearSet = new Set();
        cities.forEach(city => {
            const row = payload.data[city];
            Object.keys(row || {}).forEach(y => yearSet.add(y));
        });
        const years = Array.from(yearSet).sort();

        let tableHTML = `<div class="assistant-table-wrap"><table class="assistant-table"><thead><tr><th>City</th>${years.map(y=>`<th>${y}</th>`).join("")}</tr></thead><tbody>`;
        for(const city of cities){
            tableHTML += `<tr><td class="city-cell">${city}</td>`;
            for(const y of years){
                const v = (payload.data[city] && payload.data[city][y]) ?? "—";
                const formatted = typeof v === 'number' ? formatIndianNumber(v) : v;
                tableHTML += `<td>${formatted}</td>`;
            }
            tableHTML += `</tr>`;
        }
        tableHTML += `</tbody></table></div>`;

        card.innerHTML = `
            <div class="assistant-card-title">📊 ${payload.title}</div>
            ${contextText ? `<div class="assistant-card-sub">${contextText}</div>` : ''}
            <div class="assistant-divider"></div>
            ${tableHTML}
            ${payload.insight || payload.summary ? `<div class="assistant-summary" style="margin-top: 0.3rem; padding: 0.4rem; background: #f0f9ff; border-radius: 0.375rem; font-size: 0.75rem; line-height: 1.4;">${payload.insight || payload.summary}</div>` : ''}
            <div class="assistant-source">📚 ${payload.source || ""}</div>
        `;
        body.appendChild(card);
        body.scrollTop = body.scrollHeight;
        return;
    }

    // Generic rendering
    let dataHTML = "";
    if(payload.data && typeof payload.data === "object"){
        for(const key of Object.keys(payload.data)){
            const val = payload.data[key];
            dataHTML += renderValue(key, val);
        }
    } else if(Array.isArray(payload.data)){
        dataHTML = payload.data.map(d => `<div class="assistant-metric"><span>${d}</span></div>`).join("");
    }

    // Add icon based on type
    let icon = "📊";
    if(payload.type === "trend_analysis") icon = "📈";
    if(payload.type === "gender_ratio" || payload.type === "gender_analysis") icon = "👥";
    if(payload.type === "government") icon = "🏛️";
    if(payload.type.includes("top")) icon = "🏆";

    card.innerHTML = `
        <div class="assistant-card-title">${icon} ${payload.title}</div>
        ${contextText ? `<div class="assistant-card-sub">${contextText}</div>` : ''}
        <div class="assistant-divider"></div>
        ${dataHTML}
        ${payload.insight || payload.summary ? `<div class="assistant-summary" style="margin-top: 0.3rem; padding: 0.4rem; background: #f0f9ff; border-radius: 0.375rem; font-size: 0.75rem; line-height: 1.4;">${payload.insight || payload.summary}</div>` : ''}
        <div class="assistant-source">📚 ${payload.source || ""}</div>
    `;

    body.appendChild(card);
    body.scrollTop = body.scrollHeight;
}

function autoFillQuestion(text) {
    document.getElementById("assistantInput").value = text;
    // Automatically send the query for better UX
    sendAssistantQuery();
}
// =======================================
// ENTER KEY TO SEND MESSAGE
// =======================================
document.getElementById("assistantInput").addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();   // Prevent newline
        sendAssistantQuery();     // Send message
    }
});