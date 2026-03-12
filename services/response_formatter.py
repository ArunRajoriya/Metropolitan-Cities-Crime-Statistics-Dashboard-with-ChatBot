"""
Response Formatter - Generate natural language responses
"""


def format_number(num):
    """Format number with commas"""
    return f"{int(num):,}"


def format_comparison_response(data, context):
    """Format multi-city comparison response"""
    cities = list(data.keys())
    
    if len(cities) == 2:
        city1, city2 = cities
        val1, val2 = data[city1], data[city2]
        
        if val1 > val2:
            leader = city1
            follower = city2
            diff = val1 - val2
            pct = (diff / val2 * 100) if val2 > 0 else 0
        else:
            leader = city2
            follower = city1
            diff = val2 - val1
            pct = (diff / val1 * 100) if val1 > 0 else 0
        
        response = f"{leader} recorded {format_number(data[leader])} arrests, "
        response += f"which is {format_number(diff)} ({pct:.1f}%) more than {follower}'s {format_number(data[follower])} arrests"
        
        if context.get("year"):
            response += f" in {context['year']}"
        
        return response + "."
    
    # Multiple cities
    sorted_cities = sorted(data.items(), key=lambda x: x[1], reverse=True)
    total = sum(data.values())
    
    response = f"Across {len(cities)} cities, total arrests were {format_number(total)}. "
    response += f"{sorted_cities[0][0]} leads with {format_number(sorted_cities[0][1])}, "
    response += f"followed by {sorted_cities[1][0]} ({format_number(sorted_cities[1][1])})"
    
    return response + "."


def format_trend_response(trend_data, city):
    """Format trend analysis response"""
    years = sorted(trend_data.keys())
    
    if len(years) < 2:
        return f"Insufficient data for trend analysis in {city}."
    
    first_year = years[0]
    last_year = years[-1]
    first_val = trend_data[first_year]
    last_val = trend_data[last_year]
    
    change = last_val - first_val
    pct_change = (change / first_val * 100) if first_val > 0 else 0
    
    direction = "increased" if change > 0 else "decreased" if change < 0 else "remained stable"
    
    response = f"In {city}, arrests {direction} from {format_number(first_val)} in {first_year} "
    response += f"to {format_number(last_val)} in {last_year}"
    
    if change != 0:
        response += f", a change of {format_number(abs(change))} ({abs(pct_change):.1f}%)"
    
    # Add year-by-year context
    if len(years) > 2:
        response += ". "
        increases = sum(1 for i in range(len(years)-1) if trend_data[years[i+1]] > trend_data[years[i]])
        if increases == len(years) - 1:
            response += "The trend shows consistent growth"
        elif increases == 0:
            response += "The trend shows consistent decline"
        else:
            response += "The trend shows fluctuation"
    
    return response + "."


def format_ranking_response(ranking_data, context):
    """Format ranking response"""
    if not ranking_data:
        return "No ranking data available."
    
    top_city = ranking_data[0]
    response = f"{top_city['city']} ranks #1 with {format_number(top_city['arrests'])} arrests"
    
    if context.get("year"):
        response += f" in {context['year']}"
    
    if len(ranking_data) > 1:
        response += f". The top 3 are: "
        top_3 = [f"{r['city']} ({format_number(r['arrests'])})" for r in ranking_data[:3]]
        response += ", ".join(top_3)
    
    return response + "."


def format_statistical_response(stats, context):
    """Format statistical analysis response"""
    response = f"Statistical summary: "
    response += f"Average = {format_number(stats['mean'])}, "
    response += f"Median = {format_number(stats['median'])}, "
    response += f"Range = {format_number(stats['min'])} to {format_number(stats['max'])}"
    
    return response + "."


def format_error_with_help(error_msg, suggestions):
    """Format error message with helpful suggestions"""
    response = {
        "error": error_msg,
        "help": "Here are some things you can try:",
        "suggestions": suggestions
    }
    return response


def format_gender_analysis(gender_data, city, year):
    """Format gender gap analysis"""
    if not gender_data:
        return "Gender data not available."
    
    response = f"In {city} ({year}), "
    response += f"male arrests were {format_number(gender_data['male_arrests'])} ({gender_data['male_percentage']}%) "
    response += f"and female arrests were {format_number(gender_data['female_arrests'])} ({gender_data['female_percentage']}%). "
    response += f"The male-to-female ratio is {gender_data['male_to_female_ratio']}:1"
    
    return response + "."
