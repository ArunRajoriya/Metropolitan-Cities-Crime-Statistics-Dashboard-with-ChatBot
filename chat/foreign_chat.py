from flask import jsonify
from services.data_loader import foreign_data
from services.response_formatter import format_number

def handle_foreign_chat(intent, years, structured):
    """Enhanced foreign crime chat handler with comprehensive data analysis"""
    
    # Default to latest year if no year specified
    year = str(years[0]) if years else "2020"
    
    if year not in foreign_data:
        available_years = list(foreign_data.keys())
        return jsonify({
            "type": "error", 
            "summary": f"Foreign crime data not available for {year}. Available years: {', '.join(available_years)}",
            "suggestions": [
                f"Try 'Foreign crime {available_years[-1]}'",
                "Ask 'Foreign crime all years' for trend analysis",
                "Query 'Foreign tourists vs other foreigners 2020'"
            ]
        })

    df = foreign_data[year].copy()
    
    # Check if user wants specific crime type
    crime_query = structured.get("crime", "").lower()
    
    # Check if user wants comparison between tourist vs other foreigners
    is_comparison_query = any(word in structured.get("intent", "").lower() for word in ["compare", "vs", "versus", "breakdown"])
    
    # Check if user wants trend analysis across years
    is_trend_query = len(years) > 1 or "trend" in structured.get("intent", "").lower()
    
    # Handle trend analysis across multiple years
    if is_trend_query and len(years) > 1:
        return handle_foreign_trend_analysis(years, structured)
    
    # Handle all years trend
    if "all" in str(structured.get("years", [])).lower() or "trend" in structured.get("intent", "").lower():
        return handle_foreign_trend_analysis(list(foreign_data.keys()), structured)
    
    # Handle specific crime queries
    if crime_query and crime_query not in ["foreign", "foreigner", "crime", "data"]:
        return handle_specific_foreign_crime(year, crime_query, structured)
    
    # Handle tourist vs other foreigners comparison
    if is_comparison_query or "tourist" in structured.get("intent", "").lower():
        return handle_foreign_victim_comparison(year, structured)
    
    # Default comprehensive summary
    return handle_foreign_summary(year, structured)


def handle_foreign_summary(year, structured):
    """Provide comprehensive foreign crime summary"""
    df = foreign_data[year].copy()
    
    # Filter out total/summary rows that are not actual crimes
    total_keywords = ["total", "total (a)", "total (b)", "total (a+b)"]
    df = df[~df["Crime Head"].str.lower().isin(total_keywords)]
    
    # Calculate totals from actual crime data
    total_crimes = df["Cases of Crimes Committed against - Total Foreigners"].sum()
    tourist_crimes = df["Cases of Crimes Committed against - Foreign Tourists"].sum()
    other_crimes = df["Cases of Crimes Committed against - Other Foreigners"].sum() if "Cases of Crimes Committed against - Other Foreigners" in df.columns else df["Cases of Crimes Committed against - Other  Foreigners"].sum()
    
    # Find top crimes (excluding totals)
    top_crimes = df.nlargest(3, "Cases of Crimes Committed against - Total Foreigners")[["Crime Head", "Cases of Crimes Committed against - Total Foreigners"]]
    
    # Calculate percentages
    tourist_pct = (tourist_crimes / total_crimes * 100) if total_crimes > 0 else 0
    other_pct = (other_crimes / total_crimes * 100) if total_crimes > 0 else 0
    
    response_data = {
        "Total Foreign Crime Cases": int(total_crimes),
        "Against Foreign Tourists": int(tourist_crimes),
        "Against Other Foreigners": int(other_crimes),
        "Tourist Crime Percentage": f"{tourist_pct:.1f}%",
        "Other Foreigner Percentage": f"{other_pct:.1f}%",
        "Most Common Crime": top_crimes.iloc[0]["Crime Head"] if not top_crimes.empty else "N/A",
        "Top Crime Cases": int(top_crimes.iloc[0]["Cases of Crimes Committed against - Total Foreigners"]) if not top_crimes.empty else 0
    }
    
    # Generate insight
    insight = f"In {year}, {format_number(total_crimes)} crimes were committed against foreigners in India. "
    insight += f"Foreign tourists faced {format_number(tourist_crimes)} cases ({tourist_pct:.1f}%), "
    insight += f"while other foreigners faced {format_number(other_crimes)} cases ({other_pct:.1f}%). "
    if not top_crimes.empty:
        insight += f"The most common crime was {top_crimes.iloc[0]['Crime Head']} with {format_number(top_crimes.iloc[0]['Cases of Crimes Committed against - Total Foreigners'])} cases."
    
    return jsonify({
        "type": "foreign_summary",
        "title": f"Foreign Crime Analysis - {year}",
        "data": response_data,
        "insight": insight,
        "source": "NCRB Foreign Crime Dataset"
    })


