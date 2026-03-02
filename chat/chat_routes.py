from flask import Blueprint, request, jsonify
from services.data_loader import crime_data
from services.dataset_router import detect_dataset
from services.analytics_engine import calculate_city_totals
from services.insight_generator import generate_insight
from services.llm_extractor import llm_extract
from chat.government_chat import handle_government_chat
from chat.foreign_chat import handle_foreign_chat
from chat.advanced_features import handle_juvenile

chat_bp = Blueprint("chat", __name__)

VALID_CRIMES = [
    "murder",
    "culpable homicide not amounting to murder",
    "causing death by negligence",
    "dowry deaths",
    "abetment of suicide",
    "attempt to commit murder",
    "attempt to commit culpable homicide",
    "attempt to commit suicide",
    "hurt",
    "grievous hurt",
    "acid attack",
    "attempt to acid attack",
    "wrongful restraint/confinement",
    "assault on women with intent to outrage her modesty",
    "sexual harassment",
    "assault or use of criminal force on women with intent to disrobe",
    "voyeurism",
    "stalking",
    "kidnapping and abduction",
    "kidnapping for ransom",
    "procuration of minor girls",
    "importation of girls from foreign country",
    "human trafficking",
    "rape",
    "attempt to commit rape",
    "unnatural offences",
    "offences against state",
    "sedition",
    "unlawful assembly",
    "riots",
    "offences promoting enmity between different groups",
    "affray",
    "theft",
    "auto/motor vehicle theft",
    "other thefts",
    "burglary",
    "extortion & blackmailing",
    "robbery",
    "dacoity",
    "criminal misappropriation",
    "criminal breach of trust",
    "dishonestly receiving/dealing-in stolen property",
    "counterfeiting",
    "counterfeit currency & bank notes",
    "forgery, cheating & fraud",
    "fraud",
    "other cheating",
    "other forgery",
    "offences relating to elections",
    "disobedience to order duly promulgated by public servant",
    "harbouring an offender",
    "rash driving on public way",
    "sale of obscene books/objects",
    "obscene acts and songs at public places",
    "offences relating to religion",
    "cheating by impersonation",
    "offences related to mischief",
    "arson",
    "criminal trespass",
    "cruelty by husband or his relatives",
    "circulate false/fake news/rumours",
    "criminal intimidation",
    "insult to the modesty of women",
    "other ipc crimes",
    "total cognizable ipc crimes"
]


