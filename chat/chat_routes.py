from flask import Blueprint, request, jsonify
from services.data_loader import crime_data
from services.dataset_router import detect_dataset
from services.analytics_engine import calculate_city_totals
from services.insight_generator import generate_insight
from services.llm_extractor import llm_extract
from chat.government_chat import handle_government_chat
from chat.foreign_chat import handle_foreign_chat
from chat.advanced_features import handle_juvenile
from services.query_normalizer import normalize_query
from services.intelligent_query_handler import intelligent_handler
from services.query_understanding import (
    detect_query_type, extract_time_range, extract_top_n,
    needs_clarification, suggest_related_queries, is_question_about_data_availability
)
from services.advanced_analytics import (
    analyze_gender_gap, compare_with_average, get_percentile_rank
)
from services.response_formatter import (
    format_comparison_response, format_gender_analysis, format_number
)

chat_bp = Blueprint("chat", __name__)

VALID_CRIMES = [
    "murder","culpable homicide not amounting to murder","causing death by negligence",
    "dowry deaths","abetment of suicide","attempt to commit murder",
    "attempt to commit culpable homicide","attempt to commit suicide",
    "hurt","grievous hurt","acid attack","attempt to acid attack",
    "wrongful restraint/confinement","assault on women with intent to outrage her modesty",
    "sexual harassment","assault or use of criminal force on women with intent to disrobe",
    "voyeurism","stalking","kidnapping and abduction","kidnapping for ransom",
    "procuration of minor girls","importation of girls from foreign country",
    "human trafficking","rape","attempt to commit rape","unnatural offences",
    "offences against state","sedition","unlawful assembly","riots",
    "offences promoting enmity between different groups","affray",
    "theft","auto/motor vehicle theft","other thefts","burglary",
    "extortion & blackmailing","robbery","dacoity",
    "criminal misappropriation","criminal breach of trust",
    "dishonestly receiving/dealing-in stolen property",
    "counterfeiting","counterfeit currency & bank notes",
    "forgery, cheating & fraud","fraud","other cheating","other forgery",
    "offences relating to elections",
    "disobedience to order duly promulgated by public servant",
    "harbouring an offender","rash driving on public way",
    "sale of obscene books/objects","obscene acts and songs at public places",
    "offences relating to religion","cheating by impersonation",
    "offences related to mischief","arson","criminal trespass",
    "cruelty by husband or his relatives","circulate false/fake news/rumours",
    "criminal intimidation","insult to the modesty of women",
    "other ipc crimes","total cognizable ipc crimes"
]


