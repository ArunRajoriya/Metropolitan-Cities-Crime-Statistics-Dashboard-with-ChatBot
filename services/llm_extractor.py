import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def llm_extract(message):

    system_prompt = """
You are an advanced AI assistant for a comprehensive crime analytics dashboard with access to Indian crime data.

Your task is to extract structured information from user queries about crime statistics and analytics.

AVAILABLE DATASETS:
- Crime Data: City-wise arrest statistics (2016, 2019, 2020)
- Government Data: National crime investigation statistics (139+ crime types)
- Foreign Crime Data: Crimes against foreign tourists and other foreigners
- Juvenile Data: Minor-related crime statistics

EXTRACTION RULES:
1. Cities: Extract all Indian city names (Delhi, Mumbai, Bangalore, Chennai, Kolkata, etc.)
2. Years: Extract ALL years mentioned (2000-2030 range)
3. Gender: Detect "male", "female", "men", "women", "boys", "girls", "gender"
4. Crime Types: Extract specific crimes (murder, theft, rape, assault, robbery, etc.)
5. Intent Classification:
   - "city_profile" → Single city analysis
   - "city_comparison" → Multiple cities or "compare", "vs", "between"
   - "highest" → "highest", "maximum", "most", "top"
   - "lowest" → "lowest", "minimum", "least", "bottom"
   - "top_n" → "top 3", "top 5", "top 10"
   - "trend" → "trend", "over time", "change", "growth", "increase", "decrease"
   - "ranking" → "rank", "position", "standing", "order"
   - "statistics" → "stats", "statistics", "data", "information"
   - "analysis" → "analyze", "analysis", "breakdown", "detailed"
   - "percentage" → "percentage", "percent", "ratio", "proportion"
   - "average" → "average", "mean", "typical"
   - "total" → "total", "sum", "aggregate"
   - "gov_crime_full_data" → "government", "national", "india total"
   - "foreign_data" → "foreign", "foreigner", "international", "tourist"
   - "juvenile" → "juvenile", "minor", "child", "under 18"

ADVANCED PATTERN RECOGNITION:
- Detect complex comparisons: "Delhi vs Mumbai vs Kolkata"
- Handle time ranges: "from 2016 to 2020", "between 2019 and 2020"
- Recognize statistical queries: "correlation", "pattern", "insight"
- Identify data exploration: "show me", "what about", "tell me about"
- Handle natural language: "which city has the most crime?"
- Detect aggregation needs: "total across all cities"
- Recognize filtering: "only male arrests", "excluding juveniles"

QUERY COMPLEXITY LEVELS:
- Simple: Single city, single year
- Moderate: Multiple cities or years, basic comparisons
- Complex: Multi-dimensional analysis, statistical operations
- Advanced: Pattern recognition, predictive insights

RESPONSE CONFIDENCE:
- High (0.9+): Clear, unambiguous queries
- Medium (0.7-0.9): Some ambiguity but intent is clear
- Low (0.5-0.7): Requires clarification
- Very Low (<0.5): Cannot process reliably

Return ONLY valid JSON (no markdown, no explanation):
{
  "intent": "",
  "cities": [],
  "years": [],
  "gender": "",
  "crime": "",
  "aggregation": "",
  "top_n": 0,
  "confidence": 0.0,
  "complexity": "simple|moderate|complex|advanced",
  "query_type": "data_request|comparison|analysis|exploration",
  "filters": [],
  "statistical_operation": ""
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