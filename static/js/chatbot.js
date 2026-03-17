/* ---------------- ENHANCED CHATBOT FUNCTIONALITY ---------------- */

/* Indian Number Formatting */
function formatIndianNumber(num) {
    // Handle invalid inputs
    if (num === null || num === undefined || isNaN(num)) return '0';
    
    // Round to integer
    num = Math.round(num);
    
    if (num === 0) return '0';
    
    const numStr = Math.abs(num).toString();
    const isNegative = num < 0;
    
    if (numStr.length <= 3) {
        return isNegative ? '-' + numStr : numStr;
    }
    
    let result = '';
    let remaining = numStr;
    
    // Last 3 digits
    if (remaining.length > 3) {
        result = ',' + remaining.slice(-3);
        remaining = remaining.slice(0, -3);
    } else {
        result = remaining;
        remaining = '';
    }
    
    // Remaining digits in groups of 2
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

/* Enhanced Toggle Function */
function toggleAssistant(event) {
    if (event) event.preventDefault();

    const panel = document.getElementById("assistant-panel");
    const overlay = document.getElementById("assistant-overlay");

    panel.classList.toggle("active");
    overlay.classList.toggle("active");
    
    // Focus on input when opening
    if (panel.classList.contains("active")) {
        setTimeout(() => {
            document.getElementById("assistantInput").focus();
        }, 300);
    }
}

/* Enhanced Query Sending with Preprocessing */
async function sendAssistantQuery() {
    const input = document.getElementById("assistantInput");
    const message = input.value.trim();
    if (!message) return;

    const body = document.getElementById("assistantBody");

    // Show user message with enhanced styling
    const userDiv = document.createElement("div");
    userDiv.className = "assistant-user";
    userDiv.textContent = message;
    body.appendChild(userDiv);

    input.value = "";

    // Enhanced typing indicator with query preprocessing hint
    const typing = document.createElement("div");
    typing.className = "assistant-typing";
    typing.innerHTML = '🔍 Processing your query<span class="dots"></span>';
    body.appendChild(typing);
    
    // Animate dots
    let dotCount = 0;
    const dotInterval = setInterval(() => {
        dotCount = (dotCount + 1) % 4;
        const dots = '.'.repeat(dotCount);
        typing.innerHTML = `🔍 Processing your query${dots}`;
    }, 500);
    
    body.scrollTop = body.scrollHeight;

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await res.json();

        clearInterval(dotInterval);
        body.removeChild(typing);

        appendEnhancedResponse(data);

        // Show follow-up suggestions if available
        if (data.followup_suggestions && data.followup_suggestions.length > 0) {
            showFollowupSuggestions(data.followup_suggestions);
        }

        // Show autocomplete suggestions for next query
        updateAutocompleteSuggestions(data);

    } catch (err) {
        clearInterval(dotInterval);
        body.removeChild(typing);

        const errorDiv = document.createElement("div");
        errorDiv.className = "assistant-error";
        errorDiv.innerHTML = '⚠️ Unable to process request. Please try again or rephrase your query.';
        body.appendChild(errorDiv);
    }

    body.scrollTop = body.scrollHeight;
}

