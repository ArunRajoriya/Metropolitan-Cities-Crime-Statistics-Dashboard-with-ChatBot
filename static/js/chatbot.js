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


function appendAssistantResponse(data){
    const body = document.getElementById("assistantBody");

    if(data.type === "error"){
        const div = document.createElement("div");
        div.className = "assistant-error";
        div.innerText = data.summary || data.message;
        body.appendChild(div);
        body.scrollTop = body.scrollHeight;
        return;
    }

    const card = document.createElement("div");
    card.className = "assistant-card";

    let contextText = "";

    if(data.context){
        if(data.context.city && data.context.year){
            contextText = `${data.context.city} | ${data.context.year}`;
        } 
        else if(data.context.year){
            contextText = `${data.context.year}`;
        }
    }

    let dataHTML = "";

    if(data.data){
        for(const key in data.data){
            dataHTML += `
                <div class="assistant-metric">
                    <span>${key}</span>
                    <strong>${data.data[key]}</strong>
                </div>
            `;
        }
    }

    card.innerHTML = `
        <div class="assistant-card-title">${data.title}</div>
        <div class="assistant-card-sub">${contextText}</div>
        <div class="assistant-divider"></div>
        ${dataHTML}
        <div class="assistant-summary">${data.summary || ""}</div>
        <div class="assistant-source">${data.source || ""}</div>
    `;

    body.appendChild(card);
    body.scrollTop = body.scrollHeight;
}