def handle_foreign_victim_comparison(year, structured):
    """Compare crimes against tourists vs other foreigners"""
    df = foreign_data[year].copy()
    
    # Filter out total/summary rows that are not actual crimes
    total_keywords = ["total", "total (a)", "total (b)", "total (a+b)"]
    df = df[~df["Crime Head"].str.lower().isin(total_keywords)]
    
    tourist_col = "Cases of Crimes Committed against - Foreign Tourists"
    other_col = "Cases of Crimes Committed against - Other Foreigners" if "Cases of Crimes Committed against - Other Foreigners" in df.columns else "Cases of Crimes Committed against - Other  Foreigners"
    
    tourist_total = df[tourist_col].sum()
    other_total = df[other_col].sum()
    total = tourist_total + other_total
    
    # Top crimes for each category (excluding totals)
    tourist_top = df.nlargest(3, tourist_col)[["Crime Head", tourist_col]]
    other_top = df.nlargest(3, other_col)[["Crime Head", other_col]]
    
    response_data = {
        "Foreign Tourists": {
            "Total Cases": int(tourist_total),
            "Percentage": f"{(tourist_total/total*100):.1f}%" if total > 0 else "0%",
            "Top Crime": tourist_top.iloc[0]["Crime Head"] if not tourist_top.empty else "N/A",
            "Top Crime Cases": int(tourist_top.iloc[0][tourist_col]) if not tourist_top.empty else 0
        },
        "Other Foreigners": {
            "Total Cases": int(other_total),
            "Percentage": f"{(other_total/total*100):.1f}%" if total > 0 else "0%",
            "Top Crime": other_top.iloc[0]["Crime Head"] if not other_top.empty else "N/A",
            "Top Crime Cases": int(other_top.iloc[0][other_col]) if not other_top.empty else 0
        }
    }
    
    # Generate insight
    if tourist_total > other_total:
        leader = "Foreign tourists"
        leader_count = tourist_total
        follower = "other foreigners"
        follower_count = other_total
    else:
        leader = "Other foreigners"
        leader_count = other_total
        follower = "foreign tourists"
        follower_count = tourist_total
    
    diff = abs(tourist_total - other_total)
    diff_pct = (diff / min(tourist_total, other_total) * 100) if min(tourist_total, other_total) > 0 else 0
    
    insight = f"In {year}, {leader.lower()} faced more crimes ({format_number(leader_count)} cases) "
    insight += f"compared to {follower} ({format_number(follower_count)} cases), "
    insight += f"a difference of {format_number(diff)} cases ({diff_pct:.1f}% more). "
    
    return jsonify({
        "type": "foreign_comparison",
        "title": f"Foreign Victim Comparison - {year}",
        "data": response_data,
        "insight": insight,
        "source": "NCRB Foreign Crime Dataset"
    })


def handle_specific_foreign_crime(year, crime_query, structured):
    """Handle queries about specific crimes against foreigners"""
    df = foreign_data[year].copy()
    
    # Find matching crime
    matching_crimes = df[df["Crime Head"].str.contains(crime_query, case=False, na=False)]
    
    if matching_crimes.empty:
        available_crimes = df["Crime Head"].tolist()[:10]  # Show first 10 crimes
        return jsonify({
            "type": "error",
            "summary": f"Crime '{crime_query}' not found in foreign crime data for {year}",
            "suggestions": [
                f"Try: {crime} {year}" for crime in available_crimes[:3]
            ] + [f"Available crimes include: {', '.join(available_crimes[:5])}..."]
        })
    
    crime_data = matching_crimes.iloc[0]
    crime_name = crime_data["Crime Head"]
    
    tourist_col = "Cases of Crimes Committed against - Foreign Tourists"
    other_col = "Cases of Crimes Committed against - Other Foreigners" if "Cases of Crimes Committed against - Other Foreigners" in df.columns else "Cases of Crimes Committed against - Other  Foreigners"
    total_col = "Cases of Crimes Committed against - Total Foreigners"
    
    tourist_cases = int(crime_data[tourist_col])
    other_cases = int(crime_data[other_col])
    total_cases = int(crime_data[total_col])
    
    response_data = {
        "Crime Type": crime_name,
        "Total Cases": total_cases,
        "Foreign Tourist Cases": tourist_cases,
        "Other Foreigner Cases": other_cases,
        "Tourist Percentage": f"{(tourist_cases/total_cases*100):.1f}%" if total_cases > 0 else "0%",
        "Other Percentage": f"{(other_cases/total_cases*100):.1f}%" if total_cases > 0 else "0%"
    }
    
    # Generate insight
    insight = f"In {year}, {format_number(total_cases)} cases of {crime_name.lower()} were reported against foreigners. "
    if tourist_cases > other_cases:
        insight += f"Foreign tourists were more affected ({format_number(tourist_cases)} cases) than other foreigners ({format_number(other_cases)} cases)."
    elif other_cases > tourist_cases:
        insight += f"Other foreigners were more affected ({format_number(other_cases)} cases) than foreign tourists ({format_number(tourist_cases)} cases)."
    else:
        insight += f"Both foreign tourists and other foreigners were equally affected ({format_number(tourist_cases)} cases each)."
    
    return jsonify({
        "type": "foreign_crime_specific",
        "title": f"{crime_name} Against Foreigners - {year}",
        "data": response_data,
        "insight": insight,
        "source": "NCRB Foreign Crime Dataset"
    })