@chat_bp.route("/chat", methods=["POST"])
def chat():

    message = request.json.get("message", "").strip()
    message_lower = message.lower()
    message = normalize_query(message)
    greetings = ["hi", "hello", "hey"]

    if message_lower in greetings:
        return jsonify({
            "type": "greeting",
            "summary": "Hello! I'm your intelligent crime analytics assistant. I can help you with:",
            "capabilities": [
                "City-wise crime statistics and comparisons",
                "Year-over-year trend analysis",
                "Gender-based arrest data",
                "Juvenile crime statistics",
                "Top/bottom city rankings",
                "Government and foreign crime data"
            ],
            "example": "Try asking: 'Compare Delhi and Mumbai arrests in 2020' or 'Show me the trend for Bangalore from 2016 to 2020'"
        })

    structured = llm_extract(message) or {}
    
    # Validate and auto-correct the query
    structured = intelligent_handler.validate_and_correct_query(structured)
    
    # Check if query needs clarification
    needs_help, clarification_msg = needs_clarification(structured, message)
    if needs_help:
        return jsonify({
            "type": "clarification",
            "summary": clarification_msg,
            "suggestions": suggest_related_queries(structured, message)
        })
    
    # Handle data availability questions
    if is_question_about_data_availability(message):
        return jsonify({
            "type": "info",
            "title": "Data Availability",
            "data": {
                "Available Years": "2016, 2019, 2020",
                "Total Cities": len(intelligent_handler.all_cities),
                "Datasets": "Crime Data, Government Data, Foreign Crime Data",
                "Features": "City comparisons, trends, rankings, gender analysis, juvenile statistics"
            },
            "summary": f"I have crime data for {len(intelligent_handler.all_cities)} Indian cities across years 2016, 2019, and 2020."
        })
    
    # Detect query types for better handling
    query_types = detect_query_type(message, structured)
    
    # Extract time range if mentioned
    time_range = extract_time_range(message)
    if time_range:
        structured["years"] = [str(y) for y in time_range if str(y) in crime_data]
    
    # Extract top N if mentioned
    top_n = extract_top_n(message)
    if top_n:
        structured["top_n"] = top_n
    
    # Check confidence level
    # Be more lenient if we have a valid year extracted
    confidence = structured.get("confidence", 0.8)
    has_valid_year = any(str(y) in crime_data for y in structured.get("years", []))
    
    if confidence < 0.5 and not has_valid_year:
        return jsonify({
            "type": "clarification",
            "summary": "I'm not quite sure what you're asking. Could you rephrase?",
            "suggestions": intelligent_handler.get_contextual_suggestions(structured, "no_data"),
            "extracted": structured
        })
    
    # Try to handle complex queries first
    complex_result = intelligent_handler.handle_complex_query(structured, message)
    if complex_result:
        return jsonify(complex_result)

    # ================= CRIME ROUTING =================
    # Check crime routing FIRST before dataset detection
    # This ensures specific crime queries are handled correctly
    crime = structured.get("crime")

    # Filter out generic terms that aren't actual crimes
    generic_terms = ["arrest", "arrests", "total", "statistics", "data", "crime", "crimes"]
    
    # If crime is detected and it's not a generic term, route to government dataset
    # This handles crimes like "Assault on Women" which contain gender words
    if crime and crime.lower() not in generic_terms:
        # Route to government dataset for crime-specific queries
        return handle_government_chat(
            structured.get("intent"),
            structured.get("years", []),
            structured
        )

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

    # ================= BASIC EXTRACTION =================
    city_list = structured.get("cities", [])
    years = structured.get("years", [])
    gender = structured.get("gender")
    intent = structured.get("intent", "")
    detected_crime = structured.get("crime", "").strip()

    raw_years = years.copy()

    years = [str(y) for y in years]
    years = [y for y in years if y in crime_data]

    if raw_years and not years:
        suggestions = intelligent_handler.get_contextual_suggestions(structured, "year_not_found")
        return jsonify({
            "type": "error",
            "summary": "Invalid year. Data available only for 2016, 2019, and 2020.",
            "suggestions": suggestions
        })

    # ================= CITY VALIDATION =================
    # Validate that extracted cities exist in the dataset
    valid_cities = []
    invalid_cities = []
    
    if city_list:
        import re
        for city in city_list:
            # Check if city exists in any year's data
            city_found = False
            for year_data in crime_data.values():
                city_escaped = re.escape(city)
                if year_data["City"].str.contains(city_escaped, case=False, na=False, regex=True).any():
                    valid_cities.append(city)
                    city_found = True
                    break
            if not city_found:
                invalid_cities.append(city)
        
        # If cities were mentioned but none are valid
        if city_list and not valid_cities:
            return jsonify({
                "type": "error",
                "summary": f"City not available in dataset: {', '.join(invalid_cities)}",
                "suggestions": [
                    "Try cities like: Delhi, Mumbai, Bangalore, Chennai, Kolkata",
                    "Check the spelling of the city name",
                    "Use major metropolitan cities only"
                ]
            })
        
        # Update city_list to only include valid cities
        city_list = valid_cities
    
    # Additional check for potential city names not extracted by LLM
    # This handles cases like "Bhopal 2019" where Bhopal isn't extracted as a city
    if not city_list and not detected_crime and not gender:
        # Check if any word in the message might be a city name
        words = message.lower().split()
        common_words = ["show", "me", "data", "statistics", "crime", "arrest", "total", "the", "in", "for", "of", "and", "or", "all", "trend"]
        
        for word in words:
            if (not word.isdigit() and 
                word not in common_words and 
                len(word) > 2):
                # Check if this word exists as a city in the dataset
                import re
                word_escaped = re.escape(word)
                city_found = False
                for year_data in crime_data.values():
                    if year_data["City"].str.contains(word_escaped, case=False, na=False, regex=True).any():
                        city_found = True
                        city_list = [word.title()]  # Add as valid city
                        break
                
                # If word looks like a city but isn't found, return error
                if not city_found and word not in ["male", "female", "juvenile", "minor"]:
                    return jsonify({
                        "type": "error",
                        "summary": f"City not available in dataset: {word.title()}",
                        "suggestions": [
                            "Try cities like: Delhi, Mumbai, Bangalore, Chennai, Kolkata",
                            "Check the spelling of the city name",
                            "Use major metropolitan cities only"
                        ]
                    })

    # ================= DEFAULT YEAR / ALL YEARS =================
    # If user mentions "all" and no specific years, use all available years
    if not years and "all" in message_lower and ("year" in message_lower or "trend" in message_lower):
        years = sorted(crime_data.keys())
    elif not years:
        latest_year = sorted(crime_data.keys())[-1]
        years = [latest_year]

    year = years[0]
    
    # Check if user is asking for year-only (to show crime suggestions)
    # This handles queries like "2020", "2019", "show me 2020 data"
    # Don't trigger if a crime was detected or if a city was found
    
    if years and not city_list and not detected_crime and not gender and len(message.split()) <= 3:
        # User likely wants to see available crimes for this year
        return handle_government_chat(
            structured.get("intent"),
            years,
            structured
        )

    # ================= GENDER DETECTION =================
    # Note: Crime queries with gender words (e.g., "Assault on Women") are already routed above
    # This section only affects non-crime queries
    gender_words = ["male", "men", "man", "female", "women", "woman"]

    if not any(word in message_lower for word in gender_words):
        gender = None
    
    # Check for gender ratio/comparison queries
    is_gender_ratio_query = any(word in message_lower for word in ["ratio", "male female", "male vs female", "gender gap", "gender breakdown", "gender comparison"])

    # ================= INTENT DETECTION =================
    # Extract top_n from structured data or message
    top_n_value = structured.get("top_n", extract_top_n(message))
    
    if top_n_value or "top" in message_lower:
        intent = "top"
        if not top_n_value:
            top_n_value = 3  # default

    elif any(word in message_lower for word in ["highest", "maximum", "most"]):
        intent = "highest"

    elif any(word in message_lower for word in ["lowest", "minimum", "least"]):
        intent = "lowest"

    if any(word in message_lower for word in ["compare", "vs", "between"]):
        intent = "compare"

    # ================= JUVENILE =================
    juvenile_keywords = ["juvenile", "minor", "child", "under 18"]

    if any(word in message_lower for word in juvenile_keywords):

        city = None

        if city_list:
            possible_city = city_list[0]

            df = crime_data[year]
            
            import re
            # Escape regex special characters
            city_escaped = re.escape(possible_city)
            if df["City"].str.contains(city_escaped, case=False, na=False, regex=True).any():
                city = possible_city

        category = "total"

        # Check for gender-specific juvenile queries
        # IMPORTANT: Check "female" before "male" because "female" contains "male"
        if "girls" in message_lower or "female" in message_lower or "women" in message_lower:
            category = "girls"
        elif "boys" in message_lower or "male" in message_lower:
            category = "boys"

        ranking = None

        if intent in ["top", "highest", "lowest"]:
            ranking = intent

        return handle_juvenile(
            year=year,
            city=city,
            category=category,
            ranking=ranking,
            top_n=3
        )

    # ================= TOP N =================
    if intent == "top":

        df = crime_data[year]

        df = df[df["City"].notna()]
        df = df[~df["City"].str.lower().str.contains("total", na=False)]

        df["value"] = df.apply(
            lambda row: calculate_city_totals(row.to_dict(), gender),
            axis=1
        )

        # Use top_n_value from intent detection
        n = top_n_value if top_n_value else 3
        df_sorted = df.sort_values(by="value", ascending=False).head(n)

        results = dict(zip(df_sorted["City"], df_sorted["value"]))
        
        # Generate insight
        total = sum(results.values())
        top_city = list(results.keys())[0]
        top_value = list(results.values())[0]
        
        insight = f"{top_city} leads with {format_number(top_value)} arrests. "
        insight += f"These top {n} cities account for {format_number(total)} total arrests in {year}."

        return jsonify({
            "type": f"top_{n}",
            "title": f"Top {n} {gender.title() + ' ' if gender else ''}Arrest Cities - {year}",
            "data": results,
            "insight": insight,
            "source": "NCRB Dataset (2016–2020)"
        })

    # ================= MATRIX COMPARISON =================
    if intent == "compare" and len(city_list) >= 2 and len(years) >= 2:

        matrix = {}
        import re

        for city in city_list:

            matrix[city] = {}

            for yr in years:

                df = crime_data[yr]
                
                # Escape regex special characters
                city_escaped = re.escape(city)
                row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]

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
        not_found_cities = []
        
        import re

        for city in city_list[:2]:
            # Escape regex special characters
            city_escaped = re.escape(city)
            row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]

            if not row.empty:
                data = row.iloc[0].to_dict()
                results[city] = calculate_city_totals(data, gender)
            else:
                not_found_cities.append(city)

        # If no cities found at all
        if not results:
            suggestions = intelligent_handler.get_contextual_suggestions(structured, "city_not_found")
            return jsonify({
                "type": "error",
                "summary": "Cities not found in the database.",
                "suggestions": suggestions
            })
        
        # If only one city found when two were requested
        if len(results) == 1 and len(city_list) >= 2:
            found_city = list(results.keys())[0]
            return jsonify({
                "type": "error",
                "summary": f"Found data for {found_city}, but could not find: {', '.join(not_found_cities)}",
                "suggestions": [
                    f"Try checking the spelling of '{not_found_cities[0]}'",
                    "Use the exact city name as it appears in the dataset",
                    f"Example: 'Compare {found_city} with Mumbai'"
                ],
                "partial_data": {found_city: results[found_city]}
            })

        # Generate detailed insight
        context = {
            "year": year,
            "gender": gender,
            "comparison_data": results
        }
        insight = intelligent_handler.generate_detailed_insight(message, results, context)

        return jsonify({
            "type": "multi_city",
            "title": f"{gender.title() if gender else 'Total'} Arrest Comparison - {year}",
            "data": results,
            "insight": insight,
            "source": "NCRB Dataset (2016–2020)"
        })

    # ================= HIGHEST / LOWEST =================
    if intent in ["highest", "lowest"]:

        df = crime_data[year]

        df = df[df["City"].notna()]
        df = df[~df["City"].str.lower().str.contains("total", na=False)]

        city_totals = {}

        for _, row in df.iterrows():
            city_name = row["City"]
            total = calculate_city_totals(row.to_dict(), gender)
            city_totals[city_name] = int(total)

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

    # ================= SINGLE CITY =================
    if len(city_list) == 1:

        city = city_list[0]
        results = {}
        
        import re

        for yr in years:

            df = crime_data[yr]
            
            # Escape regex special characters
            city_escaped = re.escape(city)
            row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]

            if not row.empty:

                data = row.iloc[0].to_dict()
                total = calculate_city_totals(data, gender)
                results[yr] = total

        if not results:
            suggestions = intelligent_handler.get_contextual_suggestions(structured, "city_not_found")
            return jsonify({
                "type": "error",
                "summary": "City not found in the database.",
                "suggestions": suggestions
            })

        # Add gender analysis if requested
        if "gender" in query_types or "analysis" in query_types:
            year = years[0] if years else list(crime_data.keys())[-1]
            gender_data = analyze_gender_gap(city, year)
            if gender_data:
                gender_insight = format_gender_analysis(gender_data, city, year)
                return jsonify({
                    "type": "gender_analysis",
                    "title": f"Gender Analysis - {city} ({year})",
                    "data": gender_data,
                    "insight": gender_insight,
                    "source": "NCRB Dataset"
                })
        
        # Add percentile rank if available
        if len(results) == 1:
            yr = list(results.keys())[0]
            percentile = get_percentile_rank(city, yr, gender)
            comparison = compare_with_average(city, yr, gender)
            
            response_data = {"Arrests": results[yr]}
            insight_parts = [f"{city} recorded {results[yr]:,} arrests in {yr}"]
            
            if percentile is not None:
                response_data["Percentile Rank"] = f"{percentile}%"
                insight_parts.append(f"ranking in the {percentile}th percentile")
            
            if comparison:
                response_data["vs National Average"] = f"{comparison['status'].title()} by {abs(comparison['percentage_difference']):.1f}%"
                insight_parts.append(
                    f"{comparison['status']} the national average of {comparison['national_average']:,} by {abs(comparison['percentage_difference']):.1f}%"
                )

            return jsonify({
                "type": "city",
                "title": f"{gender.title() if gender else 'Total'} Arrests - {city} ({yr})",
                "data": response_data,
                "insight": ", ".join(insight_parts) + ".",
                "source": "NCRB Dataset (2016–2020)"
            })

        return jsonify({
            "type": "city_multi_year",
            "title": f"{gender.title() if gender else 'Total'} Arrest Comparison - {city}",
            "data": results,
            "source": "NCRB Dataset (2016–2020)"
        })

    # ================= GENDER RATIO / COMPARISON =================
    if is_gender_ratio_query and not city_list:
        # National gender ratio
        df = crime_data[year]
        
        # Filter out "Total" rows to avoid double counting
        df = df[df["City"].notna()]
        df = df[~df["City"].str.lower().str.contains("total", na=False)]
        
        male_total = sum(
            calculate_city_totals(row.to_dict(), "male")
            for _, row in df.iterrows()
        )
        
        female_total = sum(
            calculate_city_totals(row.to_dict(), "female")
            for _, row in df.iterrows()
        )
        
        total = male_total + female_total
        male_pct = (male_total / total * 100) if total > 0 else 0
        female_pct = (female_total / total * 100) if total > 0 else 0
        ratio = male_total / female_total if female_total > 0 else 0
        
        gender_data = {
            "Male Arrests": int(male_total),
            "Female Arrests": int(female_total),
            "Male Percentage": f"{male_pct:.1f}%",
            "Female Percentage": f"{female_pct:.1f}%",
            "Male-to-Female Ratio": f"{ratio:.2f}:1"
        }
        
        insight = f"In {year}, male arrests were {format_number(male_total)} ({male_pct:.1f}%) "
        insight += f"and female arrests were {format_number(female_total)} ({female_pct:.1f}%). "
        insight += f"The male-to-female ratio is {ratio:.2f}:1."
        
        return jsonify({
            "type": "gender_ratio",
            "title": f"National Gender Arrest Ratio - {year}",
            "data": gender_data,
            "insight": insight,
            "source": "NCRB Dataset (2016–2020)"
        })

    # ================= MULTI-YEAR TREND =================
    # Handle both general and gender-specific multi-year trends
    # Check for "all years" or "trend" queries without specific cities
    is_multi_year_trend = (
        not city_list and 
        ("trend" in message_lower and "all" in message_lower) or
        ("arrest trend all years" in message_lower) or
        ("male arrest trend all years" in message_lower) or
        ("female arrest trend all years" in message_lower) or
        (len(years) > 1 and "trend" in message_lower)
    )
    
    if is_multi_year_trend:
        # Use all available years if not specified
        if not years or len(years) == 1:
            years = sorted(crime_data.keys())
        
        results = {}
        for yr in years:
            df = crime_data[yr]
            
            # Filter out "Total" rows to avoid double counting
            df = df[df["City"].notna()]
            df = df[~df["City"].str.lower().str.contains("total", na=False)]
            
            total = sum(
                calculate_city_totals(row.to_dict(), gender)
                for _, row in df.iterrows()
            )
            results[yr] = total
        
        # Generate insight
        sorted_years = sorted(results.keys())
        first_year = sorted_years[0]
        last_year = sorted_years[-1]
        first_value = results[first_year]
        last_value = results[last_year]
        change = last_value - first_value
        change_pct = (change / first_value * 100) if first_value > 0 else 0
        
        gender_label = f"{gender.title()} " if gender else ""
        
        insight = f"{gender_label}Arrest trend from {first_year} to {last_year}: "
        if change > 0:
            insight += f"increased by {format_number(abs(change))} ({abs(change_pct):.1f}%), "
        elif change < 0:
            insight += f"decreased by {format_number(abs(change))} ({abs(change_pct):.1f}%), "
        else:
            insight += "remained stable, "
        insight += f"from {format_number(first_value)} to {format_number(last_value)}."
        
        return jsonify({
            "type": "multi_year_trend",
            "title": f"{gender_label}Arrest Trend Across Years ({first_year}-{last_year})",
            "data": results,
            "insight": insight,
            "source": "NCRB Dataset (2016–2020)"
        })

    # ================= GENDER TOTAL =================
    if not city_list and gender and len(years) == 1:

        df = crime_data[year]
        
        # Filter out "Total" rows to avoid double counting
        df = df[df["City"].notna()]
        df = df[~df["City"].str.lower().str.contains("total", na=False)]

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

    # ================= YEAR TOTAL =================
    if not city_list and not gender and years and "arrest" in message_lower:

        df = crime_data[year]
        
        # Filter out "Total" rows to avoid double counting
        df = df[df["City"].notna()]
        df = df[~df["City"].str.lower().str.contains("total", na=False)]

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
    suggestions = intelligent_handler.get_contextual_suggestions(structured, "general")
    
    return jsonify({
        "type": "fallback",
        "summary": "I couldn't fully understand your query. Here are some suggestions:",
        "suggestions": suggestions,
        "extracted_info": {
            "cities": structured.get("cities", []),
            "years": structured.get("years", []),
            "intent": structured.get("intent", "unknown")
        },
        "help": "Try being more specific about the city, year, or type of information you need."
    })