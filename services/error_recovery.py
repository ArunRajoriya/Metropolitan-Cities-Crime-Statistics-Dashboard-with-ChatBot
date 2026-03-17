"""
Smart Error Recovery System for Chatbot
"""
import re
from difflib import get_close_matches
from services.data_loader import crime_data


class ErrorRecoverySystem:
    """Intelligent error handling and query recovery"""
    
    def __init__(self):
        self.error_patterns = {
            'city_not_found': self._handle_city_not_found,
            'year_not_available': self._handle_year_not_available,
            'insufficient_data': self._handle_insufficient_data,
            'ambiguous_query': self._handle_ambiguous_query,
            'no_results': self._handle_no_results
        }
    
    def recover_from_error(self, error_type, original_query, extracted_data, context=None):
        """Attempt to recover from query errors"""
        handler = self.error_patterns.get(error_type)
        if handler:
            return handler(original_query, extracted_data, context)
        
        return self._generic_recovery(original_query, extracted_data)
    
    def _handle_city_not_found(self, query, extracted, context):
        """Handle city not found errors with smart suggestions"""
        cities = extracted.get('cities', [])
        if not cities:
            return self._generic_recovery(query, extracted)
        
        # Get all available cities
        all_cities = self._get_available_cities()
        
        suggestions = []
        corrections = []
        
        for city in cities:
            # Find close matches
            matches = get_close_matches(city.lower(), 
                                      [c.lower() for c in all_cities], 
                                      n=3, cutoff=0.6)
            
            if matches:
                # Find original case versions
                original_matches = []
                for match in matches:
                    for orig_city in all_cities:
                        if orig_city.lower() == match:
                            original_matches.append(orig_city)
                            break
                
                corrections.append({
                    'input': city,
                    'suggestions': original_matches
                })
        
        if corrections:
            # Generate corrected queries
            for correction in corrections:
                for suggestion in correction['suggestions'][:2]:
                    corrected_query = query.replace(correction['input'], suggestion)
                    suggestions.append(corrected_query)
        
        return {
            'type': 'city_correction',
            'message': f"City '{cities[0]}' not found in database.",
            'corrections': corrections,
            'suggested_queries': suggestions[:3],
            'available_cities': all_cities[:10]  # Show top 10 cities
        }
    
    def _handle_year_not_available(self, query, extracted, context):
        """Handle unavailable year errors"""
        years = extracted.get('years', [])
        available_years = sorted(crime_data.keys())
        
        suggestions = []
        
        for year in years:
            # Find closest available year
            year_int = int(year) if year.isdigit() else 2020
            closest_year = min(available_years, key=lambda x: abs(int(x) - year_int))
            
            corrected_query = query.replace(str(year), closest_year)
            suggestions.append(corrected_query)
        
        return {
            'type': 'year_correction',
            'message': f"Data not available for {', '.join(years)}.",
            'available_years': available_years,
            'suggested_queries': suggestions,
            'closest_matches': [min(available_years, key=lambda x: abs(int(x) - int(y))) for y in years if y.isdigit()]
        }
    
    def _handle_insufficient_data(self, query, extracted, context):
        """Handle insufficient data errors"""
        suggestions = []
        
        # Add more context to the query
        if not extracted.get('years'):
            suggestions.append(f"{query} in 2020")
            suggestions.append(f"{query} from 2016 to 2020")
        
        if not extracted.get('cities') and context and context.get('popular_cities'):
            for city in context['popular_cities'][:2]:
                suggestions.append(f"{city} {query}")
        
        return {
            'type': 'insufficient_data',
            'message': "Need more specific information to provide accurate results.",
            'suggested_queries': suggestions,
            'help_text': "Try specifying a city, year, or type of analysis you want."
        }
    
    def _handle_ambiguous_query(self, query, extracted, context):
        """Handle ambiguous queries"""
        clarifications = []
        
        # Check what's ambiguous
        if len(extracted.get('cities', [])) > 5:
            clarifications.append("Too many cities mentioned. Please specify 2-3 cities for comparison.")
        
        if not extracted.get('intent'):
            clarifications.append("What would you like to know? (statistics, comparison, trend, ranking)")
        
        # Generate specific suggestions
        suggestions = [
            "Compare Delhi and Mumbai arrests in 2020",
            "Show me top 5 cities by crime",
            "Bangalore crime trend from 2016 to 2020"
        ]
        
        return {
            'type': 'ambiguous_query',
            'message': "Your query is ambiguous. Please clarify:",
            'clarifications': clarifications,
            'suggested_queries': suggestions
        }
    
    def _handle_no_results(self, query, extracted, context):
        """Handle no results found"""
        alternatives = []
        
        # Suggest broader queries
        if extracted.get('cities') and extracted.get('years'):
            city = extracted['cities'][0]
            year = extracted['years'][0]
            alternatives.extend([
                f"All crime statistics for {city} in {year}",
                f"{city} arrests across all years",
                f"Compare {city} with other cities in {year}"
            ])
        
        return {
            'type': 'no_results',
            'message': "No data found for your specific query.",
            'alternatives': alternatives,
            'suggestion': "Try a broader search or check available data."
        }
    
    def _generic_recovery(self, query, extracted):
        """Generic recovery for unknown errors"""
        return {
            'type': 'generic_error',
            'message': "I couldn't process your query. Here are some suggestions:",
            'suggested_queries': [
                "Show me Delhi arrests in 2020",
                "Compare Mumbai and Chennai",
                "Top 5 cities by crime rate",
                "Crime trend analysis"
            ],
            'help_text': "Try using specific city names, years (2016, 2019, 2020), and clear intentions."
        }
    
    def _get_available_cities(self):
        """Get all available cities from datasets"""
        cities = set()
        for year_data in crime_data.values():
            if not year_data.empty and "City" in year_data.columns:
                city_list = year_data["City"].dropna().tolist()
                cities.update([c.strip() for c in city_list if "total" not in c.lower()])
        return sorted(list(cities))


# Global error recovery instance
error_recovery = ErrorRecoverySystem()