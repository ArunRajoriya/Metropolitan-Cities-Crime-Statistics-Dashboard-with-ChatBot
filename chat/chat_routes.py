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

    # Comparison
    if any(word in message for word in ["compare", "comparison", " vs ", "versus"]):
        return "city_comparison"

    # 🔥 Gender FIRST
    if re.search(r"\bfemale\b", message) and re.search(r"\barrest", message):
        return "female_total"

    if re.search(r"\bmale\b", message) and re.search(r"\barrest", message):
        return "male_total"

    # Highest / Lowest
    if any(word in message for word in ["highest", "top"]):
        return "highest"

    if any(word in message for word in ["lowest", "minimum", "least"]):
        return "lowest"

    # Trend
    if any(word in message for word in ["trend", "growth", "increase", "over time"]):
        return "year_trend"

    # Ratio
    if "ratio" in message:
        return "gender_ratio"

    # Population
    if "population" in message:
        return "home_kpis"
    
    # Generic profile LAST
    if any(word in message for word in ["profile", "details", "arrest", "arrests"]):
        return "city_profile"
    
    if "question" in message or "help" in message:
     return "questions"

    return "unknown"

# =========================================================
# PARAMETER EXTRACTION
# =========================================================


from services.data_loader import crime_data

def extract_parameters(message):

    message = message.lower()

    # -------- Extract all years --------
    years = re.findall(r'20\d{2}', message)
    available_years = list(crime_data.keys())

    years = [y for y in years if y in available_years]

    if not years:
     years = [max(available_years)]

    # -------- Extract cities properly --------
    cities = []
    df = crime_data[years[0]]

    for c in df["City"].dropna().unique():

        # Clean dataset city
        clean_dataset_city = (
            re.sub(r"\(.*?\)", "", str(c))
            .strip()
            .lower()
        )

        # Clean message
        clean_message = message.lower()

        if clean_dataset_city in clean_message:
            cities.append(c)

    cities = list(dict.fromkeys(cities))

    return years, cities

    print("INTENT DETECTED:", intent)
    print("MESSAGE:", message)

