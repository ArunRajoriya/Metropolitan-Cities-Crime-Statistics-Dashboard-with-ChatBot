"""
Intelligent Query Handler - Enhanced chatbot capabilities
"""
import pandas as pd
from difflib import get_close_matches
from services.data_loader import crime_data, gov_data, foreign_data
from services.analytics_engine import calculate_city_totals
from services.insight_generator import generate_insight


class IntelligentQueryHandler:
    """Enhanced query processing with fuzzy matching and context awareness"""
    
    def __init__(self):
        self.cache = {}
        self.all_cities = self._extract_all_cities()
        self.all_crimes = self._extract_all_crimes()
        
    def _extract_all_cities(self):
        """Extract unique city names from all datasets"""
        cities = set()
        for year_data in crime_data.values():
            if not year_data.empty and "City" in year_data.columns:
                city_list = year_data["City"].dropna().tolist()
                cities.update([c.strip() for c in city_list if "total" not in c.lower()])
        return sorted(list(cities))
    
    def _extract_all_crimes(self):
        """Extract unique crime types from government dataset"""
        crimes = set()
        for year_data in gov_data.values():
            if not year_data.empty and "Crime Head" in year_data.columns:
                crime_list = year_data["Crime Head"].dropna().tolist()
                crimes.update([c.strip().lower() for c in crime_list])
        return sorted(list(crimes))
    
    def fuzzy_match_city(self, city_input, threshold=0.6):
        """Find closest matching city name"""
        if not city_input:
            return None
        
        city_lower = city_input.lower()
        
        # First try exact substring match (e.g., "indore" in "Indore(Madhya Pradesh)")
        for city in self.all_cities:
            if city_lower in city.lower():
                return city
        
        # Then try fuzzy matching
        matches = get_close_matches(city_lower, 
                                    [c.lower() for c in self.all_cities], 
                                    n=1, cutoff=threshold)
        if matches:
            # Return original case city name
            for city in self.all_cities:
                if city.lower() == matches[0]:
                    return city
        
        # Finally, try matching just the city name part (before parenthesis)
        city_names_only = [c.split('(')[0].strip().lower() for c in self.all_cities]
        matches = get_close_matches(city_lower, city_names_only, n=1, cutoff=threshold)
        if matches:
            # Find the full city name
            for city in self.all_cities:
                if city.split('(')[0].strip().lower() == matches[0]:
                    return city
        
        return None
    
    def fuzzy_match_crime(self, crime_input, threshold=0.6):
        """Find closest matching crime type"""
        if not crime_input:
            return None
        
        matches = get_close_matches(crime_input.lower(), 
                                    self.all_crimes, 
                                    n=1, cutoff=threshold)
        return matches[0] if matches else None
    
    def validate_and_correct_query(self, structured):
        """Validate and auto-correct extracted data"""
        corrected = structured.copy()
        
        # Fuzzy match cities
        if "cities" in corrected and corrected["cities"]:
            matched_cities = []
            for city in corrected["cities"]:
                matched = self.fuzzy_match_city(city)
                if matched:
                    matched_cities.append(matched)
            corrected["cities"] = matched_cities
        
        # Fuzzy match crime
        if "crime" in corrected and corrected["crime"]:
            matched_crime = self.fuzzy_match_crime(corrected["crime"])
            if matched_crime:
                corrected["crime"] = matched_crime
        
        # Validate years
        if "years" in corrected and corrected["years"]:
            valid_years = [str(y) for y in corrected["years"] if str(y) in crime_data]
            corrected["years"] = valid_years
        
        return corrected
    
    def get_contextual_suggestions(self, structured, error_type="general"):
        """Generate smart suggestions based on query context"""
        suggestions = []
        
        if error_type == "city_not_found":
            # Suggest similar cities
            if structured.get("cities"):
                for city in structured["cities"][:2]:
                    similar = get_close_matches(city.lower(), 
                                               [c.lower() for c in self.all_cities], 
                                               n=3, cutoff=0.4)
                    if similar:
                        suggestions.append(f"Did you mean: {', '.join(similar[:3])}?")
        
        elif error_type == "year_not_found":
            suggestions.append("Available years: 2016, 2019, 2020")
            suggestions.append("Try: 'Show arrests in Delhi 2020'")
        
        elif error_type == "no_data":
            suggestions.append("Try asking about: arrests, crime statistics, city comparisons")
            suggestions.append("Example: 'Compare Mumbai and Delhi arrests in 2020'")
        
        # Add general helpful suggestions
        if not suggestions:
            suggestions = [
                "Top 3 cities with highest arrests in 2020",
                "Compare male and female arrests in Delhi 2019",
                "Show juvenile crime statistics for Mumbai",
                "What are the murder statistics for 2020?"
            ]
        
        return suggestions
    
    def generate_detailed_insight(self, query, data, context):
        """Generate comprehensive insights with context"""
        insight_parts = []
        
        # Add data summary
        if isinstance(data, dict):
            if len(data) == 1:
                key, value = list(data.items())[0]
                insight_parts.append(f"{key} recorded {value:,} arrests")
            elif len(data) > 1:
                total = sum(data.values())
                insight_parts.append(f"Total of {total:,} arrests across {len(data)} cities")
                
                # Add comparison
                sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
                highest = sorted_data[0]
                lowest = sorted_data[-1]
                insight_parts.append(
                    f"{highest[0]} leads with {highest[1]:,}, "
                    f"while {lowest[0]} has {lowest[1]:,}"
                )
        
        # Add year context
        if context.get("year"):
            insight_parts.append(f"in {context['year']}")
        
        # Add gender context
        if context.get("gender"):
            insight_parts.append(f"for {context['gender']} population")
        
        return ". ".join(insight_parts) + "."
    
    def handle_complex_query(self, structured, message):
        """Handle multi-dimensional queries"""
        # Check for trend analysis
        if structured.get("intent") == "trend" and len(structured.get("years", [])) > 1:
            return self._handle_trend_analysis(structured)
        
        # Check for percentage/ratio queries
        if "percentage" in message.lower() or "ratio" in message.lower():
            return self._handle_percentage_query(structured)
        
        # Check for ranking queries
        if "rank" in message.lower() or "position" in message.lower():
            return self._handle_ranking_query(structured)
        
        return None
    
    def _handle_trend_analysis(self, structured):
        """Analyze trends across multiple years"""
        cities = structured.get("cities", [])
        city = cities[0] if cities else None
        years = sorted(structured.get("years", []))
        gender = structured.get("gender")
        
        if not city or len(years) < 2:
            return None
        
        import re
        trend_data = {}
        for year in years:
            if year in crime_data:
                df = crime_data[year]
                # Escape regex special characters in city name
                city_escaped = re.escape(city)
                row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]
                if not row.empty:
                    total = calculate_city_totals(row.iloc[0].to_dict(), gender)
                    trend_data[year] = int(total)
        
        if len(trend_data) < 2:
            return None
        
        # Calculate trend
        years_list = sorted(trend_data.keys())
        first_year = years_list[0]
        last_year = years_list[-1]
        change = trend_data[last_year] - trend_data[first_year]
        pct_change = (change / trend_data[first_year] * 100) if trend_data[first_year] > 0 else 0
        
        # Extract city name without state for display
        city_display = city.split('(')[0].strip()
        
        return {
            "type": "trend_analysis",
            "title": f"Arrest Trend - {city_display} ({first_year}-{last_year})",
            "data": trend_data,
            "insight": f"In {city_display}, arrests {'increased' if change > 0 else 'decreased'} by {abs(change):,} ({abs(pct_change):.1f}%) from {first_year} to {last_year}.",
            "source": "NCRB Dataset"
        }
    
    def _handle_percentage_query(self, structured):
        """Calculate percentages and ratios"""
        # Implementation for percentage calculations
        return None
    
    def _handle_ranking_query(self, structured):
        """Show city rankings"""
        year = structured.get("years", [list(crime_data.keys())[-1]])[0]
        gender = structured.get("gender")
        
        if year not in crime_data:
            return None
        
        df = crime_data[year]
        df = df[df["City"].notna()]
        df = df[~df["City"].str.lower().str.contains("total", na=False)]
        
        rankings = []
        for _, row in df.iterrows():
            city = row["City"]
            total = calculate_city_totals(row.to_dict(), gender)
            rankings.append({"city": city, "arrests": int(total)})
        
        rankings.sort(key=lambda x: x["arrests"], reverse=True)
        
        # Add rank numbers
        for i, item in enumerate(rankings, 1):
            item["rank"] = i
        
        return {
            "type": "ranking",
            "title": f"City Rankings by Arrests - {year}",
            "data": rankings[:10],  # Top 10
            "source": "NCRB Dataset"
        }


# Global instance
intelligent_handler = IntelligentQueryHandler()