/* Enhanced Response Rendering */
function appendEnhancedResponse(payload) {
    const body = document.getElementById("assistantBody");

    // Handle errors with enhanced styling
    if (payload.type === "error" || payload.type === "clarification") {
        const card = document.createElement("div");
        card.className = "assistant-card";
        
        let html = `
            <div class="assistant-card-title">❌ ${payload.summary || payload.message || "Error"}</div>
        `;
        
        if (payload.suggestions && payload.suggestions.length > 0) {
            html += `<div class="assistant-divider"></div>`;
            html += `<div style="margin-top: 12px; font-weight: 600; color: #374151;">💡 Try these instead:</div>`;
            html += `<ul class="assistant-questions">`;
            payload.suggestions.forEach(suggestion => {
                html += `<li onclick="autoFillAndSend('${suggestion.replace(/'/g, "\\'")}')">${suggestion}</li>`;
            });
            html += `</ul>`;
        }
        
        card.innerHTML = html;
        body.appendChild(card);
        body.scrollTop = body.scrollHeight;
        return;
    }

    // Handle crime suggestions with clickable options
    if (payload.type === "crime_suggestions") {
        const card = document.createElement("div");
        card.className = "assistant-card";
        
        let html = `
            <div class="assistant-card-title">📊 ${payload.title}</div>
            <div class="assistant-card-sub">${payload.summary}</div>
            <div class="assistant-divider"></div>
            <div class="crime-suggestions-grid">
        `;
        
        // Create clickable crime options
        payload.data.forEach((crime, index) => {
            const crimeQuery = `${crime} ${payload.year}`;
            html += `
                <div class="crime-suggestion-item" onclick="autoFillAndSend('${crimeQuery.replace(/'/g, "\\'")}')">
                    <span class="crime-index">${String.fromCharCode(65 + (index % 26))}.</span>
                    <span class="crime-name">${crime}</span>
                </div>
            `;
        });
        
        html += `</div>`;
        html += buildSourceSection(payload);
        
        card.innerHTML = html;
        body.appendChild(card);
        body.scrollTop = body.scrollHeight;
        return;
    }

    // Handle greeting responses with enhanced styling
    if (payload.type === "greeting") {
        const card = document.createElement("div");
        card.className = "assistant-card";
        
        let html = `
            <div class="assistant-card-title">👋 Welcome to Crime Analytics AI</div>
            <div class="assistant-card-sub">${payload.summary}</div>
            <div class="assistant-divider"></div>
            <div style="margin-top: 12px; font-weight: 600; color: #374151;">🎯 I can help you with:</div>
            <ul class="assistant-capabilities">
        `;
        
        payload.capabilities.forEach(capability => {
            html += `<li>${capability}</li>`;
        });
        
        html += `</ul>`;
        html += `<div class="assistant-example"><strong>💡 Example:</strong> ${payload.example}</div>`;
        
        card.innerHTML = html;
        body.appendChild(card);
        body.scrollTop = body.scrollHeight;
        return;
    }

    // Enhanced main response rendering
    const card = document.createElement("div");
    card.className = "assistant-card";

    // Get appropriate icon based on response type
    let icon = getResponseIcon(payload.type);
    
    // Build context information
    let contextText = buildContextText(payload);

    // Handle comprehensive trend analysis with special formatting
    if (payload.type === "comprehensive_trend_analysis" && payload.data) {
        let html = `
            <div class="assistant-card-title">${icon} ${payload.title}</div>
            ${contextText ? `<div class="assistant-card-sub">${contextText}</div>` : ''}
            <div class="assistant-divider"></div>
        `;
        
        // National trend section
        if (payload.data.national_trend) {
            html += `<div class="assistant-metric-group">
                <div class="assistant-metric-group-title">📈 National Trend</div>`;
            for (const [year, value] of Object.entries(payload.data.national_trend)) {
                html += `<div class="assistant-metric nested"><span>${year}</span><strong>${formatIndianNumber(value)}</strong></div>`;
            }
            html += `</div>`;
        }
        
        // Top cities trend section
        if (payload.data.top_cities_trend) {
            html += `<div class="assistant-metric-group">
                <div class="assistant-metric-group-title">🏆 Top Cities Trend</div>`;
            
            const cities = Object.keys(payload.data.top_cities_trend);
            const years = new Set();
            cities.forEach(city => {
                Object.keys(payload.data.top_cities_trend[city] || {}).forEach(year => years.add(year));
            });
            const sortedYears = Array.from(years).sort();
            
            // Create mini table for top cities
            html += `<div class="assistant-table-wrap"><table class="assistant-table compact">
                <thead><tr><th>City</th>${sortedYears.map(y => `<th>${y}</th>`).join("")}</tr></thead>
                <tbody>`;
            
            cities.slice(0, 3).forEach(city => {
                html += `<tr><td class="city-cell">${city}</td>`;
                sortedYears.forEach(year => {
                    const value = payload.data.top_cities_trend[city][year];
                    const formatted = value ? formatIndianNumber(value) : "—";
                    html += `<td>${formatted}</td>`;
                });
                html += `</tr>`;
            });
            html += `</tbody></table></div></div>`;
        }
        
        // Regional insights section
        if (payload.data.regional_insights) {
            const insights = payload.data.regional_insights;
            html += `<div class="assistant-metric-group">
                <div class="assistant-metric-group-title">🎯 Key Insights</div>`;
            
            if (insights.growth_leaders && insights.growth_leaders.length > 0) {
                html += `<div class="assistant-metric nested"><span>📈 Growth Leaders</span><strong>`;
                html += insights.growth_leaders.map(item => `${item.city} (${item.change})`).join(', ');
                html += `</strong></div>`;
            }
            
            if (insights.decline_leaders && insights.decline_leaders.length > 0) {
                html += `<div class="assistant-metric nested"><span>📉 Decline Leaders</span><strong>`;
                html += insights.decline_leaders.map(item => `${item.city} (${item.change})`).join(', ');
                html += `</strong></div>`;
            }
            
            if (insights.stable_cities && insights.stable_cities.length > 0) {
                html += `<div class="assistant-metric nested"><span>⚖️ Stable Cities</span><strong>`;
                html += insights.stable_cities.map(item => `${item.city} (${item.change})`).join(', ');
                html += `</strong></div>`;
            }
            
            html += `</div>`;
        }
        
        html += buildInsightSection(payload);
        html += buildSourceSection(payload);
        
        card.innerHTML = html;
        body.appendChild(card);
        body.scrollTop = body.scrollHeight;
        return;
    }

    // Handle matrix comparison with enhanced table
    if (payload.type === "matrix_comparison" && payload.data && typeof payload.data === "object") {
        const tableHTML = buildEnhancedTable(payload.data);
        
        card.innerHTML = `
            <div class="assistant-card-title">${icon} ${payload.title}</div>
            ${contextText ? `<div class="assistant-card-sub">${contextText}</div>` : ''}
            <div class="assistant-divider"></div>
            ${tableHTML}
            ${buildInsightSection(payload)}
            ${buildSourceSection(payload)}
        `;
        body.appendChild(card);
        body.scrollTop = body.scrollHeight;
        return;
    }

    // Enhanced generic rendering
    let dataHTML = buildDataSection(payload.data);
    
    // Add note section if present
    let noteHTML = "";
    if (payload.note) {
        noteHTML = `<div class="assistant-note" style="margin-top: 12px; padding: 12px; background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; font-size: 13px; color: #92400e;"><strong>📝 Note:</strong> ${payload.note}</div>`;
    }

    card.innerHTML = `
        <div class="assistant-card-title">${icon} ${payload.title}</div>
        ${contextText ? `<div class="assistant-card-sub">${contextText}</div>` : ''}
        <div class="assistant-divider"></div>
        ${dataHTML}
        ${noteHTML}
        ${buildInsightSection(payload)}
        ${buildSourceSection(payload)}
        ${buildActionButtons(payload)}
    `;

    body.appendChild(card);
    body.scrollTop = body.scrollHeight;
}