@chat_bp.route("/chat", methods=["POST"])
def chat():

    message = request.json.get("message", "").strip()
    structured = llm_extract(message) or {}
    message_lower = message.lower()

    # ================= DATASET ROUTING =================
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

    # ================= CRIME ROUTING =================
    crime = structured.get("crime")
    if crime and crime.lower() in VALID_CRIMES:
        return handle_government_chat(
            structured.get("intent"),
            structured.get("years"),
            structured
        )

    # ================= BASIC EXTRACTION =================
    city_list = structured.get("cities", [])
    years = structured.get("years", [])
    gender = structured.get("gender")
    intent = structured.get("intent", "")

    # Validate years
    years = [str(y) for y in years if str(y) in crime_data]
    if not years:
        years = [max(crime_data.keys())]

    year = years[0]

    # Manual gender fallback
    if not gender:
        if "male" in message_lower:
            gender = "male"
        elif "female" in message_lower:
            gender = "female"

    # Manual intent fallback
    if "top" in message_lower and ("3" in message_lower or "three" in message_lower):
     intent = "top"
    elif "highest" in message_lower or "maximum" in message_lower or "most" in message_lower:
        intent = "highest"
    elif "lowest" in message_lower or "minimum" in message_lower or "least" in message_lower:
        intent = "lowest"
        # Detect compare intent
    if "compare" in message_lower or "vs" in message_lower or "between" in message_lower:
        intent = "compare"
    # ================= JUVENILE =================
    if "juvenile" in message_lower:

        city = city_list[0] if city_list else None

        category = "total"
        if "boys" in message_lower:
            category = "boys"
        elif "girls" in message_lower:
            category = "girls"

        ranking = None
        if intent == "top":
            ranking = "top"
        elif intent == "highest":
            ranking = "highest"
        elif intent == "lowest":
            ranking = "lowest"

        return handle_juvenile(
            year=year,
            city=city,
            category=category,
            ranking=ranking,
            top_n=3
        )

    # ================= TOP 3 =================
    if intent == "top":

        df = crime_data[year].copy()
        df = df[df["City"].notna()]
        df = df[~df["City"].str.lower().str.contains("total", na=False)]

        df["value"] = df.apply(
            lambda row: calculate_city_totals(row.to_dict(), gender),
            axis=1
        )

        df_sorted = df.sort_values(by="value", ascending=False).head(3)
        results = dict(zip(df_sorted["City"], df_sorted["value"]))

        return jsonify({
            "type": "top_3",
            "title": f"Top 3 {gender.title() + ' ' if gender else ''}Arrest Cities - {year}",
            "data": results,
            "source": "NCRB Dataset (2016–2020)"
        })

        # ================= MATRIX COMPARISON =================
    if intent == "compare" and len(city_list) >= 2 and len(years) >= 2:

        matrix = {}

        for city in city_list:
            matrix[city] = {}

            for yr in years:
                df = crime_data[yr]
                row = df[df["City"].str.contains(city, case=False, na=False)]

                if not row.empty:
                    total = calculate_city_totals(row.iloc[0].to_dict(), gender)
                    matrix[city][yr] = total
                else:
                    matrix[city][yr] = 0

        return jsonify({
            "type": "matrix_comparison",
            "title": "City-wise Arrest Comparison",
            "data": matrix,
            "source": "NCRB Dataset (2016–2020)"
        })
    # ================= MULTI CITY =================
    if len(city_list) >= 2:

        df = crime_data[year]
        results = {}

        for city in city_list[:2]:
            row = df[df["City"].str.contains(city, case=False, na=False)]
            if not row.empty:
                data = row.iloc[0].to_dict()
                results[city] = calculate_city_totals(data, gender)

        if not results:
            return jsonify({"type": "error", "summary": "City not found."})

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

    # ================= HIGHEST / LOWEST =================
    if intent in ["highest", "lowest"]:

        df = crime_data[year].copy()
        df = df[df["City"].notna()]
        df = df[~df["City"].str.lower().str.contains("total", na=False)]

        city_totals = {}

        for _, row in df.iterrows():
            city_name = row["City"]
            total = calculate_city_totals(row.to_dict(), gender)
            city_totals[city_name] = int(total)

        if not city_totals:
            return jsonify({"type": "error", "summary": "No data available."})

        sorted_data = sorted(
            city_totals.items(),
            key=lambda x: x[1],
            reverse=(intent == "highest")
        )

        top_city, top_value = sorted_data[0]

        return jsonify({
            "type": intent,
            "title": f"{intent.capitalize()} {gender.title() + ' ' if gender else ''}Arrest City - {year}",
            "data": {top_city: top_value},
            "source": "NCRB Dataset (2016–2020)"
        })

    # ================= GENDER TOTAL =================
    if not city_list and gender:

        df = crime_data[year]
        total = sum(
            calculate_city_totals(row.to_dict(), gender)
            for _, row in df.iterrows()
        )

        return jsonify({
            "type": "gender_total",
            "title": f"{gender.title()} Arrest Total - {year}",
            "data": {"Total": total},
            "source": "NCRB Dataset (2016–2020)"
        })

    # ================= SINGLE CITY =================
    if len(city_list) == 1:

        city = city_list[0]
        results = {}

        for yr in years:
            df = crime_data[yr]
            row = df[df["City"].str.contains(city, case=False, na=False)]

            if not row.empty:
                data = row.iloc[0].to_dict()
                total = calculate_city_totals(data, gender)
                results[yr] = total

        if not results:
            return jsonify({"type": "error", "summary": "City not found"})

        if len(results) == 1:
            yr = list(results.keys())[0]
            return jsonify({
                "type": "city",
                "title": f"{gender.title() if gender else 'Total'} Arrests - {city} ({yr})",
                "data": {"Arrests": results[yr]},
                "source": "NCRB Dataset (2016–2020)"
            })

        return jsonify({
            "type": "city_multi_year",
            "title": f"{gender.title() if gender else 'Total'} Arrest Comparison - {city}",
            "data": results,
            "source": "NCRB Dataset (2016–2020)"
        })

   # ================= YEAR TOTAL =================
    if not city_list and not gender and years:

        df = crime_data[year]
        total = sum(
            calculate_city_totals(row.to_dict(), None)
            for _, row in df.iterrows()
        )

    return jsonify({
        "type": "year_total",
        "title": f"Total Arrests - {year}",
        "data": {"Total": total},
        "source": "NCRB Dataset (2016–2020)"
    })
    # ================= FALLBACK =================
    return jsonify({
    "type": "fallback",
    "summary": "I couldn’t detect a city or year. Try asking like: 'Delhi 2019' or 'Highest arrest 2020'.",
    "suggestions": [
        "Total arrested 2020",
        "Delhi 2019",
        "Compare Delhi Mumbai 2019",
        "Highest arrest 2019"
    ]
})