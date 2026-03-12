"""
Advanced Analytics Module - Complex statistical analysis
"""
import pandas as pd
import numpy as np
from services.data_loader import crime_data, gov_data
from services.analytics_engine import calculate_city_totals


def calculate_statistics(data_dict):
    """Calculate statistical measures"""
    values = list(data_dict.values())
    
    return {
        "mean": np.mean(values),
        "median": np.median(values),
        "std_dev": np.std(values),
        "min": min(values),
        "max": max(values),
        "total": sum(values)
    }


def calculate_growth_rate(year1_data, year2_data):
    """Calculate year-over-year growth rate"""
    if year1_data == 0:
        return 0
    
    growth = ((year2_data - year1_data) / year1_data) * 100
    return round(growth, 2)


def get_percentile_rank(city, year, gender=None):
    """Get percentile rank of a city"""
    if year not in crime_data:
        return None
    
    df = crime_data[year]
    df = df[df["City"].notna()]
    df = df[~df["City"].str.lower().str.contains("total", na=False)]
    
    city_totals = []
    target_value = None
    
    for _, row in df.iterrows():
        total = calculate_city_totals(row.to_dict(), gender)
        city_totals.append(total)
        
        if city.lower() in row["City"].lower():
            target_value = total
    
    if target_value is None:
        return None
    
    # Calculate percentile
    below = sum(1 for x in city_totals if x < target_value)
    percentile = (below / len(city_totals)) * 100
    
    return round(percentile, 1)


def compare_with_average(city, year, gender=None):
    """Compare city data with national average"""
    if year not in crime_data:
        return None
    
    import re
    df = crime_data[year]
    df = df[df["City"].notna()]
    df = df[~df["City"].str.lower().str.contains("total", na=False)]
    
    city_totals = []
    target_value = None
    
    # Escape regex special characters
    city_escaped = re.escape(city)
    
    for _, row in df.iterrows():
        total = calculate_city_totals(row.to_dict(), gender)
        city_totals.append(total)
        
        if re.search(city_escaped, row["City"], re.IGNORECASE):
            target_value = total
    
    if target_value is None:
        return None
    
    avg = np.mean(city_totals)
    diff = target_value - avg
    pct_diff = (diff / avg) * 100 if avg > 0 else 0
    
    return {
        "city_value": int(target_value),
        "national_average": int(avg),
        "difference": int(diff),
        "percentage_difference": round(pct_diff, 1),
        "status": "above" if diff > 0 else "below"
    }


def get_crime_breakdown(city, year):
    """Get detailed crime breakdown for a city"""
    # This would require crime-specific columns in the dataset
    # Placeholder for future implementation
    return None


def analyze_gender_gap(city, year):
    """Analyze male vs female arrest gap"""
    if year not in crime_data:
        return None
    
    import re
    df = crime_data[year]
    
    # Escape regex special characters
    city_escaped = re.escape(city)
    row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]
    
    if row.empty:
        return None
    
    data = row.iloc[0].to_dict()
    male_total = calculate_city_totals(data, "male")
    female_total = calculate_city_totals(data, "female")
    
    if male_total == 0 and female_total == 0:
        return None
    
    total = male_total + female_total
    male_pct = (male_total / total * 100) if total > 0 else 0
    female_pct = (female_total / total * 100) if total > 0 else 0
    ratio = male_total / female_total if female_total > 0 else 0
    
    return {
        "male_arrests": int(male_total),
        "female_arrests": int(female_total),
        "male_percentage": round(male_pct, 1),
        "female_percentage": round(female_pct, 1),
        "male_to_female_ratio": round(ratio, 2)
    }


def get_top_cities_by_metric(year, metric="total", gender=None, top_n=10):
    """Get top N cities by specified metric"""
    if year not in crime_data:
        return None
    
    df = crime_data[year]
    df = df[df["City"].notna()]
    df = df[~df["City"].str.lower().str.contains("total", na=False)]
    
    city_data = []
    
    for _, row in df.iterrows():
        city = row["City"]
        total = calculate_city_totals(row.to_dict(), gender)
        city_data.append({"city": city, "value": int(total)})
    
    # Sort by value
    city_data.sort(key=lambda x: x["value"], reverse=True)
    
    return city_data[:top_n]


def calculate_correlation(city1, city2, years):
    """Calculate correlation between two cities across years"""
    city1_values = []
    city2_values = []
    
    import re
    
    for year in years:
        if year not in crime_data:
            continue
        
        df = crime_data[year]
        
        # Escape regex special characters
        city1_escaped = re.escape(city1)
        city2_escaped = re.escape(city2)
        
        row1 = df[df["City"].str.contains(city1_escaped, case=False, na=False, regex=True)]
        row2 = df[df["City"].str.contains(city2_escaped, case=False, na=False, regex=True)]
        
        if not row1.empty and not row2.empty:
            val1 = calculate_city_totals(row1.iloc[0].to_dict(), None)
            val2 = calculate_city_totals(row2.iloc[0].to_dict(), None)
            city1_values.append(val1)
            city2_values.append(val2)
    
    if len(city1_values) < 2:
        return None
    
    correlation = np.corrcoef(city1_values, city2_values)[0, 1]
    
    return {
        "correlation": round(correlation, 3),
        "interpretation": "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.4 else "weak"
    }