/* Helper Functions for Enhanced Rendering */
function getResponseIcon(type) {
    const icons = {
        "city": "🏙️",
        "multi_city": "📊",
        "multi_year_trend": "📈",
        "top_cities_trend": "🏆",
        "comprehensive_trend_analysis": "📊",
        "trend_analysis": "📈",
        "crime_suggestions": "📋",
        "foreign_summary": "🌍",
        "foreign_comparison": "👥",
        "foreign_trend": "📈",
        "gender_analysis": "👥",
        "government": "🏛️",
        "juvenile": "👶",
        "top_": "🏆",
        "ranking": "🏆",
        "statistics": "📊",
        "analysis": "🔍",
        "correlation_analysis": "🔗",
        "pattern_analysis": "🔍",
        "prediction_analysis": "🔮",
        "advanced_ranking": "🏆",
        "aggregation_analysis": "📊"
    };
    
    for (const [key, icon] of Object.entries(icons)) {
        if (type.includes(key)) return icon;
    }
    return "📊";
}

function buildContextText(payload) {
    if (!payload.context) return "";
    
    let parts = [];
    if (payload.context.city) parts.push(`📍 ${payload.context.city}`);
    if (payload.context.year) parts.push(`📅 ${payload.context.year}`);
    if (payload.context.gender) parts.push(`👥 ${payload.context.gender}`);
    
    return parts.join(" | ");
}

