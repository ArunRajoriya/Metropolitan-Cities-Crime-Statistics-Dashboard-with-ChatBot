import os
import requests
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_insight(user_question, data):
    prompt = f"""
You are an expert crime analytics assistant providing insights from Indian crime data.

User Question: {user_question}

Data: {json.dumps(data)}

INSTRUCTIONS:
1. Provide a clear, concise insight in 2-3 sentences
2. Highlight key findings and patterns
3. Use specific numbers and comparisons
4. Be factual and professional
5. If comparing cities, mention the leader and notable differences
6. If showing trends, mention direction and magnitude of change
7. Add context about what the numbers mean

Return ONLY the insight text, no headings or formatting.
"""

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a crime analytics expert."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            },
            timeout=10
        )

        # 🔥 Check HTTP status
        if response.status_code != 200:
            print("GROQ ERROR:", response.status_code, response.text)
            return "Insight generation unavailable at the moment."

        result = response.json()

        # 🔥 Check structure safely
        if "choices" not in result:
            print("INVALID GROQ RESPONSE:", result)
            return "Insight generation unavailable."

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("INSIGHT EXCEPTION:", e)
        return "Insight generation temporarily unavailable."