@chat_bp.route("/chat", methods=["POST"])
def chat():

    message = request.json.get("message", "").lower().strip()

    intent = detect_intent(message)
    years, cities = extract_parameters(message)

    # =====================================================
    # QUESTIONS
    # =====================================================
    if intent == "questions":

        suggestions = [
            "Highest arrests 2020",
            "Lowest arrests 2019",
            "Compare Delhi and Mumbai 2020",
            "Compare Delhi and Mumbai 2016 and 2019",
            "City profile Mumbai 2020",
            "Female arrested",
            "Male arrested 2019",
            "Trend of arrests",
            "Gender ratio 2020",
            "Population stats"
        ]

        return jsonify({
            "type": "questions",
            "title": "You can ask questions like:",
            "data": suggestions,
            "summary": "Try any of the above queries to explore crime statistics.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # GENDER RATIO
    # =====================================================
    if intent == "gender_ratio":

        year = years[0]
        data = call_api("/api/gender-ratio", {"year": year})

        return jsonify({
            "type": "gender_ratio",
            "title": f"Gender Arrest Ratio - {year}",
            "data": data,
            "summary": f"Male to female arrest ratio in {year}.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # POPULATION
    # =====================================================
    if intent == "home_kpis":

        data = call_api("/api/home-kpis")

        return jsonify({
            "type": "kpi",
            "title": "Population Indicators",
            "data": data,
            "summary": "Latest population indicators.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # MULTI-CITY MULTI-YEAR
    # =====================================================
    if intent == "city_comparison" and len(cities) >= 2 and len(years) > 1:

        matrix = {}

        for city in cities[:2]:
            matrix[city] = {}

            for year in years:
                data = call_api("/api/city-profile", {
                    "year": year,
                    "city": city
                })

                total = data.get(
                    "Total - Total Persons Arrested by age and Sex", 0
                )
                matrix[city][year] = total

        return jsonify({
            "type": "matrix_comparison",
            "title": "Multi-City Multi-Year Comparison",
            "data": matrix,
            "summary": "Comparison across selected cities and years.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # MULTI-CITY SINGLE YEAR
    # =====================================================
    if intent == "city_comparison" and len(cities) >= 2:

        year = years[0]
        results = {}

        for city in cities[:2]:
            data = call_api("/api/city-profile", {
                "year": year,
                "city": city
            })

            results[city] = data.get(
                "Total - Total Persons Arrested by age and Sex", 0
            )

        return jsonify({
            "type": "multi_city",
            "title": f"City Comparison - {year}",
            "data": results,
            "summary": f"Comparison of selected cities in {year}.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # MULTI-YEAR SINGLE CITY
    # =====================================================
    if intent == "city_profile" and len(cities) == 1 and len(years) > 1:

        city = cities[0]
        results = {}

        for year in years:
            data = call_api("/api/city-profile", {
                "year": year,
                "city": city
            })

            results[year] = data.get(
                "Total - Total Persons Arrested by age and Sex", 0
            )

        return jsonify({
            "type": "multi_year_city",
            "title": f"{city} Arrest Comparison",
            "data": results,
            "summary": f"Comparison of total arrests in {city} across selected years.",
            "source": "NCRB Dataset (2016–2020)"
        })


    # =====================================================
    # SINGLE CITY PROFILE
    # =====================================================
    if intent == "city_profile" and len(cities) == 1:

        city = cities[0]
        year = years[0]

        data = call_api("/api/city-profile", {
            "year": year,
            "city": city
        })

        return jsonify({
            "type": "city_profile",
            "title": f"{city} Crime Profile - {year}",
            "data": data,
            "summary": f"Detailed arrest breakdown for {city} in {year}.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # MALE TOTAL
    # =====================================================
    if intent == "male_total":

        year_match = re.search(r'20\d{2}', message)

        if not year_match:
            result = {}
            for yr in crime_data.keys():
                data = call_api("/api/gender-ratio", {"year": yr})
                result[yr] = data.get("male", 0)

            return jsonify({
                "type": "trend",
                "title": "Male Arrest Trend",
                "data": result,
                "summary": "Trend of male arrests across available years.",
                "source": "NCRB Dataset (2016–2020)"
            })

        year = year_match.group()
        data = call_api("/api/gender-ratio", {"year": year})

        return jsonify({
            "type": "male_total",
            "title": f"Total Male Arrests - {year}",
            "data": {"Male Arrested": data.get("male", 0)},
            "summary": f"Total male arrests recorded in {year}.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # FEMALE TOTAL
    # =====================================================
    if intent == "female_total":

        year_match = re.search(r'20\d{2}', message)

        if not year_match:
            result = {}
            for yr in crime_data.keys():
                data = call_api("/api/gender-ratio", {"year": yr})
                result[yr] = data.get("female", 0)

            return jsonify({
                "type": "trend",
                "title": "Female Arrest Trend",
                "data": result,
                "summary": "Trend of female arrests across available years.",
                "source": "NCRB Dataset (2016–2020)"
            })

        year = year_match.group()
        data = call_api("/api/gender-ratio", {"year": year})

        return jsonify({
            "type": "female_total",
            "title": f"Total Female Arrests - {year}",
            "data": {"Female Arrested": data.get("female", 0)},
            "summary": f"Total female arrests recorded in {year}.",
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
            "data": data,
            "summary": "Trend of arrests across available years.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # HIGHEST
    # =====================================================
    if intent == "highest":

        year = years[0]
        data = call_api("/api/city-comparison", {"year": year})

        sorted_cities = sorted(
            data.items(),
            key=lambda x: int(x[1]),
            reverse=True
        )

        top_city, top_value = sorted_cities[0]

        return jsonify({
            "type": "highest",
            "title": f"Highest Arrest City - {year}",
            "data": {top_city: top_value},
            "summary": f"{top_city} recorded the highest arrests in {year}.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # LOWEST
    # =====================================================
    if intent == "lowest":

        year = years[0]
        data = call_api("/api/city-comparison", {"year": year})

        sorted_cities = sorted(
            data.items(),
            key=lambda x: int(x[1])
        )

        lowest_city, lowest_value = sorted_cities[0]

        return jsonify({
            "type": "lowest",
            "title": f"Lowest Arrest City - {year}",
            "data": {lowest_city: lowest_value},
            "summary": f"{lowest_city} recorded the lowest arrests in {year}.",
            "source": "NCRB Dataset (2016–2020)"
        })

    # =====================================================
    # FALLBACK
    # =====================================================
    return jsonify({
        "type": "error",
        "summary": "Unable to interpret request."
    })