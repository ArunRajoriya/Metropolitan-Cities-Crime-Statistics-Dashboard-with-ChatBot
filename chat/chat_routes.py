from flask import Blueprint, request, jsonify, session
import re

chat_bp = Blueprint("chat", __name__)

# =========================================================
# Intent Keywords
# =========================================================
INTENTS = {
    "highest": ["highest", "maximum", "most", "top"],
    "lowest": ["lowest", "minimum", "least"],
    "trend": ["trend", "increase", "growth", "change", "rise", "decline"],
    "arrest": ["arrest", "arrests", "detained"],
    "population": ["population", "residents", "people"]
}


# =========================================================
# Intent Detection
# =========================================================
def detect_intent(message):
    for intent, keywords in INTENTS.items():
        for word in keywords:
            if re.search(rf"\b{word}\b", message):
                return intent
    return None


# =========================================================
# AI Summary Generator
# =========================================================
def generate_summary(intent, city, year, metrics):

    # =====================================================
    # Arrest Summary
    # =====================================================
    if intent == "arrest":

        total = int(metrics.get("Total Persons Arrested", "0").replace(",", ""))
        male = int(metrics.get("Male Arrested", "0").replace(",", ""))
        female = int(metrics.get("Female Arrested", "0").replace(",", ""))

        male_percent = round((male / total) * 100, 2) if total else 0
        female_percent = round((female / total) * 100, 2) if total else 0

        gender_insight = (
            "Male arrests overwhelmingly dominate the statistics."
            if male_percent > 90 else
            "Male arrests form a strong majority."
            if male_percent > 70 else
            "Arrests are relatively balanced across genders."
        )

        risk_level = (
            "High Risk City"
            if total > 100000 else
            "Moderate Risk City"
            if total > 30000 else
            "Lower Risk City"
        )

        return (
            f"In {year}, {city} recorded {total:,} total arrests. "
            f"Male arrests accounted for {male_percent}% while female arrests "
            f"accounted for {female_percent}%. "
            f"{gender_insight} "
            f"Based on arrest volume, this city can be classified as a {risk_level}."
        )

    # =====================================================
    # Trend Summary
    # =====================================================
    if intent == "trend":

        change = metrics.get("Overall Change", "0%")
        observation = metrics.get("Observation", "")

        try:
            numeric_change = float(change.replace("%", ""))
        except:
            numeric_change = 0

        direction = (
            "significant growth"
            if numeric_change > 20 else
            "moderate change"
        )

        return (
            f"Between 2016 and 2020, {city} recorded a {change} overall change in arrests. "
            f"This reflects a {direction} in criminal activity patterns. "
            f"{observation}"
        )

    # =====================================================
    # Population Summary
    # =====================================================
    if intent == "population":
        return (
            f"In {year}, the total population of {city} was "
            f"{metrics.get('Total Population')}."
        )

    # =====================================================
    # Highest Summary
    # =====================================================
    if intent == "highest":
        return (
            f"In {year}, {city} recorded the highest arrests among metropolitan cities "
            f"with {metrics.get('Highest Arrests')} total arrests."
        )

    # =====================================================
    # Lowest Summary
    # =====================================================
    if intent == "lowest":
        return (
            f"In {year}, {city} recorded the lowest arrests among metropolitan cities "
            f"with {metrics.get('Lowest Arrests')} total arrests."
        )

    return "Crime statistics summary generated."

