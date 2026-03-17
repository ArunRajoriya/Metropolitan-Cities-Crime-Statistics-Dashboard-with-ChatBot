#!/usr/bin/env python3
"""
Test script to verify the top cities fix
"""
import pandas as pd

def test_city_counts():
    """Test to verify city counts in each year"""
    
    years = ["2016", "2019", "2020"]
    
    for year in years:
        try:
            df = pd.read_csv(f"data/crime_data_{year}.csv")
            
            # Filter out total rows and null cities
            df_clean = df[df["City"].notna()]
            df_clean = df_clean[~df_clean["City"].str.lower().str.contains("total", na=False)]
            
            city_count = len(df_clean)
            cities = df_clean["City"].tolist()
            
            print(f"\n=== {year} Dataset ===")
            print(f"Total cities: {city_count}")
            print(f"Cities: {cities}")
            
        except Exception as e:
            print(f"Error reading {year} data: {e}")

if __name__ == "__main__":
    test_city_counts()