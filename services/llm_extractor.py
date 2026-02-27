import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def llm_extract(message):

    system_prompt = """
You are a strict intent extraction engine for a crime analytics dashboard.

Rules:
- Extract city names.
- Extract year if mentioned.
- Extract gender if mentioned.
- If one city is mentioned → intent = city_profile.
- If two cities → intent = city_comparison.
- If highest/maximum/top → intent = highest.
- If lowest/minimum/least → intent = lowest.
- If government/national mentioned → intent = gov_crime_full_data.
- If foreign mentioned → intent = foreign_data.

Return JSON only:
{
  "intent": "",
  "cities": [],
  "years": [],
  "gender": "",
  "crime": ""
}
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
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0
            },
            timeout=10
        )

        result = response.json()

        content = result["choices"][0]["message"]["content"]
        content = content.replace("```json", "").replace("```", "").strip()

        return json.loads(content)

    except Exception as e:
        print("LLM ERROR:", e)
        return {
            "intent": "unknown",
            "cities": [],
            "years": [],
            "gender": "",
            "crime": ""
        }