# =========================================================
# Main Chat Route
# =========================================================
@chat_bp.route("/chat", methods=["POST"])
def chat():

    from app import crime_data

    message = request.json.get("message", "").lower().strip()
    intent = detect_intent(message)

    # =========================================================
    # Year Extraction
    # =========================================================
    year_match = re.search(r'20\d{2}', message)

    if year_match:
        year = year_match.group()
    else:
        year = session.get("last_year")

    # Trend does NOT require specific year
    if intent != "trend":
        if not year:
            return jsonify({"type": "error", "message": "Please specify a year."})

        if year not in crime_data:
            available_years = ", ".join(sorted(crime_data.keys()))
            return jsonify({
                "type": "error",
                "message": f"Data available only for years: {available_years}."
            })

    # Load dataframe only if year-based query
    if year in crime_data:
        df = crime_data[year]

    # =========================================================
    # City Extraction
    # =========================================================
    city = None

    if year in crime_data:
        for c in df["City"].dropna().unique():
            clean_city = re.sub(r"\(.*?\)", "", str(c)).strip().lower()
            if clean_city in message:
                city = c
                break

    if not city:
        city = session.get("last_city")

    if not intent:
        intent = session.get("last_intent")

    # Store memory
    if city:
        session["last_city"] = city
    if intent:
        session["last_intent"] = intent
    if year:
        session["last_year"] = year

    # =========================================================
    # Highest Arrest City
    # =========================================================
    if intent == "highest":

        clean_df = df.dropna(subset=[
            "City",
            "Total - Total Persons Arrested by age and Sex"
        ])

        sorted_df = clean_df.sort_values(
            "Total - Total Persons Arrested by age and Sex",
            ascending=False
        )

        top_city = str(sorted_df.iloc[0]["City"])
        top_value = int(sorted_df.iloc[0]
                        ["Total - Total Persons Arrested by age and Sex"])

        metrics = {
            "Highest Arrests": f"{top_value:,}"
        }

        summary = generate_summary(intent, top_city, year, metrics)

        return jsonify({
            "type": "comparison",
            "title": "Metropolitan Crime Statistics",
            "city": top_city,
            "year": year,
            "metrics": metrics,
            "summary": summary,
            "source": "NCRB Dataset (2016–2020)"
        })

    # =========================================================
    # Lowest Arrest City
    # =========================================================
    if intent == "lowest":

        clean_df = df.dropna(subset=[
            "City",
            "Total - Total Persons Arrested by age and Sex"
        ])

        sorted_df = clean_df.sort_values(
            "Total - Total Persons Arrested by age and Sex",
            ascending=True
        )

        low_city = str(sorted_df.iloc[0]["City"])
        low_value = int(sorted_df.iloc[0]
                        ["Total - Total Persons Arrested by age and Sex"])

        metrics = {
            "Lowest Arrests": f"{low_value:,}"
        }

        summary = generate_summary(intent, low_city, year, metrics)

        return jsonify({
            "type": "comparison",
            "title": "Metropolitan Crime Statistics",
            "city": low_city,
            "year": year,
            "metrics": metrics,
            "summary": summary,
            "source": "NCRB Dataset (2016–2020)"
        })

    # =========================================================
    # Arrest Query (City Specific)
    # =========================================================
    if intent == "arrest" and city:

        row = df[df["City"] == city]

        if row.empty:
            return jsonify({
                "type": "error",
                "message": f"No arrest data found for {city} in {year}."
            })

        total_arrest = int(
            row["Total - Total Persons Arrested by age and Sex"].values[0])
        male_arrest = int(row["Total - Male"].values[0])
        female_arrest = int(row["Total - Female"].values[0])

        ratio = round(male_arrest / female_arrest,
                      2) if female_arrest > 0 else "N/A"

        metrics = {
            "Total Persons Arrested": f"{total_arrest:,}",
            "Male Arrested": f"{male_arrest:,}",
            "Female Arrested": f"{female_arrest:,}",
            "Male : Female Arrest Ratio": f"{ratio} : 1"
        }

        summary = generate_summary(intent, city, year, metrics)

        return jsonify({
            "type": "arrest",
            "title": "Metropolitan Crime Statistics",
            "city": city,
            "year": year,
            "metrics": metrics,
            "summary": summary,
            "source": "NCRB Dataset (2016–2020)"
        })

    # =========================================================
    # Population Query
    # =========================================================
    if intent == "population" and city:

        row = df[df["City"] == city]

        if row.empty:
            return jsonify({
                "type": "error",
                "message": f"No population data found for {city} in {year}."
            })

        total_pop = int(row["Total Population"].values[0])

        metrics = {
            "Total Population": f"{total_pop:,}"
        }

        summary = generate_summary(intent, city, year, metrics)

        return jsonify({
            "type": "population",
            "title": "Metropolitan Crime Statistics",
            "city": city,
            "year": year,
            "metrics": metrics,
            "summary": summary,
            "source": "NCRB Dataset (2016–2020)"
        })

    # =========================================================
    # Trend Analysis (2016–2020)
    # =========================================================
    if intent == "trend" and city:

        trend_data = {}

        for yr in sorted(crime_data.keys()):
            temp_df = crime_data[yr]

            row = temp_df[
    temp_df["City"].str.replace(r"\(.*?\)", "", regex=True)
    .str.strip()
    .str.lower() ==
    re.sub(r"\(.*?\)", "", city).strip().lower()
]

            if not row.empty:
                try:
                    trend_data[yr] = int(
                        row["Total - Total Persons Arrested by age and Sex"].values[0]
                    )
                except:
                    pass

        if len(trend_data) < 2:
            return jsonify({
                "type": "error",
                "message": f"Insufficient data available for trend analysis of {city}."
            })

        years_sorted = sorted(trend_data.keys())

        first_value = trend_data[years_sorted[0]]
        last_value = trend_data[years_sorted[-1]]

        percent_change = round(
            ((last_value - first_value) / first_value) * 100, 2
        ) if first_value > 0 else 0

        observation = (
            "Arrests show an increasing trend."
            if percent_change > 0
            else "Arrests show a decreasing trend."
            if percent_change < 0
            else "Arrests remain stable over the period."
        )

        metrics = {
            f"{yr} Arrests": f"{trend_data[yr]:,}"
            for yr in years_sorted
        }

        metrics["Overall Change"] = f"{percent_change}%"
        metrics["Observation"] = observation

        summary = generate_summary(intent, city, "2016–2020", metrics)

        return jsonify({
            "type": "trend",
            "title": "Metropolitan Crime Trend Analysis",
            "city": city,
            "year": "2016–2020",
            "metrics": metrics,
            "summary": summary,
            "source": "NCRB Dataset (2016–2020)"
        })

    # =========================================================
    # Fallback
    # =========================================================
    return jsonify({
        "type": "error",
        "message": "Unable to process query. Please specify a valid city and year."
    })