function buildEnhancedTable(data) {
    const cities = Object.keys(data);
    const yearSet = new Set();
    cities.forEach(city => {
        const row = data[city];
        Object.keys(row || {}).forEach(y => yearSet.add(y));
    });
    const years = Array.from(yearSet).sort();

    let tableHTML = `<div class="assistant-table-wrap"><table class="assistant-table">
        <thead><tr><th>City</th>${years.map(y => `<th>${y}</th>`).join("")}</tr></thead>
        <tbody>`;
    
    for (const city of cities) {
        tableHTML += `<tr><td class="city-cell">${city}</td>`;
        for (const y of years) {
            const v = (data[city] && data[city][y]) ?? "—";
            const formatted = typeof v === 'number' ? formatIndianNumber(v) : v;
            tableHTML += `<td>${formatted}</td>`;
        }
        tableHTML += `</tr>`;
    }
    tableHTML += `</tbody></table></div>`;
    
    return tableHTML;
}

function buildDataSection(data) {
    if (!data || typeof data !== "object") return "";
    
    let html = "";
    for (const [key, val] of Object.entries(data)) {
        html += renderEnhancedValue(key, val);
    }
    return html;
}

function renderEnhancedValue(key, val) {
    if (val === null || val === undefined) {
        return `<div class="assistant-metric"><span>${key}</span><strong>—</strong></div>`;
    }

    if (typeof val === "number") {
        const keyLower = key.toLowerCase();
        const isPercentage = keyLower.includes('percentage') || keyLower.includes('percent');
        const isRatio = keyLower.includes('ratio');
        const isSmallDecimal = val < 100 && val % 1 !== 0;
        
        let formatted;
        if (isPercentage || isRatio || isSmallDecimal) {
            formatted = val.toFixed(2);
        } else {
            formatted = formatIndianNumber(Math.round(val));
        }
        return `<div class="assistant-metric"><span>${key}</span><strong>${formatted}</strong></div>`;
    }
    
    if (typeof val === "string") {
        return `<div class="assistant-metric"><span>${key}</span><strong>${val}</strong></div>`;
    }

    if (typeof val === "object" && !Array.isArray(val)) {
        const rows = Object.entries(val).map(([k, v]) => {
            let formattedVal = v;
            if (typeof v === 'number') {
                const kLower = k.toLowerCase();
                const isPercentage = kLower.includes('percentage') || kLower.includes('percent');
                const isRatio = kLower.includes('ratio');
                const isCount = kLower.includes('count');
                const isSmallDecimal = v < 100 && v % 1 !== 0;
                
                if (isPercentage || isRatio) {
                    formattedVal = v.toFixed(2) + (isPercentage ? '%' : '');
                } else if (isSmallDecimal && !isCount) {
                    formattedVal = v.toFixed(2);
                } else {
                    formattedVal = formatIndianNumber(Math.round(v));
                }
            } else if (typeof v === 'string') {
                formattedVal = v;
            } else {
                formattedVal = JSON.stringify(v);
            }
            return `<div class="assistant-metric nested"><span>${k}</span><strong>${formattedVal}</strong></div>`;
        }).join("");
        return `<div class="assistant-metric-group"><div class="assistant-metric-group-title">${key}</div>${rows}</div>`;
    }

    if (Array.isArray(val)) {
        return `<div class="assistant-metric"><span>${key}</span><strong>${val.join(', ')}</strong></div>`;
    }

    return `<div class="assistant-metric"><span>${key}</span><strong>${JSON.stringify(val)}</strong></div>`;
}

function buildInsightSection(payload) {
    if (!payload.insight && !payload.summary) return "";
    
    const content = payload.insight || payload.summary;
    return `<div class="assistant-summary" style="margin-top: 16px; padding: 16px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 12px; font-size: 14px; line-height: 1.5; color: #1e40af; border: 1px solid #bfdbfe;">${content}</div>`;
}

function buildSourceSection(payload) {
    if (!payload.source) return "";
    return `<div class="assistant-source">📚 ${payload.source}</div>`;
}

function buildActionButtons(payload) {
    // Add contextual action buttons based on response type
    let buttons = [];
    
    if (payload.type.includes("city") || payload.type.includes("comparison")) {
        buttons.push(`<button onclick="suggestRelatedQuery('trend analysis')" class="action-btn">📈 View Trends</button>`);
        buttons.push(`<button onclick="suggestRelatedQuery('gender analysis')" class="action-btn">👥 Gender Analysis</button>`);
    }
    
    if (payload.type.includes("trend")) {
        buttons.push(`<button onclick="suggestRelatedQuery('detailed breakdown')" class="action-btn">🔍 Detailed View</button>`);
    }
    
    if (buttons.length === 0) return "";
    
    return `<div style="margin-top: 16px; display: flex; gap: 8px; flex-wrap: wrap;">${buttons.join('')}</div>`;
}

