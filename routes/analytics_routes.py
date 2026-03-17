"""
Analytics Routes for Chatbot Performance Monitoring
"""
from flask import Blueprint, jsonify, render_template_string
from services.chatbot_analytics import chatbot_analytics

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/chatbot/analytics")
def chatbot_performance():
    """Get chatbot performance analytics"""
    summary = chatbot_analytics.get_performance_summary()
    recommendations = chatbot_analytics.get_optimization_recommendations()
    
    return jsonify({
        "performance": summary,
        "recommendations": recommendations,
        "status": "success"
    })


@analytics_bp.route("/chatbot/analytics/dashboard")
def analytics_dashboard():
    """Simple analytics dashboard"""
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chatbot Analytics Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric { display: inline-block; margin: 10px 20px; text-align: center; }
            .metric-value { font-size: 2em; font-weight: bold; color: #3b82f6; }
            .metric-label { font-size: 0.9em; color: #666; }
            .recommendation { padding: 10px; margin: 10px 0; border-left: 4px solid #f59e0b; background: #fef3c7; }
            .high-priority { border-left-color: #ef4444; background: #fee2e2; }
            .medium-priority { border-left-color: #f59e0b; background: #fef3c7; }
            .low-priority { border-left-color: #10b981; background: #d1fae5; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f8f9fa; }
            .refresh-btn { background: #3b82f6; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Chatbot Analytics Dashboard</h1>
            <button class="refresh-btn" onclick="location.reload()">Refresh Data</button>
            
            <div class="card">
                <h2>Performance Overview</h2>
                <div id="metrics"></div>
            </div>
            
            <div class="card">
                <h2>Popular Queries</h2>
                <div id="popular-queries"></div>
            </div>
            
            <div class="card">
                <h2>Optimization Recommendations</h2>
                <div id="recommendations"></div>
            </div>
            
            <div class="card">
                <h2>Usage Patterns</h2>
                <div id="usage-patterns"></div>
            </div>
        </div>
        
        <script>
            async function loadAnalytics() {
                try {
                    const response = await fetch('/chatbot/analytics');
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        displayMetrics(data.performance.overview);
                        displayPopularQueries(data.performance);
                        displayRecommendations(data.recommendations);
                        displayUsagePatterns(data.performance);
                    }
                } catch (error) {
                    console.error('Failed to load analytics:', error);
                }
            }
            
            function displayMetrics(overview) {
                const metricsDiv = document.getElementById('metrics');
                metricsDiv.innerHTML = `
                    <div class="metric">
                        <div class="metric-value">${overview.total_queries || 0}</div>
                        <div class="metric-label">Total Queries</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${overview.success_rate || '0%'}</div>
                        <div class="metric-label">Success Rate</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${overview.avg_response_time || '0s'}</div>
                        <div class="metric-label">Avg Response Time</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${overview.cache_hit_rate || '0%'}</div>
                        <div class="metric-label">Cache Hit Rate</div>
                    </div>
                `;
            }
            
            function displayPopularQueries(performance) {
                const queriesDiv = document.getElementById('popular-queries');
                let html = '<table><tr><th>Query Type</th><th>Count</th></tr>';
                
                if (performance.popular_queries) {
                    Object.entries(performance.popular_queries).forEach(([query, count]) => {
                        html += `<tr><td>${query}</td><td>${count}</td></tr>`;
                    });
                }
                
                html += '</table>';
                queriesDiv.innerHTML = html;
            }
            
            function displayRecommendations(recommendations) {
                const recDiv = document.getElementById('recommendations');
                let html = '';
                
                if (recommendations && recommendations.length > 0) {
                    recommendations.forEach(rec => {
                        html += `
                            <div class="recommendation ${rec.priority}-priority">
                                <strong>${rec.issue}</strong><br>
                                ${rec.recommendation}<br>
                                <small>Current: ${rec.current_value} | Target: ${rec.target_value}</small>
                            </div>
                        `;
                    });
                } else {
                    html = '<p>No optimization recommendations at this time. Great job! 🎉</p>';
                }
                
                recDiv.innerHTML = html;
            }
            
            function displayUsagePatterns(performance) {
                const patternsDiv = document.getElementById('usage-patterns');
                let html = '<div style="display: flex; gap: 20px;">';
                
                // Popular cities
                if (performance.popular_cities) {
                    html += '<div><h3>Popular Cities</h3><ul>';
                    Object.entries(performance.popular_cities).forEach(([city, count]) => {
                        html += `<li>${city}: ${count} queries</li>`;
                    });
                    html += '</ul></div>';
                }
                
                // Popular years
                if (performance.popular_years) {
                    html += '<div><h3>Popular Years</h3><ul>';
                    Object.entries(performance.popular_years).forEach(([year, count]) => {
                        html += `<li>${year}: ${count} queries</li>`;
                    });
                    html += '</ul></div>';
                }
                
                html += '</div>';
                patternsDiv.innerHTML = html;
            }
            
            // Load analytics on page load
            loadAnalytics();
            
            // Auto-refresh every 30 seconds
            setInterval(loadAnalytics, 30000);
        </script>
    </body>
    </html>
    """
    
    return render_template_string(dashboard_html)


@analytics_bp.route("/chatbot/analytics/export")
def export_analytics():
    """Export analytics data"""
    data = chatbot_analytics.export_analytics_data()
    
    return jsonify({
        "data": data,
        "export_format": "json",
        "timestamp": chatbot_analytics.export_analytics_data(format='dict')['export_timestamp']
    })