def handle_foreign_trend_analysis(years, structured):
    """Analyze foreign crime trends across multiple years"""
    trend_data = {}
    tourist_trend = {}
    other_trend = {}
    
    for year in years:
        if year in foreign_data:
            df = foreign_data[year].copy()
            
            # Filter out total/summary rows that are not actual crimes
            total_keywords = ["total", "total (a)", "total (b)", "total (a+b)"]
            df = df[~df["Crime Head"].str.lower().isin(total_keywords)]
            
            tourist_col = "Cases of Crimes Committed against - Foreign Tourists"
            other_col = "Cases of Crimes Committed against - Other Foreigners" if "Cases of Crimes Committed against - Other Foreigners" in df.columns else "Cases of Crimes Committed against - Other  Foreigners"
            total_col = "Cases of Crimes Committed against - Total Foreigners"
            
            total = df[total_col].sum()
            tourist = df[tourist_col].sum()
            other = df[other_col].sum()
            
            trend_data[year] = int(total)
            tourist_trend[year] = int(tourist)
            other_trend[year] = int(other)
    
    if len(trend_data) < 2:
        return jsonify({
            "type": "error",
            "summary": "Need at least 2 years of data for trend analysis",
            "suggestions": [
                "Try 'Foreign crime 2019 vs 2020'",
                "Ask 'Foreign crime trend all years'"
            ]
        })
    
    # Calculate trend
    sorted_years = sorted(trend_data.keys())
    first_year = sorted_years[0]
    last_year = sorted_years[-1]
    
    first_total = trend_data[first_year]
    last_total = trend_data[last_year]
    change = last_total - first_total
    change_pct = (change / first_total * 100) if first_total > 0 else 0
    
    response_data = {
        "Total Trend": trend_data,
        "Tourist Trend": tourist_trend,
        "Other Foreigner Trend": other_trend,
        "Overall Change": f"{change:+d} cases",
        "Percentage Change": f"{change_pct:+.1f}%",
        "Trend Direction": "Increasing" if change > 0 else "Decreasing" if change < 0 else "Stable"
    }
    
    # Generate insight
    direction = "increased" if change > 0 else "decreased" if change < 0 else "remained stable"
    insight = f"Foreign crime cases {direction} from {format_number(first_total)} in {first_year} "
    insight += f"to {format_number(last_total)} in {last_year}, "
    if change != 0:
        insight += f"a change of {format_number(abs(change))} cases ({abs(change_pct):.1f}%). "
    else:
        insight += "showing no change. "
    
    # Add tourist vs other trend
    tourist_change = tourist_trend[last_year] - tourist_trend[first_year]
    other_change = other_trend[last_year] - other_trend[first_year]
    
    if abs(tourist_change) > abs(other_change):
        insight += f"Tourist-related crimes showed a larger change ({tourist_change:+d} cases) than other foreigner crimes ({other_change:+d} cases)."
    else:
        insight += f"Other foreigner crimes showed a larger change ({other_change:+d} cases) than tourist-related crimes ({tourist_change:+d} cases)."
    
    return jsonify({
        "type": "foreign_trend",
        "title": f"Foreign Crime Trend Analysis ({first_year}-{last_year})",
        "data": response_data,
        "insight": insight,
        "source": "NCRB Foreign Crime Dataset"
    })