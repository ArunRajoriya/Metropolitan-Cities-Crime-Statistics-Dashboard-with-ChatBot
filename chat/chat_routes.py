from flask import Blueprint, request, jsonify
import time
from services.data_loader import crime_data
from services.dataset_router import detect_dataset
from services.analytics_engine import calculate_city_totals
from services.insight_generator import generate_insight
from services.llm_extractor import llm_extract
from chat.government_chat import handle_government_chat
from chat.foreign_chat import handle_foreign_chat
from chat.advanced_features import handle_juvenile
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
from services.advanced_query_processor import advanced_processor

# Add caching enhancement
from services.cache_manager import chatbot_cache

chat_bp = Blueprint("chatbot", __name__)

def create_cached_response(response_data, cache_key_data, start_time):
    """Helper function to add timing and caching to responses"""
    response_data['response_time'] = f"{time.time() - start_time:.2f}s"
    
    # Cache successful responses (not errors or greetings)
    if response_data.get('type') not in ['error', 'fallback', 'clarification', 'greeting']:
        chatbot_cache.set(cache_key_data, response_data)
    
    return jsonify(response_data)

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
    start_time = time.time()
    message = request.json.get("message", "").strip()
    message_lower = message.lower()
    
    # Handle greetings
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
            "example": "Try asking: 'Compare Delhi and Mumbai arrests in 2020' or 'Show me the trend for Bangalore from 2016 to 2020'",
            "response_time": f"{time.time() - start_time:.2f}s"
        })

    structured = llm_extract(message) or {}
    
    # Check cache first for performance boost
    cache_key_data = {
        'cities': structured.get('cities', []),
        'years': structured.get('years', []),
        'gender': structured.get('gender'),
        'intent': structured.get('intent'),
        'crime': structured.get('crime')
    }
    
    cached_response = chatbot_cache.get(cache_key_data)
    if cached_response:
        cached_response['cached'] = True
        cached_response['response_time'] = f"{time.time() - start_time:.2f}s"
        return jsonify(cached_response)
    
    # Early year validation - check if user mentioned years that don't exist
    extracted_years = structured.get("years", [])
    if extracted_years:
        invalid_years = [str(y) for y in extracted_years if str(y) not in crime_data]
        if invalid_years:
            return jsonify({
                "type": "error",
                "summary": f"Data not available for {', '.join(invalid_years)}. Available years: 2016, 2019, 2020.",
                "suggestions": [
                    f"Try using 2020 instead: '{message.replace(invalid_years[0], '2020')}'",
                    "Ask 'What years are available?'",
                    "Use available years: 2016, 2019, or 2020"
                ]
            })
    
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
        # Get city counts for each year
        city_counts = {}
        for year, df in crime_data.items():
            df_clean = df[df["City"].notna()]
            df_clean = df_clean[~df_clean["City"].str.lower().str.contains("total", na=False)]
            city_counts[year] = len(df_clean)
        
        return jsonify({
            "type": "info",
            "title": "Data Availability",
            "data": {
                "Available Years": "2016, 2019, 2020",
                "Cities by Year": {f"{year}": f"{count} cities" for year, count in city_counts.items()},
                "Total Unique Cities": len(intelligent_handler.all_cities),
                "Datasets": "Crime Data, Government Data, Foreign Crime Data",
                "Features": "City comparisons, trends, rankings, gender analysis, juvenile statistics"
            },
            "summary": f"I have crime data across {len(city_counts)} years with varying city coverage: " + 
                      ", ".join([f"{year} ({count} cities)" for year, count in city_counts.items()]) + ".",
            "note": "City coverage varies by year. 2020 has 19 cities, which is the most comprehensive dataset."
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
        
        # Validate if requested top_n is reasonable
        if top_n > 50:
            return jsonify({
                "type": "clarification",
                "summary": f"Requesting top {top_n} cities is too many. I can show up to 20 cities maximum.",
                "suggestions": [
                    "Try 'top 10 cities' for a good overview",
                    "Ask for 'top 20 cities' for comprehensive ranking",
                    "Use 'top 5 cities' for quick insights"
                ]
            })
    
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
    
    # Try advanced query processing for sophisticated analytics
    advanced_result = advanced_processor.process_advanced_query(message, structured)
    if advanced_result:
        return jsonify(advanced_result)

    # ================= CRIME ROUTING =================
    # Check crime routing FIRST before dataset detection
    # This ensures specific crime queries are handled correctly
    crime = structured.get("crime")

    # Filter out generic terms that aren't actual crimes
    generic_terms = ["arrest", "arrests", "total", "statistics", "data", "crime", "crimes"]
    
    # If crime is detected and it's not a generic term, route to government dataset
    # BUT check for foreign keywords first - foreign crime queries should go to foreign dataset
    if crime and crime.lower() not in generic_terms:
        # Check if this is a foreign crime query
        message_lower = message.lower()
        if "foreign" in message_lower or "foreigner" in message_lower or "tourist" in message_lower:
            # Route to foreign dataset for foreign crime queries
            return handle_foreign_chat(
                structured.get("intent"),
                structured.get("years", []),
                structured
            )
        else:
            # Route to government dataset for regular crime-specific queries
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
    original_years = years.copy()  # Keep track of original years before filtering
    years = [y for y in years if y in crime_data]

    # ================= DEFAULT YEAR / ALL YEARS =================
    # If user mentions "all" and no specific years, use all available years
    if not years and "all" in message_lower and ("year" in message_lower or "trend" in message_lower):
        years = sorted(crime_data.keys())
    elif not years and not original_years:
        # No years mentioned at all - use default
        latest_year = sorted(crime_data.keys())[-1]
        years = [latest_year]
    elif not years and original_years:
        # Years were mentioned but none are valid - show error
        invalid_years = [y for y in original_years if y not in crime_data]
        return jsonify({
            "type": "error",
            "summary": f"Data not available for {', '.join(invalid_years)}. Available years: 2016, 2019, 2020.",
            "suggestions": [
                f"Try 'Compare Delhi and Mumbai arrests in 2020'",
                f"Ask 'Delhi arrests 2019'",
                f"Use available years: 2016, 2019, or 2020"
            ]
        })

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
        requested_n = top_n_value if top_n_value else 3
        available_cities = len(df)
        actual_n = min(requested_n, available_cities)
        
        df_sorted = df.sort_values(by="value", ascending=False).head(actual_n)

        results = dict(zip(df_sorted["City"], df_sorted["value"]))
        
        # Generate insight with accurate numbers
        total = sum(results.values())
        top_city = list(results.keys())[0]
        top_value = list(results.values())[0]
        
        insight = f"{top_city} leads with {format_number(top_value)} arrests. "
        
        # Adjust insight based on requested vs actual
        if requested_n > available_cities:
            insight += f"Showing all {actual_n} available cities (requested top {requested_n}). "
        
        insight += f"These top {actual_n} cities account for {format_number(total)} total arrests in {year}."

        # Create appropriate title
        if requested_n > available_cities:
            title = f"Top {actual_n} {gender.title() + ' ' if gender else ''}Arrest Cities - {year} (All Available)"
        else:
            title = f"Top {actual_n} {gender.title() + ' ' if gender else ''}Arrest Cities - {year}"

        return jsonify({
            "type": f"top_{actual_n}",
            "title": title,
            "data": results,
            "insight": insight,
            "note": f"Showing {actual_n} of {requested_n} requested cities" if requested_n > available_cities else None,
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

        if not city_totals:
            return jsonify({
                "type": "error",
                "summary": f"No city data available for {year}",
                "suggestions": ["Try a different year (2016, 2019, 2020)", "Ask for available data"]
            })

        sorted_data = sorted(
            city_totals.items(),
            key=lambda x: x[1],
            reverse=(intent == "highest")
        )

        top_city, top_value = sorted_data[0]
        
        # Add context about total cities
        total_cities = len(city_totals)
        insight = f"{top_city} has the {intent} arrests with {format_number(top_value)} cases in {year}. "
        insight += f"This is among {total_cities} cities in the dataset."

        return jsonify({
            "type": intent,
            "title": f"{intent.capitalize()} {gender.title() + ' ' if gender else ''}Arrest City - {year}",
            "data": {top_city: top_value},
            "insight": insight,
            "context": f"Analyzed {total_cities} cities",
            "source": "NCRB Dataset (2016–2020)"
        })

    # ================= CITY-SPECIFIC TREND =================
    # Handle city-specific trend queries with smart defaults
    if len(city_list) == 1 and "trend" in message_lower:
        city = city_list[0]
        
        # Use all available years if no years specified or only one year
        if not years or len(years) == 1:
            years = sorted(crime_data.keys())
        
        results = {}
        import re
        
        for yr in years:
            df = crime_data[yr]
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
        
        # Generate trend insight
        if len(results) >= 2:
            sorted_years = sorted(results.keys())
            first_year = sorted_years[0]
            last_year = sorted_years[-1]
            first_value = results[first_year]
            last_value = results[last_year]
            change = last_value - first_value
            change_pct = (change / first_value * 100) if first_value > 0 else 0
            
            gender_label = f"{gender.title()} " if gender else ""
            
            insight = f"{city} {gender_label.lower()}arrest trend from {first_year} to {last_year}: "
            if change > 0:
                insight += f"increased by {format_number(abs(change))} ({abs(change_pct):.1f}%), "
            elif change < 0:
                insight += f"decreased by {format_number(abs(change))} ({abs(change_pct):.1f}%), "
            else:
                insight += "remained stable, "
            insight += f"from {format_number(first_value)} to {format_number(last_value)}."
            
            return jsonify({
                "type": "city_trend",
                "title": f"{city} {gender_label}Arrest Trend ({first_year}-{last_year})",
                "data": results,
                "insight": insight,
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
    # Enhanced to handle generic trend queries with smart defaults
    is_multi_year_trend = (
        ("trend" in message_lower and not city_list) or
        ("trend analysis" in message_lower) or
        ("show me trend" in message_lower) or
        ("arrest trend" in message_lower and not city_list) or
        ("male arrest trend" in message_lower and not city_list) or
        ("female arrest trend" in message_lower and not city_list) or
        (len(years) > 1 and "trend" in message_lower and not city_list)
    )
    
    if is_multi_year_trend:
        # Smart defaults for generic trend queries
        if not years or len(years) == 1:
            years = sorted(crime_data.keys())  # Use all available years
        
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
        
        insight = f"National {gender_label.lower()}arrest trend from {first_year} to {last_year}: "
        if change > 0:
            insight += f"increased by {format_number(abs(change))} ({abs(change_pct):.1f}%), "
        elif change < 0:
            insight += f"decreased by {format_number(abs(change))} ({abs(change_pct):.1f}%), "
        else:
            insight += "remained stable, "
        insight += f"from {format_number(first_value)} to {format_number(last_value)}."
        
        return jsonify({
            "type": "multi_year_trend",
            "title": f"National {gender_label}Arrest Trend ({first_year}-{last_year})",
            "data": results,
            "insight": insight,
            "source": "NCRB Dataset (2016–2020)"
        })

    # ================= TOP CITIES TREND (Smart Default) =================
    # Handle generic trend queries by showing top cities trend
    if "trend" in message_lower and not city_list and not is_multi_year_trend:
        # Show trend for top 5 cities across all years
        all_years = sorted(crime_data.keys())
        
        # First, find top 5 cities in the latest year
        latest_year = all_years[-1]
        df_latest = crime_data[latest_year]
        df_latest = df_latest[df_latest["City"].notna()]
        df_latest = df_latest[~df_latest["City"].str.lower().str.contains("total", na=False)]
        
        city_totals = {}
        for _, row in df_latest.iterrows():
            city_name = row["City"]
            total = calculate_city_totals(row.to_dict(), gender)
            city_totals[city_name] = int(total)
        
        # Get top 5 cities
        top_cities = sorted(city_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        top_city_names = [city for city, _ in top_cities]
        
        # Get trend data for these top cities
        trend_data = {}
        for city in top_city_names:
            city_data = {}
            import re
            for yr in all_years:
                df = crime_data[yr]
                city_escaped = re.escape(city)
                row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]
                if not row.empty:
                    total = calculate_city_totals(row.iloc[0].to_dict(), gender)
                    city_data[yr] = int(total)
            
            if city_data:
                trend_data[city] = city_data
        
        if trend_data:
            # Generate insight for top cities trend
            insight_parts = []
            for city, data in list(trend_data.items())[:3]:  # Top 3 for insight
                years_sorted = sorted(data.keys())
                if len(years_sorted) >= 2:
                    first_val = data[years_sorted[0]]
                    last_val = data[years_sorted[-1]]
                    change_pct = ((last_val - first_val) / first_val * 100) if first_val > 0 else 0
                    
                    if abs(change_pct) > 5:  # Only mention significant changes
                        direction = "increased" if change_pct > 0 else "decreased"
                        insight_parts.append(f"{city} {direction} by {abs(change_pct):.1f}%")
            
            insight = f"Top cities trend analysis shows "
            if insight_parts:
                insight += ", ".join(insight_parts) + f" from {all_years[0]} to {all_years[-1]}."
            else:
                insight += f"relatively stable patterns across top cities from {all_years[0]} to {all_years[-1]}."
            
            return jsonify({
                "type": "top_cities_trend",
                "title": f"Top 5 Cities {gender.title() + ' ' if gender else ''}Arrest Trend",
                "data": trend_data,
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
    
    response = {
        "type": "fallback",
        "summary": "I couldn't fully understand your query. Here are some suggestions:",
        "suggestions": suggestions,
        "extracted_info": {
            "cities": structured.get("cities", []),
            "years": structured.get("years", []),
            "intent": structured.get("intent", "unknown")
        },
        "help": "Try being more specific about the city, year, or type of information you need.",
        "response_time": f"{time.time() - start_time:.2f}s"
    }
    
    # Cache successful responses (not errors or greetings)
    if response.get('type') not in ['error', 'fallback', 'clarification', 'greeting']:
        chatbot_cache.set(cache_key_data, response)
    
    return jsonify(response)