import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def llm_extract(message):

    system_prompt = """
You are an advanced intent extraction engine for a crime analytics dashboard.

Your task is to extract structured information from user queries about crime statistics.

EXTRACTION RULES:
1. Cities: Extract all Indian city names mentioned (e.g., Delhi, Mumbai, Bangalore)
2. Years: Extract years between 2016-2020 (available: 2016, 2019, 2020)
3. Gender: Detect "male", "female", "men", "women", "boys", "girls"
4. Crime Types: Extract specific crime names (murder, theft, rape, assault, etc.)
5. Intent Classification:
   - "city_profile" → Single city query
   - "city_comparison" → Multiple cities or "compare", "vs", "between"
   - "highest" → "highest", "maximum", "most", "top"
   - "lowest" → "lowest", "minimum", "least", "bottom"
   - "top_n" → "top 3", "top 5", "top 10"
   - "trend" → "trend", "over time", "change", "growth"
   - "gov_crime_full_data" → "government", "national", "india total"
   - "foreign_data" → "foreign", "foreigner", "international"
   - "juvenile" → "juvenile", "minor", "child", "under 18"
   - "statistics" → General stats without specific city

ADVANCED FEATURES:
- Detect aggregation requests: "total", "sum", "average", "percentage"
- Detect ranking: "rank", "position", "standing"
- Detect time comparisons: "year over year", "compared to last year"
- Handle misspellings: Try to match closest city/crime name

Return ONLY valid JSON (no markdown, no explanation):
{
  "intent": "",
  "cities": [],
  "years": [],
  "gender": "",
  "crime": "",
  "aggregation": "",
  "top_n": 0,
  "confidence": 0.0
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
        
        parsed = json.loads(content)
        
        # Add confidence score if not present
        if "confidence" not in parsed:
            parsed["confidence"] = 0.8
            
        return parsed

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