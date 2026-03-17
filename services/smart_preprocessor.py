"""
Smart Query Preprocessor for Enhanced User Experience
"""
import re
from difflib import get_close_matches
from services.data_loader import crime_data


class SmartPreprocessor:
    """Intelligent query preprocessing and enhancement"""
    
    def __init__(self):
        self.common_abbreviations = {
            'del': 'delhi', 'mum': 'mumbai', 'blr': 'bangalore', 'bang': 'bangalore',
            'chen': 'chennai', 'kol': 'kolkata', 'hyd': 'hyderabad', 'pune': 'pune',
            'ahm': 'ahmedabad', 'sur': 'surat', 'jaipur': 'jaipur', 'luck': 'lucknow',
            'kan': 'kanpur', 'nag': 'nagpur', 'ind': 'indore', 'thr': 'thane',
            'bho': 'bhopal', 'vis': 'visakhapatnam', 'pat': 'patna', 'vad': 'vadodara',
            'lud': 'ludhiana', 'agr': 'agra', 'nash': 'nashik', 'fari': 'faridabad',
            'mee': 'meerut', 'raj': 'rajkot', 'kal': 'kalyan', 'vas': 'vasai',
            'vai': 'varanasi', 'sri': 'srinagar', 'aur': 'aurangabad', 'dha': 'dhanbad',
            'amb': 'amritsar', 'all': 'allahabad', 'ran': 'ranchi', 'how': 'howrah',
            'jab': 'jabalpur', 'gwa': 'gwalior', 'vij': 'vijayawada', 'jod': 'jodhpur',
            'mad': 'madurai', 'rai': 'raipur', 'kot': 'kota', 'gun': 'guntakal',
            'chan': 'chandigarh', 'mys': 'mysore', 'bar': 'bareilly', 'ali': 'aligarh',
            'mor': 'moradabad', 'gor': 'gorakhpur', 'jam': 'jalandhar', 'tir': 'tiruchirapalli',
            'sal': 'salem', 'tir': 'tirunelveli', 'kok': 'kozhikode', 'thr': 'thrissur',
            'col': 'kollam', 'ern': 'ernakulam', 'tvm': 'thiruvananthapuram'
        }
        
        self.query_templates = {
            'comparison': [
                'Compare {city1} and {city2} in {year}',
                'Show me {city1} vs {city2} arrests',
                '{city1} versus {city2} crime statistics'
            ],
            'trend': [
                'Show {city} trend from {start_year} to {end_year}',
                '{city} arrest trend over time',
                'Crime trend analysis for {city}'
            ],
            'ranking': [
                'Top {n} cities by crime in {year}',
                'Highest crime cities in {year}',
                'City rankings for {year}'
            ],
            'statistics': [
                '{city} crime statistics in {year}',
                'Show me {city} arrests for {year}',
                '{gender} arrests in {city} {year}'
            ]
        }
        
        self.intent_keywords = {
            'comparison': ['compare', 'vs', 'versus', 'between', 'difference'],
            'trend': ['trend', 'over time', 'change', 'growth', 'pattern'],
            'ranking': ['top', 'highest', 'lowest', 'best', 'worst', 'rank'],
            'statistics': ['show', 'tell', 'what', 'how many', 'statistics']
        }
    
    def preprocess_query(self, message):
        """Preprocess and enhance user query"""
        original_message = message
        enhanced_message = message.lower().strip()
        
        # Expand abbreviations
        enhanced_message = self._expand_abbreviations(enhanced_message)
        
        # Fix common typos
        enhanced_message = self._fix_common_typos(enhanced_message)
        
        # Normalize year formats
        enhanced_message = self._normalize_years(enhanced_message)
        
        # Add context if missing
        enhanced_message = self._add_missing_context(enhanced_message)
        
        return {
            'original': original_message,
            'enhanced': enhanced_message,
            'suggestions': self._generate_query_suggestions(enhanced_message),
            'confidence': self._calculate_enhancement_confidence(original_message, enhanced_message)
        }
    
    def _expand_abbreviations(self, message):
        """Expand common city abbreviations"""
        words = message.split()
        expanded_words = []
        
        for word in words:
            # Remove punctuation for matching
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in self.common_abbreviations:
                expanded_words.append(self.common_abbreviations[clean_word])
            else:
                expanded_words.append(word)
        
        return ' '.join(expanded_words)
    
    def _fix_common_typos(self, message):
        """Fix common typos in city names and keywords"""
        typo_fixes = {
            'delhii': 'delhi', 'mumbaii': 'mumbai', 'bangalor': 'bangalore',
            'chenai': 'chennai', 'kolkatta': 'kolkata', 'hyderabaad': 'hyderabad',
            'arests': 'arrests', 'arest': 'arrest', 'criem': 'crime',
            'statistcs': 'statistics', 'comparision': 'comparison',
            'anaylsis': 'analysis', 'trand': 'trend'
        }
        
        for typo, correction in typo_fixes.items():
            message = re.sub(r'\b' + typo + r'\b', correction, message, flags=re.IGNORECASE)
        
        return message
    
    def _normalize_years(self, message):
        """Normalize year formats and handle ranges"""
        # Convert "20" to "2020", "19" to "2019", etc.
        message = re.sub(r'\b(1[6-9]|20)\b', lambda m: '20' + m.group(1), message)
        
        # Handle year ranges
        message = re.sub(r'(\d{4})\s*-\s*(\d{4})', r'\1 to \2', message)
        message = re.sub(r'(\d{4})\s*–\s*(\d{4})', r'\1 to \2', message)
        
        return message
    
    def _add_missing_context(self, message):
        """Add missing context based on query patterns"""
        # If user asks for "trend" without years, suggest using all years
        if 'trend' in message and not re.search(r'\d{4}', message):
            message += ' from 2016 to 2020'
        
        # If user asks for "top" without number, add default
        if re.search(r'\btop\b', message) and not re.search(r'top\s+\d+', message):
            message = re.sub(r'\btop\b', 'top 5', message)
        
        return message
    
    def _generate_query_suggestions(self, message):
        """Generate smart query suggestions"""
        suggestions = []
        
        # Detect intent and generate relevant suggestions
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in message for keyword in keywords):
                templates = self.query_templates.get(intent, [])
                suggestions.extend(templates[:2])  # Add top 2 templates
        
        # Add popular queries if no specific intent detected
        if not suggestions:
            suggestions = [
                'Compare Delhi and Mumbai arrests in 2020',
                'Show me top 5 cities by crime',
                'Bangalore crime trend from 2016 to 2020',
                'Gender-wise breakdown for Chennai'
            ]
        
        return suggestions[:3]
    
    def _calculate_enhancement_confidence(self, original, enhanced):
        """Calculate confidence in query enhancement"""
        if original.lower() == enhanced.lower():
            return 1.0  # No changes needed
        
        # Calculate based on number of improvements made
        improvements = 0
        
        # Check for abbreviation expansions
        for abbr in self.common_abbreviations:
            if abbr in original.lower() and abbr not in enhanced.lower():
                improvements += 1
        
        # Check for typo fixes
        if len(enhanced.split()) != len(original.split()):
            improvements += 1
        
        # Check for context additions
        if len(enhanced) > len(original) * 1.2:
            improvements += 1
        
        return min(1.0, 0.7 + (improvements * 0.1))
    
    def get_autocomplete_suggestions(self, partial_query):
        """Get autocomplete suggestions for partial queries"""
        suggestions = []
        partial_lower = partial_query.lower()
        
        # City name suggestions
        all_cities = self._get_all_cities()
        city_matches = [city for city in all_cities if city.lower().startswith(partial_lower)]
        suggestions.extend(city_matches[:5])
        
        # Common query patterns
        common_patterns = [
            'Compare Delhi and Mumbai',
            'Top 5 cities by crime',
            'Show me trend analysis',
            'Gender breakdown for',
            'Crime statistics in 2020',
            'Juvenile crime data',
            'Foreign crime statistics'
        ]
        
        pattern_matches = [pattern for pattern in common_patterns 
                          if pattern.lower().startswith(partial_lower)]
        suggestions.extend(pattern_matches[:3])
        
        return suggestions[:8]
    
    def _get_all_cities(self):
        """Get all available cities from data"""
        cities = set()
        for year_data in crime_data.values():
            if not year_data.empty and "City" in year_data.columns:
                city_list = year_data["City"].dropna().tolist()
                cities.update([c.strip().split('(')[0].strip() for c in city_list 
                              if "total" not in c.lower()])
        return sorted(list(cities))


# Global preprocessor instance
smart_preprocessor = SmartPreprocessor()