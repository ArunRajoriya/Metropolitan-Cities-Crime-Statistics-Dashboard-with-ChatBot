"""
Conversation Context Manager for Chatbot
"""
import time
from collections import deque


class ConversationContext:
    """Manage conversation context and follow-up queries"""
    
    def __init__(self, max_history=10, context_ttl=1800):  # 30 minutes
        self.sessions = {}
        self.max_history = max_history
        self.context_ttl = context_ttl
    
    def get_session_id(self, request):
        """Generate session ID from request (IP + User-Agent hash)"""
        import hashlib
        session_data = f"{request.remote_addr}_{request.headers.get('User-Agent', '')}"
        return hashlib.md5(session_data.encode()).hexdigest()[:16]
    
    def add_interaction(self, session_id, query, response, extracted_data):
        """Add interaction to conversation history"""
        current_time = time.time()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'history': deque(maxlen=self.max_history),
                'last_context': {},
                'last_activity': current_time
            }
        
        interaction = {
            'timestamp': current_time,
            'query': query,
            'response_type': response.get('type'),
            'extracted_data': extracted_data,
            'entities': {
                'cities': extracted_data.get('cities', []),
                'years': extracted_data.get('years', []),
                'gender': extracted_data.get('gender'),
                'intent': extracted_data.get('intent')
            }
        }
        
        self.sessions[session_id]['history'].append(interaction)
        self.sessions[session_id]['last_activity'] = current_time
        self._update_context(session_id, extracted_data)
    
    def get_context_enhanced_query(self, session_id, current_query, current_extracted):
        """Enhance current query with conversation context"""
        if session_id not in self.sessions:
            return current_extracted
        
        session = self.sessions[session_id]
        
        # Check if session is still valid
        if time.time() - session['last_activity'] > self.context_ttl:
            del self.sessions[session_id]
            return current_extracted
        
        enhanced_extracted = current_extracted.copy()
        last_context = session['last_context']
        
        # Inherit missing entities from context
        if not enhanced_extracted.get('cities') and last_context.get('cities'):
            enhanced_extracted['cities'] = last_context['cities']
        
        if not enhanced_extracted.get('years') and last_context.get('years'):
            enhanced_extracted['years'] = last_context['years']
        
        if not enhanced_extracted.get('gender') and last_context.get('gender'):
            enhanced_extracted['gender'] = last_context['gender']
        
        # Handle follow-up patterns
        enhanced_extracted = self._handle_followup_patterns(
            current_query, enhanced_extracted, session['history']
        )
        
        return enhanced_extracted
    
    def _update_context(self, session_id, extracted_data):
        """Update session context with latest interaction"""
        context = self.sessions[session_id]['last_context']
        
        # Update with non-empty values
        if extracted_data.get('cities'):
            context['cities'] = extracted_data['cities']
        
        if extracted_data.get('years'):
            context['years'] = extracted_data['years']
        
        if extracted_data.get('gender'):
            context['gender'] = extracted_data['gender']
        
        if extracted_data.get('intent'):
            context['last_intent'] = extracted_data['intent']
    
    def _handle_followup_patterns(self, query, extracted, history):
        """Handle common follow-up patterns"""
        query_lower = query.lower()
        
        if not history:
            return extracted
        
        last_interaction = history[-1]
        
        # Pattern: "What about [year]?" - inherit cities from last query
        if query_lower.startswith('what about') and extracted.get('years'):
            if last_interaction['entities'].get('cities'):
                extracted['cities'] = last_interaction['entities']['cities']
        
        # Pattern: "Show me the trend" - inherit cities and use all years
        if 'trend' in query_lower and not extracted.get('cities'):
            if last_interaction['entities'].get('cities'):
                extracted['cities'] = last_interaction['entities']['cities']
                extracted['years'] = ['2016', '2019', '2020']  # All available years
        
        # Pattern: "Compare with [city]" - add to existing cities
        if 'compare with' in query_lower or 'vs' in query_lower:
            if last_interaction['entities'].get('cities') and extracted.get('cities'):
                # Combine cities from context and current query
                all_cities = last_interaction['entities']['cities'] + extracted['cities']
                extracted['cities'] = list(set(all_cities))  # Remove duplicates
        
        # Pattern: "For males/females" - inherit other context
        if extracted.get('gender') and not extracted.get('cities'):
            if last_interaction['entities'].get('cities'):
                extracted['cities'] = last_interaction['entities']['cities']
            if last_interaction['entities'].get('years'):
                extracted['years'] = last_interaction['entities']['years']
        
        # Pattern: "In [year]" - inherit cities and intent
        if extracted.get('years') and not extracted.get('cities'):
            if last_interaction['entities'].get('cities'):
                extracted['cities'] = last_interaction['entities']['cities']
            if not extracted.get('intent') and last_interaction['entities'].get('intent'):
                extracted['intent'] = last_interaction['entities']['intent']
        
        return extracted
    
    def get_conversation_summary(self, session_id):
        """Get summary of conversation for context"""
        if session_id not in self.sessions:
            return None
        
        history = list(self.sessions[session_id]['history'])
        if not history:
            return None
        
        # Analyze conversation patterns
        cities_mentioned = set()
        years_mentioned = set()
        intents_used = set()
        
        for interaction in history[-5:]:  # Last 5 interactions
            entities = interaction['entities']
            cities_mentioned.update(entities.get('cities', []))
            years_mentioned.update(entities.get('years', []))
            if entities.get('intent'):
                intents_used.add(entities['intent'])
        
        return {
            'cities_discussed': list(cities_mentioned),
            'years_discussed': list(years_mentioned),
            'common_intents': list(intents_used),
            'interaction_count': len(history)
        }
    
    def suggest_followup_questions(self, session_id, last_response):
        """Suggest relevant follow-up questions"""
        if session_id not in self.sessions:
            return []
        
        summary = self.get_conversation_summary(session_id)
        if not summary:
            return []
        
        suggestions = []
        response_type = last_response.get('type', '')
        
        # Suggestions based on last response type
        if response_type == 'city':
            if summary['cities_discussed']:
                city = summary['cities_discussed'][0]
                suggestions.extend([
                    f"Show me the trend for {city}",
                    f"Compare {city} with another city",
                    f"Gender breakdown for {city}"
                ])
        
        elif response_type == 'multi_city':
            suggestions.extend([
                "Show me the trend over time",
                "What about juvenile crime?",
                "Gender-wise comparison"
            ])
        
        elif response_type == 'trend_analysis':
            if summary['cities_discussed']:
                suggestions.extend([
                    "What caused this trend?",
                    "Compare with national average",
                    "Show me other cities with similar patterns"
                ])
        
        elif response_type.startswith('top_'):
            suggestions.extend([
                "What about the bottom cities?",
                "Show me the trend for top cities",
                "Gender breakdown for these cities"
            ])
        
        # Generic suggestions if no specific ones
        if not suggestions:
            suggestions = [
                "Show me more details",
                "What about other years?",
                "Compare with different cities"
            ]
        
        return suggestions[:3]
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time - session['last_activity'] > self.context_ttl
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]


# Global context manager
conversation_context = ConversationContext()