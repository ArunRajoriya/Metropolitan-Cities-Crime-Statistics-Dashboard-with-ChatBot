"""
Intelligent Cache Manager for Chatbot Performance
"""
import time
import hashlib
from functools import wraps


class ChatbotCache:
    """Smart caching system for chatbot responses"""
    
    def __init__(self, max_size=1000, ttl=3600):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
    
    def _generate_key(self, query_data):
        """Generate cache key from query parameters"""
        # Create a consistent hash from query components
        key_data = {
            'cities': sorted(query_data.get('cities', [])),
            'years': sorted(query_data.get('years', [])),
            'gender': query_data.get('gender', ''),
            'intent': query_data.get('intent', ''),
            'crime': query_data.get('crime', '')
        }
        key_string = str(sorted(key_data.items()))
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, query_data):
        """Get cached response if available and valid"""
        key = self._generate_key(query_data)
        
        if key in self.cache:
            cached_time, response = self.cache[key]
            
            # Check if cache is still valid
            if time.time() - cached_time < self.ttl:
                self.access_times[key] = time.time()
                return response
            else:
                # Remove expired cache
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
        
        return None
    
    def set(self, query_data, response):
        """Cache response with automatic cleanup"""
        key = self._generate_key(query_data)
        current_time = time.time()
        
        # Clean up if cache is full
        if len(self.cache) >= self.max_size:
            self._cleanup_old_entries()
        
        self.cache[key] = (current_time, response)
        self.access_times[key] = current_time
    
    def _cleanup_old_entries(self):
        """Remove least recently used entries"""
        # Sort by access time and remove oldest 20%
        sorted_keys = sorted(self.access_times.items(), key=lambda x: x[1])
        keys_to_remove = [k for k, _ in sorted_keys[:len(sorted_keys)//5]]
        
        for key in keys_to_remove:
            if key in self.cache:
                del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]


# Global cache instance
chatbot_cache = ChatbotCache()


def cache_response(func):
    """Decorator to cache chatbot responses"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract query data from arguments
        if len(args) > 0 and isinstance(args[0], dict):
            query_data = args[0]
            
            # Try to get from cache first
            cached_response = chatbot_cache.get(query_data)
            if cached_response:
                return cached_response
            
            # Execute function and cache result
            response = func(*args, **kwargs)
            if response and response.get('type') != 'error':
                chatbot_cache.set(query_data, response)
            
            return response
        
        return func(*args, **kwargs)
    
    return wrapper