"""
Chatbot Performance Analytics and Monitoring
"""
import time
import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta


class ChatbotAnalytics:
    """Track and analyze chatbot performance and usage patterns"""
    
    def __init__(self):
        self.metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'error_queries': 0,
            'response_times': [],
            'query_types': Counter(),
            'popular_cities': Counter(),
            'popular_years': Counter(),
            'user_satisfaction': [],
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        self.daily_stats = defaultdict(lambda: {
            'queries': 0,
            'errors': 0,
            'avg_response_time': 0,
            'unique_users': set()
        })
        
        self.query_patterns = defaultdict(int)
        self.error_patterns = defaultdict(int)
    
    def log_query(self, query, extracted_data, response, response_time, session_id, success=True):
        """Log query metrics"""
        self.metrics['total_queries'] += 1
        
        if success:
            self.metrics['successful_queries'] += 1
        else:
            self.metrics['error_queries'] += 1
        
        # Track response time
        self.metrics['response_times'].append(response_time)
        
        # Track query patterns
        intent = extracted_data.get('intent', 'unknown')
        self.metrics['query_types'][intent] += 1
        
        # Track popular entities
        cities = extracted_data.get('cities', [])
        years = extracted_data.get('years', [])
        
        for city in cities:
            self.metrics['popular_cities'][city] += 1
        
        for year in years:
            self.metrics['popular_years'][year] += 1
        
        # Daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        self.daily_stats[today]['queries'] += 1
        self.daily_stats[today]['unique_users'].add(session_id)
        
        if not success:
            self.daily_stats[today]['errors'] += 1
            error_type = response.get('type', 'unknown_error')
            self.error_patterns[error_type] += 1
        
        # Update average response time
        total_time = sum(self.metrics['response_times'])
        self.daily_stats[today]['avg_response_time'] = total_time / len(self.metrics['response_times'])
    
    def log_cache_hit(self, hit=True):
        """Log cache performance"""
        if hit:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
    
    def get_performance_summary(self):
        """Get comprehensive performance summary"""
        total_queries = self.metrics['total_queries']
        if total_queries == 0:
            return {"message": "No queries processed yet"}
        
        success_rate = (self.metrics['successful_queries'] / total_queries) * 100
        avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        
        cache_total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = (self.metrics['cache_hits'] / cache_total * 100) if cache_total > 0 else 0
        
        return {
            'overview': {
                'total_queries': total_queries,
                'success_rate': f"{success_rate:.1f}%",
                'error_rate': f"{(100 - success_rate):.1f}%",
                'avg_response_time': f"{avg_response_time:.2f}s",
                'cache_hit_rate': f"{cache_hit_rate:.1f}%"
            },
            'popular_queries': dict(self.metrics['query_types'].most_common(5)),
            'popular_cities': dict(self.metrics['popular_cities'].most_common(5)),
            'popular_years': dict(self.metrics['popular_years'].most_common(3)),
            'common_errors': dict(self.error_patterns.most_common(3)),
            'performance_trends': self._get_performance_trends()
        }
    
    def _get_performance_trends(self):
        """Analyze performance trends over time"""
        if len(self.daily_stats) < 2:
            return {"message": "Insufficient data for trend analysis"}
        
        # Get last 7 days
        recent_days = sorted(self.daily_stats.keys())[-7:]
        
        trends = {
            'daily_queries': [],
            'daily_errors': [],
            'daily_response_times': [],
            'daily_unique_users': []
        }
        
        for day in recent_days:
            stats = self.daily_stats[day]
            trends['daily_queries'].append({
                'date': day,
                'queries': stats['queries']
            })
            trends['daily_errors'].append({
                'date': day,
                'errors': stats['errors']
            })
            trends['daily_response_times'].append({
                'date': day,
                'avg_time': stats['avg_response_time']
            })
            trends['daily_unique_users'].append({
                'date': day,
                'users': len(stats['unique_users'])
            })
        
        return trends
    
    def get_optimization_recommendations(self):
        """Generate optimization recommendations"""
        recommendations = []
        
        # Response time analysis
        avg_time = sum(self.metrics['response_times']) / len(self.metrics['response_times']) if self.metrics['response_times'] else 0
        if avg_time > 2.0:
            recommendations.append({
                'type': 'performance',
                'priority': 'high',
                'issue': 'Slow response times',
                'recommendation': 'Implement more aggressive caching for popular queries',
                'current_value': f"{avg_time:.2f}s",
                'target_value': '<2.0s'
            })
        
        # Error rate analysis
        total_queries = self.metrics['total_queries']
        error_rate = (self.metrics['error_queries'] / total_queries * 100) if total_queries > 0 else 0
        if error_rate > 15:
            recommendations.append({
                'type': 'accuracy',
                'priority': 'high',
                'issue': 'High error rate',
                'recommendation': 'Improve query preprocessing and validation',
                'current_value': f"{error_rate:.1f}%",
                'target_value': '<10%'
            })
        
        # Cache performance
        cache_total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = (self.metrics['cache_hits'] / cache_total * 100) if cache_total > 0 else 0
        if cache_hit_rate < 60:
            recommendations.append({
                'type': 'caching',
                'priority': 'medium',
                'issue': 'Low cache hit rate',
                'recommendation': 'Optimize cache key generation and increase cache size',
                'current_value': f"{cache_hit_rate:.1f}%",
                'target_value': '>70%'
            })
        
        # Popular query optimization
        top_queries = self.metrics['query_types'].most_common(3)
        if top_queries:
            recommendations.append({
                'type': 'optimization',
                'priority': 'low',
                'issue': 'Popular query patterns identified',
                'recommendation': f"Pre-compute results for: {', '.join([q[0] for q in top_queries])}",
                'current_value': f"Top query: {top_queries[0][0]} ({top_queries[0][1]} times)",
                'target_value': 'Pre-cached responses'
            })
        
        return recommendations
    
    def export_analytics_data(self, format='json'):
        """Export analytics data for external analysis"""
        data = {
            'metrics': dict(self.metrics),
            'daily_stats': {k: {**v, 'unique_users': len(v['unique_users'])} for k, v in self.daily_stats.items()},
            'query_patterns': dict(self.query_patterns),
            'error_patterns': dict(self.error_patterns),
            'export_timestamp': datetime.now().isoformat()
        }
        
        # Convert Counter objects to regular dicts
        data['metrics']['query_types'] = dict(data['metrics']['query_types'])
        data['metrics']['popular_cities'] = dict(data['metrics']['popular_cities'])
        data['metrics']['popular_years'] = dict(data['metrics']['popular_years'])
        
        if format == 'json':
            return json.dumps(data, indent=2)
        
        return data


# Global analytics instance
chatbot_analytics = ChatbotAnalytics()