/* Enhanced Auto-fill and Send */
function autoFillAndSend(text) {
    const input = document.getElementById("assistantInput");
    input.value = text;
    sendAssistantQuery();
}

function autoFillQuestion(text) {
    document.getElementById("assistantInput").value = text;
}

function suggestRelatedQuery(type) {
    // Generate contextual follow-up queries
    const suggestions = {
        'trend analysis': 'Show me the trend analysis',
        'gender analysis': 'Show me gender breakdown',
        'detailed breakdown': 'Give me detailed statistics'
    };
    
    autoFillAndSend(suggestions[type] || type);
}

/* Enhanced Enter Key Handler */
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById("assistantInput");
    if (input) {
        input.addEventListener("keydown", function(event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendAssistantQuery();
            }
        });
        
        // Add input suggestions
        input.addEventListener("focus", function() {
            showInputSuggestions();
        });
    }
});

/* Input Suggestions */
function showInputSuggestions() {
    // Could add a dropdown with common queries
    const suggestions = [
        "Compare Delhi and Mumbai arrests in 2020",
        "Top 5 cities by crime rate",
        "Gender analysis for Chennai 2019",
        "Foreign crime statistics 2020",
        "Juvenile crime trends"
    ];
    
    // Implementation for suggestion dropdown could go here
}

/* Follow-up Suggestions */
function showFollowupSuggestions(suggestions) {
    const body = document.getElementById("assistantBody");
    
    const followupDiv = document.createElement("div");
    followupDiv.className = "assistant-followup";
    followupDiv.innerHTML = `
        <div class="followup-title">💡 You might also want to ask:</div>
        <div class="followup-buttons">
            ${suggestions.map(suggestion => 
                `<button class="followup-btn" onclick="autoFillAndSend('${suggestion.replace(/'/g, "\\'")}')">${suggestion}</button>`
            ).join('')}
        </div>
    `;
    
    body.appendChild(followupDiv);
    body.scrollTop = body.scrollHeight;
}

/* Autocomplete Suggestions */
function updateAutocompleteSuggestions(responseData) {
    // Store suggestions for autocomplete
    if (responseData.suggestions) {
        window.chatbotSuggestions = responseData.suggestions;
    }
}

/* Enhanced Input with Autocomplete */
function setupEnhancedInput() {
    const input = document.getElementById("assistantInput");
    if (!input) return;
    
    // Create suggestions dropdown
    const suggestionsDiv = document.createElement("div");
    suggestionsDiv.id = "chatbot-suggestions";
    suggestionsDiv.className = "chatbot-suggestions";
    input.parentNode.insertBefore(suggestionsDiv, input.nextSibling);
    
    let suggestionTimeout;
    
    input.addEventListener("input", function() {
        clearTimeout(suggestionTimeout);
        const value = this.value.trim();
        
        if (value.length < 2) {
            hideSuggestions();
            return;
        }
        
        suggestionTimeout = setTimeout(() => {
            showAutocompleteSuggestions(value);
        }, 300);
    });
    
    input.addEventListener("blur", function() {
        // Hide suggestions after a delay to allow clicking
        setTimeout(hideSuggestions, 200);
    });
}

function showAutocompleteSuggestions(partial) {
    const suggestionsDiv = document.getElementById("chatbot-suggestions");
    if (!suggestionsDiv) return;
    
    // Get suggestions from various sources
    const suggestions = [];
    
    // Add common query patterns
    const commonQueries = [
        "Compare Delhi and Mumbai arrests in 2020",
        "Top 5 cities by crime rate",
        "Show me trend analysis",
        "Gender breakdown for Chennai",
        "Juvenile crime statistics",
        "Foreign crime data 2020"
    ];
    
    // Filter suggestions based on partial input
    const filtered = commonQueries.filter(query => 
        query.toLowerCase().includes(partial.toLowerCase())
    );
    
    suggestions.push(...filtered.slice(0, 5));
    
    // Add stored suggestions from previous responses
    if (window.chatbotSuggestions) {
        const contextSuggestions = window.chatbotSuggestions.filter(query =>
            query.toLowerCase().includes(partial.toLowerCase())
        );
        suggestions.push(...contextSuggestions.slice(0, 3));
    }
    
    if (suggestions.length === 0) {
        hideSuggestions();
        return;
    }
    
    // Remove duplicates
    const uniqueSuggestions = [...new Set(suggestions)];
    
    suggestionsDiv.innerHTML = uniqueSuggestions.slice(0, 6).map(suggestion =>
        `<div class="suggestion-item" onclick="selectSuggestion('${suggestion.replace(/'/g, "\\'")}')">${suggestion}</div>`
    ).join('');
    
    suggestionsDiv.style.display = 'block';
}

