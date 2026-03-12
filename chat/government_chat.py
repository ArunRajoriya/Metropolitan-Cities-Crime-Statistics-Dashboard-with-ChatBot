from flask import jsonify
from services.data_loader import gov_data
from services.insight_generator import generate_insight
import pandas as pd


def get_crime_suggestions(year):
    """Get all crime suggestions for a given year"""
    if year not in gov_data:
        return []
    
    df = gov_data[year].copy()
    df.columns = df.columns.str.strip()
    
    # Get all unique crimes
    all_crimes = df["Crime Head"].dropna().unique().tolist()
    
    # Return all crimes sorted alphabetically for all years
    return sorted(all_crimes)


def handle_government_chat(intent, years, structured):

    year = str(years[0]) if years else list(gov_data.keys())[-1]

    if year not in gov_data:
        return jsonify({"type": "error", "summary": "Year not available"})

    crime_name = structured.get("crime", "").strip().lower()

    # If no crime specified, show suggestions
    if not crime_name:
        suggestions = get_crime_suggestions(year)
        
        if suggestions:
            # Check if this is 2016 (broad categories) or 2019/2020 (detailed crimes)
            df = gov_data[year].copy()
            df.columns = df.columns.str.strip()
            unique_crimes = len(df['Crime Head'].unique())
            
            if unique_crimes < 50:
                # 2016 - broad categories
                title = f"Available Crime Categories for {year}"
                summary = f"Select a crime category to view statistics for {year} ({unique_crimes} broad categories):"
            else:
                # 2019/2020 - detailed crimes
                title = f"Available Crime Statistics for {year}"
                summary = f"Select a crime type to view detailed statistics for {year} ({unique_crimes} crimes available):"
            
            return jsonify({
                "type": "crime_suggestions",
                "title": title,
                "summary": summary,
                "data": suggestions,  # Show ALL crimes for all years
                "year": year,
                "source": "Government Dataset"
            })
        else:
            return jsonify({
                "type": "error", 
                "summary": f"Crime data not available for {year}."
            })

    df = gov_data[year].copy()
    df.columns = df.columns.str.strip()
    
    # Try multiple matching strategies
    crime_row = pd.DataFrame()
    
    # Strategy 1: Exact match
    crime_row = df[df["Crime Head"].str.lower() == crime_name]
    
    # Strategy 2: Partial match (contains)
    if crime_row.empty:
        crime_row = df[df["Crime Head"].str.lower().str.contains(crime_name, na=False, regex=False)]
    
    # Strategy 3: Reverse partial match (crime_name contains Crime Head)
    if crime_row.empty:
        for idx, row in df.iterrows():
            crime_head = str(row["Crime Head"]).lower()
            if crime_head in crime_name or crime_name in crime_head:
                crime_row = df[df.index == idx]
                break
    
    # Strategy 4: Fuzzy match with high threshold
    if crime_row.empty:
        from difflib import get_close_matches
        all_crimes_lower = df["Crime Head"].str.lower().tolist()
        matches = get_close_matches(crime_name, all_crimes_lower, n=1, cutoff=0.6)
        if matches:
            crime_row = df[df["Crime Head"].str.lower() == matches[0]]
    
    if crime_row.empty:
        # Suggest similar crimes
        all_crimes = df["Crime Head"].str.lower().tolist()
        from difflib import get_close_matches
        suggestions = get_close_matches(crime_name, all_crimes, n=3, cutoff=0.4)
        
        return jsonify({
            "type": "error",
            "summary": f"Crime '{crime_name}' not found in government dataset for {year}",
            "suggestions": [f"Did you mean: {', '.join(suggestions)}?"] if suggestions else [
                f"Try: 'murder {year}'",
                f"Try: 'theft {year}'",
                f"Try: 'rape {year}'"
            ]
        })

    # Get the first matching row
    data = crime_row.fillna(0).to_dict(orient="records")[0]
    actual_crime_name = data.get("Crime Head", crime_name)
    
    # Extract key statistics
    key_stats = {}
    for key, value in data.items():
        if key != "Crime Head" and value != 0:
            # Convert to int if numeric
            try:
                key_stats[key] = int(value) if isinstance(value, (int, float)) else value
            except:
                key_stats[key] = value
    
    # Generate insight
    insight_text = generate_insight(
        f"What are the statistics for {actual_crime_name} in {year}?",
        key_stats
    )
    
    # If LLM insight fails, generate a basic insight
    if "unavailable" in insight_text.lower():
        # Create a basic insight from the data
        cases_reported = key_stats.get("Cases Reported during the year", 0)
        chargesheeting_rate = key_stats.get("Charge-Sheeting Rate", 0)
        
        if cases_reported and chargesheeting_rate:
            insight_text = f"In {year}, {cases_reported:,} cases of {actual_crime_name} were reported with a charge-sheeting rate of {chargesheeting_rate}%."
        elif cases_reported:
            insight_text = f"In {year}, {cases_reported:,} cases of {actual_crime_name} were reported across India."
        else:
            insight_text = f"Detailed statistics for {actual_crime_name} in {year} are available in the data."

    return jsonify({
        "type": "government",
        "title": f"{actual_crime_name} - {year}",
        "data": key_stats,
        "insight": insight_text,
        "source": "Government Dataset"
    })