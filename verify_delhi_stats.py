#!/usr/bin/env python3
"""
Verify Delhi's percentile rank and national average calculations
"""
import pandas as pd
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.analytics_engine import calculate_city_totals

def verify_delhi_calculations():
    """Verify the exact calculations for Delhi 2020"""
    
    # Load 2020 data
    df = pd.read_csv("data/crime_data_2020.csv")
    
    # Clean data (remove totals and null cities)
    df = df[df["City"].notna()]
    df = df[~df["City"].str.lower().str.contains("total", na=False)]
    
    print("=== 2020 Dataset Analysis ===")
    print(f"Total cities: {len(df)}")
    
    # Calculate totals for all cities
    city_totals = []
    delhi_total = None
    
    for _, row in df.iterrows():
        city = row["City"]
        total = calculate_city_totals(row.to_dict(), None)  # No gender filter
        city_totals.append({"city": city, "total": int(total)})
        
        if "delhi" in city.lower():
            delhi_total = int(total)
            delhi_city_name = city
    
    # Sort by total arrests
    city_totals.sort(key=lambda x: x["total"], reverse=True)
    
    print(f"\n=== All Cities (sorted by arrests) ===")
    for i, city_data in enumerate(city_totals, 1):
        marker = " ← DELHI" if "delhi" in city_data["city"].lower() else ""
        print(f"{i:2d}. {city_data['city']:<25} {city_data['total']:>8,}{marker}")
    
    # Calculate percentile rank
    total_values = [x["total"] for x in city_totals]
    below_delhi = sum(1 for x in total_values if x < delhi_total)
    percentile = (below_delhi / len(total_values)) * 100
    
    print(f"\n=== Percentile Calculation ===")
    print(f"Delhi arrests: {delhi_total:,}")
    print(f"Cities below Delhi: {below_delhi}")
    print(f"Total cities: {len(total_values)}")
    print(f"Percentile rank: ({below_delhi}/{len(total_values)}) * 100 = {percentile:.1f}%")
    
    # Calculate national average comparison
    national_avg = sum(total_values) / len(total_values)
    difference = delhi_total - national_avg
    percentage_diff = (difference / national_avg) * 100
    
    print(f"\n=== National Average Comparison ===")
    print(f"Delhi arrests: {delhi_total:,}")
    print(f"National average: {national_avg:,.0f}")
    print(f"Difference: {difference:,.0f}")
    print(f"Percentage above average: {percentage_diff:.1f}%")
    
    print(f"\n=== Final Results ===")
    print(f"Delhi Percentile Rank: {percentile:.1f}%")
    print(f"Above National Average by: {percentage_diff:.1f}%")

if __name__ == "__main__":
    verify_delhi_calculations()