function hideSuggestions() {
    const suggestionsDiv = document.getElementById("chatbot-suggestions");
    if (suggestionsDiv) {
        suggestionsDiv.style.display = 'none';
    }
}

function selectSuggestion(suggestion) {
    const input = document.getElementById("assistantInput");
    if (input) {
        input.value = suggestion;
        input.focus();
    }
    hideSuggestions();
}

/* Enhanced Error Handling */
function handleEnhancedError(errorData) {
    const body = document.getElementById("assistantBody");
    
    const errorCard = document.createElement("div");
    errorCard.className = "assistant-card error-card";
    
    let html = `
        <div class="assistant-card-title">❌ ${errorData.message || errorData.summary}</div>
    `;
    
    // Show corrections if available
    if (errorData.corrections && errorData.corrections.length > 0) {
        html += `<div class="assistant-divider"></div>`;
        html += `<div class="error-corrections">`;
        html += `<div class="correction-title">🔧 Did you mean:</div>`;
        
        errorData.corrections.forEach(correction => {
            html += `<div class="correction-group">`;
            html += `<span class="correction-input">"${correction.input}"</span> → `;
            correction.suggestions.forEach((suggestion, index) => {
                html += `<button class="correction-btn" onclick="autoFillAndSend('${suggestion.replace(/'/g, "\\'")}')">${suggestion}</button>`;
                if (index < correction.suggestions.length - 1) html += ' or ';
            });
            html += `</div>`;
        });
        
        html += `</div>`;
    }
    
    // Show suggestions
    if (errorData.suggested_queries && errorData.suggested_queries.length > 0) {
        html += `<div class="assistant-divider"></div>`;
        html += `<div style="margin-top: 12px; font-weight: 600; color: #374151;">💡 Try these instead:</div>`;
        html += `<ul class="assistant-questions">`;
        errorData.suggested_queries.forEach(suggestion => {
            html += `<li onclick="autoFillAndSend('${suggestion.replace(/'/g, "\\'")}')">${suggestion}</li>`;
        });
        html += `</ul>`;
    }
    
    errorCard.innerHTML = html;
    body.appendChild(errorCard);
    body.scrollTop = body.scrollHeight;
}

/* Initialize Enhanced Features */
document.addEventListener('DOMContentLoaded', function() {
    setupEnhancedInput();
    
    // Add CSS for new features
    const style = document.createElement('style');
    style.textContent = `
        .chatbot-suggestions {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        }
        
        .suggestion-item {
            padding: 8px 12px;
            cursor: pointer;
            border-bottom: 1px solid #f3f4f6;
            font-size: 14px;
        }
        
        .suggestion-item:hover {
            background-color: #f9fafb;
        }
        
        .suggestion-item:last-child {
            border-bottom: none;
        }
        
        .assistant-followup {
            margin: 16px 0;
            padding: 16px;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 12px;
            border: 1px solid #bfdbfe;
        }
        
        .followup-title {
            font-weight: 600;
            color: #1e40af;
            margin-bottom: 12px;
            font-size: 14px;
        }
        
        .followup-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .followup-btn {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .followup-btn:hover {
            background: #2563eb;
        }
        
        .error-card {
            border-left: 4px solid #ef4444;
        }
        
        .error-corrections {
            margin-top: 12px;
        }
        
        .correction-title {
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
        }
        
        .correction-group {
            margin: 8px 0;
            padding: 8px;
            background: #f9fafb;
            border-radius: 6px;
        }
        
        .correction-input {
            font-weight: 600;
            color: #ef4444;
        }
        
        .correction-btn {
            background: #10b981;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            margin: 0 4px;
        }
        
        .correction-btn:hover {
            background: #059669;
        }
    `;
    document.head.appendChild(style);
});