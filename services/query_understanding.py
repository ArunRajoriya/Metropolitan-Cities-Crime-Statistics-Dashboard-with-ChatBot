"""
Query Understanding - Handle ambiguous and complex queries
"""
import re
from services.data_loader import crime_data


def detect_query_type(message, structured):
    """Detect the type of query and required data"""
    msg = message.lower()
    
    query_types = {
        "comparison": ["compare", "vs", "versus", "between", "difference"],
        "ranking": ["top", "bottom", "highest", "lowest", "best", "worst", "rank"],
        "trend": ["trend", "over time", "change", "growth", "increase", "decrease", "year over year"],
        "statistics": ["average", "mean", "median", "total", "sum", "statistics", "stats"],
        "percentage": ["percentage", "percent", "%", "ratio", "proportion"],
        "specific": ["how many", "what is", "show me", "tell me"],
        "analysis": ["analyze", "analysis", "breakdown", "detailed", "in-depth"]
    }
    
    detected_types = []
    for qtype, keywords in query_types.items():
        if any(keyword in msg for keyword in keywords):
            detected_types.append(qtype)
    
    return detected_types if detected_types else ["specific"]


def extract_time_range(message):
    """Extract time range from query"""
    msg = message.lower()
    
    # Pattern: "from 2016 to 2020"
    pattern1 = r"from\s+(\d{4})\s+to\s+(\d{4})"
    match = re.search(pattern1, msg)
    if match:
        return list(range(int(match.group(1)), int(match.group(2)) + 1))
    
    # Pattern: "between 2016 and 2020"
    pattern2 = r"between\s+(\d{4})\s+and\s+(\d{4})"
    match = re.search(pattern2, msg)
    if match:
        return list(range(int(match.group(1)), int(match.group(2)) + 1))
    
    # Pattern: "2016-2020" or "2016 to 2020"
    pattern3 = r"(\d{4})\s*[-–to]\s*(\d{4})"
    match = re.search(pattern3, msg)
    if match:
        return list(range(int(match.group(1)), int(match.group(2)) + 1))
    
    return None


def extract_top_n(message):
    """Extract top N value from query"""
    msg = message.lower()
    
    # Pattern: "top 5", "top 10", "top arrest 10", etc.
    patterns = [
        r"top\s+(?:arrest\s+|crime\s+|city\s+|cities\s+)*(\d{1,2})",  # Limit to 1-2 digits to avoid years
        r"first\s+(\d{1,2})",
        r"(\d{1,2})\s+highest",
        r"(\d{1,2})\s+lowest"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, msg)
        if match:
            num = int(match.group(1))
            # Reasonable limits for top N queries
            if 1 <= num <= 50:
                return num
    
    # Default top N
    if "top" in msg:
        return 3
    
    return None


def detect_aggregation_type(message):
    """Detect type of aggregation requested"""
    msg = message.lower()
    
    if any(word in msg for word in ["average", "mean", "avg"]):
        return "average"
    elif any(word in msg for word in ["total", "sum", "all"]):
        return "total"
    elif any(word in msg for word in ["median", "middle"]):
        return "median"
    elif any(word in msg for word in ["maximum", "max", "highest"]):
        return "max"
    elif any(word in msg for word in ["minimum", "min", "lowest"]):
        return "min"
    
    return None


def is_question_about_data_availability(message):
    """Check if user is asking about data availability"""
    msg = message.lower()
    
    availability_keywords = [
        "do you have", "is there", "available", "can you show",
        "what data", "which years", "which cities"
    ]
    
    return any(keyword in msg for keyword in availability_keywords)


def extract_comparison_entities(message, structured):
    """Extract entities being compared"""
    cities = structured.get("cities", [])
    years = structured.get("years", [])
    
    # Check if comparing cities
    if len(cities) >= 2:
        return {"type": "cities", "entities": cities}
    
    # Check if comparing years
    if len(years) >= 2:
        return {"type": "years", "entities": years}
    
    # Check if comparing genders
    msg = message.lower()
    if any(word in msg for word in ["male", "female", "men", "women"]) and \
       any(word in msg for word in ["compare", "vs", "versus", "difference"]):
        return {"type": "genders", "entities": ["male", "female"]}
    
    return None


def needs_clarification(structured, message):
    """Determine if query needs clarification"""
    msg = message.lower()
    
    # Check if too vague
    vague_queries = [
        "tell me about crime",
        "show me data",
        "what about arrests",
        "crime statistics"
    ]
    
    if any(vague in msg for vague in vague_queries):
        return True, "Your query is too general. Please specify a city, year, or type of information."
    
    # Check if conflicting intents
    if structured.get("intent") == "city_comparison" and len(structured.get("cities", [])) < 2:
        return True, "You mentioned comparison but I only detected one city. Which cities would you like to compare?"
    
    # Check if missing critical info
    if "trend" in msg and len(structured.get("years", [])) < 2:
        return True, "For trend analysis, please specify a time range (e.g., 'from 2016 to 2020')."
    
    return False, None


def suggest_related_queries(structured, message):
    """Suggest related queries based on current query"""
    suggestions = []
    
    cities = structured.get("cities", [])
    years = structured.get("years", [])
    
    if cities and len(cities) == 1:
        city = cities[0]
        suggestions.append(f"Compare {city} with another city")
        suggestions.append(f"Show trend for {city} over multiple years")
        suggestions.append(f"Gender breakdown for {city}")
    
    if years and len(years) == 1:
        year = years[0]
        suggestions.append(f"Top 10 cities in {year}")
        suggestions.append(f"Compare {year} with other years")
    
    if not suggestions:
        suggestions = [
            "Show me top 5 cities by arrests in 2020",
            "Compare Delhi and Mumbai from 2016 to 2020",
            "What's the trend for Bangalore?",
            "Gender-wise breakdown for Chennai 2019"
        ]
    
    return suggestions[:3]


def parse_complex_query(message):
    """Parse complex multi-part queries"""
    # Split by conjunctions
    parts = re.split(r'\s+and\s+|\s+also\s+|\s+plus\s+', message.lower())
    
    if len(parts) > 1:
        return {
            "is_complex": True,
            "parts": parts,
            "suggestion": "I detected multiple questions. Let me answer them one by one."
        }
    
    return {"is_complex": False}
