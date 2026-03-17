"""
Advanced Query Processor - Handle complex and natural language queries
"""
import re
from services.data_loader import crime_data, gov_data, foreign_data
from services.analytics_engine import calculate_city_totals
from services.advanced_analytics import analyze_gender_gap, compare_with_average, get_percentile_rank
from services.response_formatter import format_number


class AdvancedQueryProcessor:
    """Process complex natural language queries with advanced analytics"""
    
    def __init__(self):
        self.query_patterns = self._initialize_patterns()
        self.context_memory = {}
    
    def _initialize_patterns(self):
        """Initialize advanced query patterns"""
        return {
            # Statistical queries
            'correlation': r'correlat|relationship|connect|link',
            'pattern': r'pattern|trend|behavior|insight',
            'prediction': r'predict|forecast|future|expect',
            'comparison': r'compare|versus|vs|against|difference',
            'ranking': r'rank|order|sort|arrange|list',
            'aggregation': r'total|sum|average|mean|median',
            
            # Natural language patterns
            'question_words': r'what|which|who|where|when|how|why',
            'superlatives': r'most|least|highest|lowest|best|worst',
            'temporal': r'over time|across years|year by year|annually',
            'geographical': r'across cities|city wise|regional|state wise',
            
            # Complex operations
            'filtering': r'only|excluding|without|except|filter',
            'grouping': r'group by|categorize|classify|segment',
            'calculation': r'calculate|compute|determine|find out'
        }
    
    def process_advanced_query(self, message, structured):
        """Process advanced queries that require complex analysis"""
        
        # Handle generic trend analysis queries with smart defaults
        if self._is_generic_trend_query(message, structured):
            return self._handle_generic_trend_analysis(message, structured)
        
        # Check for statistical operations
        if self._matches_pattern(message, 'correlation'):
            return self._handle_correlation_query(message, structured)
        
        if self._matches_pattern(message, 'pattern'):
            return self._handle_pattern_analysis(message, structured)
        
        if self._matches_pattern(message, 'prediction'):
            return self._handle_prediction_query(message, structured)
        
        # Check for complex comparisons
        if self._matches_pattern(message, 'comparison') and len(structured.get('cities', [])) > 2:
            return self._handle_multi_city_comparison(message, structured)
        
        # Check for advanced ranking
        if self._matches_pattern(message, 'ranking'):
            return self._handle_advanced_ranking(message, structured)
        
        # Check for aggregation queries
        if self._matches_pattern(message, 'aggregation'):
            return self._handle_aggregation_query(message, structured)
        
        # Check for natural language questions
        if self._matches_pattern(message, 'question_words'):
            return self._handle_natural_question(message, structured)
        
        return None
    
    def _matches_pattern(self, message, pattern_name):
        """Check if message matches a specific pattern"""
        pattern = self.query_patterns.get(pattern_name, '')
        return bool(re.search(pattern, message.lower()))
    
    def _is_generic_trend_query(self, message, structured):
        """Check if this is a generic trend query that needs smart defaults"""
        message_lower = message.lower()
        
        # Generic trend patterns
        generic_patterns = [
            r'^show me.*trend',
            r'^trend analysis',
            r'^what.*trend',
            r'^display.*trend',
            r'^give me.*trend'
        ]
        
        # Check if it matches generic patterns and has no specific cities
        is_generic = any(re.search(pattern, message_lower) for pattern in generic_patterns)
        has_no_cities = not structured.get('cities', [])
        
        return is_generic and has_no_cities
    
    def _handle_generic_trend_analysis(self, message, structured):
        """Handle generic trend analysis with smart defaults"""
        years = structured.get('years', [])
        gender = structured.get('gender')
        
        # Use all available years if none specified
        if not years:
            years = sorted(crime_data.keys())
        
        # Provide comprehensive trend analysis
        analysis_data = {
            "national_trend": self._get_national_trend(years, gender),
            "top_cities_trend": self._get_top_cities_trend(years, gender),
            "regional_insights": self._get_regional_insights(years, gender)
        }
        
        # Generate comprehensive insight
        insight = self._generate_comprehensive_trend_insight(analysis_data, years, gender)
        
        return {
            "type": "comprehensive_trend_analysis",
            "title": f"Comprehensive {gender.title() + ' ' if gender else ''}Crime Trend Analysis",
            "data": analysis_data,
            "insight": insight,
            "source": "NCRB Dataset - Advanced Trend Analysis"
        }
    
    def _get_national_trend(self, years, gender):
        """Get national level trend data"""
        national_data = {}
        
        for year in years:
            if year in crime_data:
                df = crime_data[year]
                df = df[df["City"].notna()]
                df = df[~df["City"].str.lower().str.contains("total", na=False)]
                
                total = sum(
                    calculate_city_totals(row.to_dict(), gender)
                    for _, row in df.iterrows()
                )
                national_data[year] = int(total)
        
        return national_data
    
    def _get_top_cities_trend(self, years, gender):
        """Get trend data for top 5 cities"""
        # Find top cities from latest year
        latest_year = sorted(years)[-1] if years else "2020"
        
        if latest_year in crime_data:
            df = crime_data[latest_year]
            df = df[df["City"].notna()]
            df = df[~df["City"].str.lower().str.contains("total", na=False)]
            
            city_totals = {}
            for _, row in df.iterrows():
                city = row["City"]
                total = calculate_city_totals(row.to_dict(), gender)
                city_totals[city] = int(total)
            
            # Get top 5 cities
            top_cities = sorted(city_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            top_city_names = [city for city, _ in top_cities]
            
            # Get trend for these cities
            trend_data = {}
            for city in top_city_names:
                city_data = {}
                for year in years:
                    if year in crime_data:
                        df = crime_data[year]
                        import re
                        city_escaped = re.escape(city)
                        row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]
                        if not row.empty:
                            total = calculate_city_totals(row.iloc[0].to_dict(), gender)
                            city_data[year] = int(total)
                
                if city_data:
                    trend_data[city] = city_data
            
            return trend_data
        
        return {}
    
    def _get_regional_insights(self, years, gender):
        """Get regional insights and patterns"""
        insights = {
            "growth_leaders": [],
            "decline_leaders": [],
            "stable_cities": []
        }
        
        if len(years) >= 2:
            first_year = sorted(years)[0]
            last_year = sorted(years)[-1]
            
            if first_year in crime_data and last_year in crime_data:
                # Compare first and last year
                df_first = crime_data[first_year]
                df_last = crime_data[last_year]
                
                # Filter out totals
                df_first = df_first[df_first["City"].notna()]
                df_first = df_first[~df_first["City"].str.lower().str.contains("total", na=False)]
                df_last = df_last[df_last["City"].notna()]
                df_last = df_last[~df_last["City"].str.lower().str.contains("total", na=False)]
                
                city_changes = {}
                
                for _, row_first in df_first.iterrows():
                    city = row_first["City"]
                    import re
                    city_escaped = re.escape(city)
                    row_last = df_last[df_last["City"].str.contains(city_escaped, case=False, na=False, regex=True)]
                    
                    if not row_last.empty:
                        first_val = calculate_city_totals(row_first.to_dict(), gender)
                        last_val = calculate_city_totals(row_last.iloc[0].to_dict(), gender)
                        
                        if first_val > 0:
                            change_pct = ((last_val - first_val) / first_val * 100)
                            city_changes[city] = change_pct
                
                # Categorize cities
                for city, change in city_changes.items():
                    if change > 20:
                        insights["growth_leaders"].append({"city": city, "change": f"+{change:.1f}%"})
                    elif change < -20:
                        insights["decline_leaders"].append({"city": city, "change": f"{change:.1f}%"})
                    elif abs(change) <= 10:
                        insights["stable_cities"].append({"city": city, "change": f"{change:+.1f}%"})
                
                # Sort and limit
                insights["growth_leaders"] = sorted(insights["growth_leaders"], 
                                                  key=lambda x: float(x["change"].replace("+", "").replace("%", "")), 
                                                  reverse=True)[:3]
                insights["decline_leaders"] = sorted(insights["decline_leaders"], 
                                                   key=lambda x: float(x["change"].replace("%", "")))[:3]
                insights["stable_cities"] = insights["stable_cities"][:3]
        
        return insights
    
    def _generate_comprehensive_trend_insight(self, analysis_data, years, gender):
        """Generate comprehensive insight from trend analysis"""
        insights = []
        
        # National trend insight
        national_data = analysis_data["national_trend"]
        if len(national_data) >= 2:
            years_sorted = sorted(national_data.keys())
            first_val = national_data[years_sorted[0]]
            last_val = national_data[years_sorted[-1]]
            change_pct = ((last_val - first_val) / first_val * 100) if first_val > 0 else 0
            
            direction = "increased" if change_pct > 0 else "decreased" if change_pct < 0 else "remained stable"
            insights.append(f"National {gender.lower() if gender else ''}arrests {direction} by {abs(change_pct):.1f}% from {years_sorted[0]} to {years_sorted[-1]}")
        
        # Regional insights
        regional = analysis_data["regional_insights"]
        if regional["growth_leaders"]:
            top_grower = regional["growth_leaders"][0]
            insights.append(f"{top_grower['city']} shows highest growth ({top_grower['change']})")
        
        if regional["decline_leaders"]:
            top_decliner = regional["decline_leaders"][0]
            insights.append(f"{top_decliner['city']} shows steepest decline ({top_decliner['change']})")
        
        return ". ".join(insights) + "." if insights else "Comprehensive trend analysis completed."
    
    def _handle_correlation_query(self, message, structured):
        """Handle correlation and relationship queries"""
        cities = structured.get('cities', [])
        years = structured.get('years', [])
        
        if len(cities) >= 2 and len(years) >= 2:
            # Multi-dimensional correlation analysis
            correlation_data = {}
            
            for city in cities[:3]:  # Limit to 3 cities for clarity
                city_data = {}
                for year in years:
                    if year in crime_data:
                        df = crime_data[year]
                        import re
                        city_escaped = re.escape(city)
                        row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]
                        if not row.empty:
                            total = calculate_city_totals(row.iloc[0].to_dict(), structured.get('gender'))
                            city_data[year] = int(total)
                
                if city_data:
                    correlation_data[city] = city_data
            
            if correlation_data:
                # Calculate correlation insights
                insights = self._generate_correlation_insights(correlation_data)
                
                return {
                    "type": "correlation_analysis",
                    "title": "Crime Correlation Analysis",
                    "data": correlation_data,
                    "insight": insights,
                    "source": "NCRB Dataset - Advanced Analytics"
                }
        
        return None
    
    def _handle_pattern_analysis(self, message, structured):
        """Handle pattern recognition queries"""
        cities = structured.get('cities', [])
        years = structured.get('years', [])
        
        if cities and len(years) >= 2:
            city = cities[0]
            pattern_data = {}
            
            for year in sorted(years):
                if year in crime_data:
                    df = crime_data[year]
                    import re
                    city_escaped = re.escape(city)
                    row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]
                    if not row.empty:
                        total = calculate_city_totals(row.iloc[0].to_dict(), structured.get('gender'))
                        pattern_data[year] = int(total)
            
            if len(pattern_data) >= 2:
                patterns = self._analyze_patterns(pattern_data)
                
                return {
                    "type": "pattern_analysis",
                    "title": f"Crime Pattern Analysis - {city}",
                    "data": pattern_data,
                    "patterns": patterns,
                    "insight": self._generate_pattern_insights(city, pattern_data, patterns),
                    "source": "NCRB Dataset - Pattern Recognition"
                }
        
        return None
    
    def _handle_prediction_query(self, message, structured):
        """Handle prediction and forecasting queries"""
        cities = structured.get('cities', [])
        years = structured.get('years', [])
        
        if cities and len(years) >= 2:
            city = cities[0]
            historical_data = {}
            
            for year in sorted(years):
                if year in crime_data:
                    df = crime_data[year]
                    import re
                    city_escaped = re.escape(city)
                    row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]
                    if not row.empty:
                        total = calculate_city_totals(row.iloc[0].to_dict(), structured.get('gender'))
                        historical_data[year] = int(total)
            
            if len(historical_data) >= 2:
                prediction = self._simple_prediction(historical_data)
                
                return {
                    "type": "prediction_analysis",
                    "title": f"Crime Trend Prediction - {city}",
                    "data": {
                        "Historical Data": historical_data,
                        "Predicted Trend": prediction['trend'],
                        "Confidence Level": prediction['confidence']
                    },
                    "insight": prediction['insight'],
                    "source": "NCRB Dataset - Predictive Analytics"
                }
        
        return None
    
    def _handle_multi_city_comparison(self, message, structured):
        """Handle complex multi-city comparisons"""
        cities = structured.get('cities', [])
        years = structured.get('years', [])
        
        if len(cities) >= 3:
            year = years[0] if years else "2020"
            
            if year in crime_data:
                df = crime_data[year]
                comparison_data = {}
                
                for city in cities[:5]:  # Limit to 5 cities
                    import re
                    city_escaped = re.escape(city)
                    row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]
                    if not row.empty:
                        total = calculate_city_totals(row.iloc[0].to_dict(), structured.get('gender'))
                        comparison_data[city] = int(total)
                
                if len(comparison_data) >= 3:
                    analysis = self._advanced_comparison_analysis(comparison_data)
                    
                    return {
                        "type": "multi_city_analysis",
                        "title": f"Advanced City Comparison - {year}",
                        "data": comparison_data,
                        "analysis": analysis,
                        "insight": self._generate_comparison_insights(comparison_data, analysis),
                        "source": "NCRB Dataset - Multi-City Analytics"
                    }
        
        return None
    
    def _handle_advanced_ranking(self, message, structured):
        """Handle advanced ranking queries"""
        years = structured.get('years', [])
        gender = structured.get('gender')
        
        year = years[0] if years else "2020"
        
        if year in crime_data:
            df = crime_data[year]
            df = df[df["City"].notna()]
            df = df[~df["City"].str.lower().str.contains("total", na=False)]
            
            rankings = []
            for _, row in df.iterrows():
                city = row["City"]
                total = calculate_city_totals(row.to_dict(), gender)
                
                # Get additional metrics
                percentile = get_percentile_rank(city, year, gender)
                comparison = compare_with_average(city, year, gender)
                
                rankings.append({
                    "city": city,
                    "arrests": int(total),
                    "percentile": percentile,
                    "vs_average": comparison['status'] if comparison else "N/A",
                    "difference_pct": comparison['percentage_difference'] if comparison else 0
                })
            
            # Sort by arrests
            rankings.sort(key=lambda x: x["arrests"], reverse=True)
            
            # Add rank numbers
            for i, item in enumerate(rankings, 1):
                item["rank"] = i
            
            return {
                "type": "advanced_ranking",
                "title": f"Advanced City Rankings - {year}",
                "data": rankings[:10],  # Top 10
                "insight": self._generate_ranking_insights(rankings[:10]),
                "source": "NCRB Dataset - Advanced Rankings"
            }
        
        return None
    
    def _handle_aggregation_query(self, message, structured):
        """Handle aggregation and statistical queries"""
        years = structured.get('years', [])
        gender = structured.get('gender')
        
        if not years:
            years = list(crime_data.keys())
        
        aggregated_data = {}
        
        for year in years:
            if year in crime_data:
                df = crime_data[year]
                df = df[df["City"].notna()]
                df = df[~df["City"].str.lower().str.contains("total", na=False)]
                
                totals = []
                for _, row in df.iterrows():
                    total = calculate_city_totals(row.to_dict(), gender)
                    totals.append(total)
                
                if totals:
                    aggregated_data[year] = {
                        "total": sum(totals),
                        "average": sum(totals) / len(totals),
                        "median": sorted(totals)[len(totals)//2],
                        "max": max(totals),
                        "min": min(totals),
                        "cities_count": len(totals)
                    }
        
        if aggregated_data:
            return {
                "type": "aggregation_analysis",
                "title": "Statistical Aggregation Analysis",
                "data": aggregated_data,
                "insight": self._generate_aggregation_insights(aggregated_data),
                "source": "NCRB Dataset - Statistical Analysis"
            }
        
        return None
    
    def _handle_natural_question(self, message, structured):
        """Handle natural language questions"""
        message_lower = message.lower()
        
        # "Which city has the most/least crime?"
        if re.search(r'which city.*most|which city.*highest', message_lower):
            return self._find_extreme_city(structured, "highest")
        
        if re.search(r'which city.*least|which city.*lowest', message_lower):
            return self._find_extreme_city(structured, "lowest")
        
        # "How many cities have more than X arrests?"
        threshold_match = re.search(r'how many cities.*more than (\d+)', message_lower)
        if threshold_match:
            threshold = int(threshold_match.group(1))
            return self._count_cities_above_threshold(structured, threshold)
        
        # "What percentage of cities have high crime?"
        if re.search(r'what percentage.*cities.*high', message_lower):
            return self._calculate_high_crime_percentage(structured)
        
        return None
    
    def _find_extreme_city(self, structured, extreme_type):
        """Find city with highest or lowest crime"""
        years = structured.get('years', [])
        gender = structured.get('gender')
        
        year = years[0] if years else "2020"
        
        if year in crime_data:
            df = crime_data[year]
            df = df[df["City"].notna()]
            df = df[~df["City"].str.lower().str.contains("total", na=False)]
            
            city_totals = {}
            for _, row in df.iterrows():
                city = row["City"]
                total = calculate_city_totals(row.to_dict(), gender)
                city_totals[city] = int(total)
            
            if city_totals:
                if extreme_type == "highest":
                    extreme_city = max(city_totals.items(), key=lambda x: x[1])
                else:
                    extreme_city = min(city_totals.items(), key=lambda x: x[1])
                
                city_name, arrests = extreme_city
                
                return {
                    "type": "extreme_city",
                    "title": f"City with {extreme_type.title()} Crime Rate - {year}",
                    "data": {city_name: arrests},
                    "insight": f"{city_name} has the {extreme_type} number of arrests ({format_number(arrests)}) in {year}.",
                    "source": "NCRB Dataset"
                }
        
        return None
    
    # Helper methods for analysis
    def _generate_correlation_insights(self, correlation_data):
        """Generate insights from correlation analysis"""
        insights = []
        
        for city, data in correlation_data.items():
            years = sorted(data.keys())
            if len(years) >= 2:
                first_val = data[years[0]]
                last_val = data[years[-1]]
                change_pct = ((last_val - first_val) / first_val * 100) if first_val > 0 else 0
                
                if abs(change_pct) > 20:
                    direction = "increased" if change_pct > 0 else "decreased"
                    insights.append(f"{city} shows strong {direction} trend ({abs(change_pct):.1f}%)")
        
        return ". ".join(insights) if insights else "No strong correlations detected in the data."
    
    def _analyze_patterns(self, pattern_data):
        """Analyze patterns in time series data"""
        years = sorted(pattern_data.keys())
        values = [pattern_data[year] for year in years]
        
        patterns = {
            "trend": "stable",
            "volatility": "low",
            "growth_rate": 0
        }
        
        if len(values) >= 2:
            # Calculate trend
            first_val = values[0]
            last_val = values[-1]
            growth_rate = ((last_val - first_val) / first_val * 100) if first_val > 0 else 0
            
            patterns["growth_rate"] = round(growth_rate, 1)
            
            if growth_rate > 10:
                patterns["trend"] = "increasing"
            elif growth_rate < -10:
                patterns["trend"] = "decreasing"
            
            # Calculate volatility
            if len(values) >= 3:
                changes = [abs(values[i] - values[i-1]) / values[i-1] * 100 for i in range(1, len(values)) if values[i-1] > 0]
                avg_change = sum(changes) / len(changes) if changes else 0
                
                if avg_change > 20:
                    patterns["volatility"] = "high"
                elif avg_change > 10:
                    patterns["volatility"] = "medium"
        
        return patterns
    
    def _generate_pattern_insights(self, city, pattern_data, patterns):
        """Generate insights from pattern analysis"""
        trend = patterns["trend"]
        volatility = patterns["volatility"]
        growth_rate = patterns["growth_rate"]
        
        insight = f"{city} shows a {trend} crime pattern"
        
        if growth_rate != 0:
            direction = "increase" if growth_rate > 0 else "decrease"
            insight += f" with {abs(growth_rate):.1f}% {direction}"
        
        insight += f" and {volatility} volatility over the analyzed period."
        
        return insight
    
    def _simple_prediction(self, historical_data):
        """Simple linear prediction based on historical data"""
        years = sorted(historical_data.keys())
        values = [historical_data[year] for year in years]
        
        if len(values) >= 2:
            # Simple linear trend
            first_val = values[0]
            last_val = values[-1]
            avg_change = (last_val - first_val) / (len(values) - 1)
            
            # Predict next value
            next_year = str(int(years[-1]) + 1)
            predicted_value = last_val + avg_change
            
            # Determine confidence based on consistency
            changes = [values[i] - values[i-1] for i in range(1, len(values))]
            consistency = 1 - (max(changes) - min(changes)) / (max(values) - min(values)) if max(values) != min(values) else 1
            confidence = max(0.3, min(0.9, consistency))
            
            trend = "increasing" if avg_change > 0 else "decreasing" if avg_change < 0 else "stable"
            
            return {
                "trend": trend,
                "predicted_value": int(max(0, predicted_value)),
                "confidence": f"{confidence*100:.0f}%",
                "insight": f"Based on historical trends, crime is expected to {trend} with {confidence*100:.0f}% confidence."
            }
        
        return {
            "trend": "insufficient_data",
            "confidence": "0%",
            "insight": "Insufficient historical data for reliable prediction."
        }
    
    def _advanced_comparison_analysis(self, comparison_data):
        """Perform advanced analysis on comparison data"""
        values = list(comparison_data.values())
        
        analysis = {
            "total": sum(values),
            "average": sum(values) / len(values),
            "median": sorted(values)[len(values)//2],
            "range": max(values) - min(values),
            "std_dev": self._calculate_std_dev(values),
            "outliers": self._find_outliers(comparison_data)
        }
        
        return analysis
    
    def _calculate_std_dev(self, values):
        """Calculate standard deviation"""
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _find_outliers(self, data):
        """Find outlier cities"""
        values = list(data.values())
        mean = sum(values) / len(values)
        std_dev = self._calculate_std_dev(values)
        
        outliers = []
        for city, value in data.items():
            if abs(value - mean) > 2 * std_dev:
                outliers.append(city)
        
        return outliers
    
    def _generate_comparison_insights(self, comparison_data, analysis):
        """Generate insights from comparison analysis"""
        outliers = analysis["outliers"]
        range_val = analysis["range"]
        
        insight = f"Analysis of {len(comparison_data)} cities shows "
        
        if outliers:
            insight += f"significant variation with {', '.join(outliers)} as outliers. "
        else:
            insight += "relatively consistent crime patterns. "
        
        insight += f"The range spans {format_number(range_val)} arrests, indicating "
        
        if range_val > analysis["average"]:
            insight += "high disparity between cities."
        else:
            insight += "moderate variation across cities."
        
        return insight
    
    def _generate_ranking_insights(self, rankings):
        """Generate insights from ranking analysis"""
        top_city = rankings[0]
        bottom_city = rankings[-1]
        
        insight = f"{top_city['city']} leads with {format_number(top_city['arrests'])} arrests "
        insight += f"(rank #{top_city['rank']}, {top_city['percentile']}th percentile), "
        insight += f"while {bottom_city['city']} has {format_number(bottom_city['arrests'])} arrests "
        insight += f"(rank #{bottom_city['rank']})."
        
        return insight
    
    def _generate_aggregation_insights(self, aggregated_data):
        """Generate insights from aggregation analysis"""
        if len(aggregated_data) == 1:
            year, data = list(aggregated_data.items())[0]
            insight = f"In {year}, {data['cities_count']} cities reported a total of "
            insight += f"{format_number(data['total'])} arrests with an average of "
            insight += f"{format_number(int(data['average']))} per city."
        else:
            years = sorted(aggregated_data.keys())
            first_year = years[0]
            last_year = years[-1]
            
            first_total = aggregated_data[first_year]['total']
            last_total = aggregated_data[last_year]['total']
            change_pct = ((last_total - first_total) / first_total * 100) if first_total > 0 else 0
            
            direction = "increased" if change_pct > 0 else "decreased"
            insight = f"From {first_year} to {last_year}, total arrests {direction} by "
            insight += f"{abs(change_pct):.1f}% from {format_number(first_total)} to {format_number(last_total)}."
        
        return insight


# Global instance
advanced_processor = AdvancedQueryProcessor()