from flask import Blueprint, request, jsonify
from services.data_loader import crime_data
from services.dataset_router import detect_dataset
from services.analytics_engine import calculate_city_totals
from services.insight_generator import generate_insight
from services.llm_extractor import llm_extract
from chat.government_chat import handle_government_chat
from chat.foreign_chat import handle_foreign_chat

chat_bp = Blueprint("chat", __name__)
VALID_CRIMES = [
    "murder",
    "rape",
    "kidnapping",
    "theft",
    "robbery",
    "burglary",
    "assault",
    "dowry death",
    "cyber crime"
]
INTENT_HANDLERS = {
    "trend": "handle_trend",
    "city_comparison": "handle_city_comparison",
    "city_trend": "handle_multi_year_city",
    "city_single": "handle_single_city"
}

@chat_bp.route("/chat", methods=["POST"])
def chat():

    message = request.json.get("message", "").strip()
    structured = llm_extract(message)

    dataset_type = detect_dataset(message, structured)

    if dataset_type == "government":
     return handle_government_chat(
        structured.get("intent"),
        structured.get("years"),
        structured
    )

    if dataset_type == "foreign":
     return handle_foreign_chat(
        structured.get("intent"),
        structured.get("years"),
        structured
    )
    
    

# 🔥 AUTO CRIME ROUTING HERE
    crime = structured.get("crime")
    if crime and crime.lower() in VALID_CRIMES:
     return handle_government_chat(
    structured.get("intent"),
    structured.get("years"),
    structured
)
    

    # ===============================
    # CITY / GENDER LOGIC
    # ===============================
    city_list = structured.get("cities", [])
    years = structured.get("years", [])
    gender = structured.get("gender")

    # Convert valid years
    years = [str(y) for y in years if str(y) in crime_data]

    if not years:
        years = [max(crime_data.keys())]

    # ======================================================
    # 🔥 GENDER + YEAR ONLY (NO CITY)
    # Example: "Male arrests 2020"
    # ======================================================
    if not city_list and gender:

        results = {}

        for yr in years:
            df = crime_data[yr]
            total = 0

            for _, row in df.iterrows():
                total += calculate_city_totals(row.to_dict(), gender)

            results[yr] = total

        return jsonify({
            "type": "trend",
            "title": f"{gender.title()} Arrest Trend",
            "data": results,
            "source": "NCRB Dataset (2016–2020)"
        })

    # ======================================================
    # MULTI-CITY SINGLE-YEAR
    # ======================================================
    if len(city_list) >= 2 and len(years) == 1:

        year = years[0]
        df = crime_data[year]
        results = {}

        for city in city_list[:2]:
            row = df[df["City"].str.contains(city, case=False, na=False)]

            if not row.empty:
                data = row.iloc[0].to_dict()
                results[city] = calculate_city_totals(data, gender)

        insight = generate_insight(message, {
            "year": year,
            "comparison_data": results
        })

        return jsonify({
            "type": "multi_city",
            "title": f"{gender.title() if gender else 'Total'} Arrest Comparison - {year}",
            "data": results,
            "insight": insight,
            "source": "NCRB Dataset (2016–2020)"
        })

    # ======================================================
    # MULTI-YEAR SINGLE-CITY
    # ======================================================
    if len(city_list) == 1 and len(years) > 1:

        city = city_list[0]
        results = {}

        for yr in years:
            df = crime_data[yr]
            row = df[df["City"].str.contains(city, case=False, na=False)]

            if not row.empty:
                data = row.iloc[0].to_dict()
                results[yr] = calculate_city_totals(data, gender)

        insight = generate_insight(message, {
            "city": city,
            "multi_year_data": results
        })

        return jsonify({
            "type": "multi_year_city",
            "title": f"{gender.title() if gender else 'Total'} Arrest Trend - {city}",
            "data": results,
            "insight": insight,
            "source": "NCRB Dataset (2016–2020)"
        })

    # ======================================================
    # SINGLE CITY SINGLE YEAR
    # ======================================================
    if len(city_list) == 1 and len(years) == 1:

        city = city_list[0]
        year = years[0]
        df = crime_data[year]

        row = df[df["City"].str.contains(city, case=False, na=False)]

        if row.empty:
            return jsonify({
                "type": "error",
                "summary": "City not found"
            })

        data = row.iloc[0].to_dict()
        total = calculate_city_totals(data, gender)

        insight = generate_insight(message, {
            "city": city,
            "year": year,
            "total_arrests": total
        })

        return jsonify({
            "type": "city",
            "title": f"{gender.title() if gender else 'Total'} Arrests - {city} ({year})",
            "data": {"Arrests": total},
            "insight": insight,
            "source": "NCRB Dataset (2016–2020)"
        })

    return jsonify({
        "type": "error",
        "summary": "Unable to interpret request."
    })