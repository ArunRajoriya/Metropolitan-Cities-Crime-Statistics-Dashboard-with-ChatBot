from flask import Blueprint, request, jsonify, current_app
import re

chat_bp = Blueprint("chat", __name__)

# =========================================================
# API CALL HELPER (Orchestrator Layer)
# =========================================================
def call_api(endpoint, params=None):
    with current_app.test_client() as client:
        response = client.get(endpoint, query_string=params)
        return response.get_json()


# =========================================================
# INTENT DETECTION (Business Level)
# =========================================================
def detect_intent(message):

    message = message.lower()

    # Specific first
    if any(word in message for word in ["compare", "comparison", " vs ", "versus"]):
        return "city_comparison"

    if any(word in message for word in ["highest", "top"]):
        return "highest"

    if any(word in message for word in ["lowest", "minimum", "least"]):
        return "lowest"

    if "trend" in message:
        return "year_trend"

    if "ratio" in message:
        return "gender_ratio"

    if "population" in message:
        return "home_kpis"

    if any(word in message for word in ["profile", "details", "arrest", "arrests"]):
        return "city_profile"

    return "unknown"


# =========================================================
# PARAMETER EXTRACTION
# =========================================================
def extract_parameters(message):

    from services.data_loader import crime_data
    import re

    year_match = re.search(r'20\d{2}', message)
    year = year_match.group() if year_match else max(crime_data.keys())

    city = None
    df = crime_data[year]

    for c in df["City"].dropna().unique():
        clean_city = re.sub(r"\(.*?\)", "", str(c)).strip().lower()

        if clean_city in message:
            city = c
            break

    return year, city


# =========================================================
# MAIN CHAT ROUTE
# =========================================================
@chat_bp.route("/chat", methods=["POST"])
def chat():

    message = request.json.get("message", "").lower().strip()

    intent = detect_intent(message)
    year, city = extract_parameters(message)

    # =====================================================
    # CITY COMPARISON
    # =====================================================
    if intent == "city_comparison":

        data = call_api("/api/city-comparison", {"year": year})

        return jsonify({
            "type": "comparison",
            "title": f"City Comparison - {year}",
            "context": {"year": year},
            "data": data,
            "summary": f"Ranking of metropolitan cities by total arrests in {year}.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # CITY PROFILE
    # =====================================================
    if intent == "city_profile" and city:

        data = call_api("/api/city-profile", {
            "year": year,
            "city": city
        })

        return jsonify({
            "type": "city_profile",
            "title": f"{city} Crime Profile - {year}",
            "context": {"year": year, "city": city},
            "data": data,
            "summary": f"Detailed arrest breakdown for {city} in {year}.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # GENDER RATIO
    # =====================================================
    if intent == "gender_ratio":

        data = call_api("/api/gender-ratio", {"year": year})

        return jsonify({
            "type": "gender_ratio",
            "title": f"Gender Arrest Ratio - {year}",
            "context": {"year": year},
            "data": data,
            "summary": f"Male to female arrest ratio in {year}.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # POPULATION KPIs
    # =====================================================
    if intent == "home_kpis":

        data = call_api("/api/home-kpis")

        return jsonify({
            "type": "kpi",
            "title": "Population Indicators",
            "context": {},
            "data": data,
            "summary": "Latest population indicators.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # YEAR TREND
    # =====================================================
    if intent == "year_trend":

        data = call_api("/api/year-trend")

        return jsonify({
            "type": "trend",
            "title": "Year-wise Arrest Trend",
            "context": {},
            "data": data,
            "summary": "Trend of arrests across available years.",
            "source": "NCRB Dataset (2016–2020)"
        })

    if intent == "highest":

        data = call_api("/api/city-comparison", {"year": year})

        sorted_cities = sorted(
            [(k, int(v)) for k, v in data.items()],
            key=lambda x: x[1],
            reverse=True
        )

        top_city, top_value = sorted_cities[0]

        return jsonify({
            "type": "highest",
            "title": f"Highest Arrest City - {year}",
            "context": {"year": year},
            "data": {top_city: top_value},
            "summary": f"{top_city} recorded the highest arrests in {year}.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =========================
    # LOWEST
    # =========================
    if intent == "lowest":

        data = call_api("/api/city-comparison", {"year": year})

        sorted_cities = sorted(
            [(k, int(v)) for k, v in data.items()],
            key=lambda x: x[1]
        )

        lowest_city, lowest_value = sorted_cities[0]

        return jsonify({
            "type": "lowest",
            "title": f"Lowest Arrest City - {year}",
            "context": {"year": year},
            "data": {lowest_city: lowest_value},
            "summary": f"{lowest_city} recorded the lowest arrests in {year}.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =========================
    # FALLBACK
    # =========================
    return jsonify({
        "type": "error",
        "summary": "Unable to process request."
    })