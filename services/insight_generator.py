import os
import requests
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_insight(user_question, data):

    prompt = f"""
User Question:
{user_question}

Data:
{json.dumps(data, indent=2)}

Provide:
1. Clear explanation
2. Key insight
3. One smart follow-up suggestion
Keep it professional.
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