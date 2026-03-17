# Chatbot Usage Guide

## Quick Start

The enhanced chatbot can now understand natural language queries and provide intelligent responses. Here's how to use it:

## Basic Query Patterns

### 1. City-Specific Queries
```
"Show arrests in Delhi 2020"
"How many arrests in Mumbai?"
"Delhi arrests"
"What about Bangalore 2019?"
```

### 2. Gender-Specific Queries
```
"Male arrests in Delhi 2020"
"Female arrests Mumbai"
"Show me women arrests in Bangalore"
"Men vs women arrests in Chennai"
```

### 3. Comparison Queries
```
"Compare Delhi and Mumbai 2020"
"Delhi vs Mumbai vs Kolkata"
"Compare male and female arrests in Delhi"
"Show me Delhi and Mumbai side by side"
```

### 4. Ranking Queries
```
"Top 5 cities by arrests"
"Top 10 cities 2020"
"Highest arrest city"
"Lowest crime city"
"Which city has most arrests?"
"Show me city rankings"
```

### 5. Trend Analysis
```
"Show trend for Delhi from 2016 to 2020"
"Delhi arrests over time"
"How did Mumbai change from 2016 to 2020?"
"Year over year growth in Bangalore"
"Trend analysis for Chennai"
```

### 6. Statistical Queries
```
"What's the average arrests in 2020?"
"Show statistics for Delhi"
"Percentile rank of Mumbai"
"Compare Delhi with national average"
"How does Bangalore rank?"
```

### 7. Gender Analysis
```
"Gender breakdown for Mumbai 2020"
"Male to female ratio in Delhi"
"Analyze gender gap in Bangalore"
"Show me gender statistics for Chennai"
```

### 8. Juvenile Queries
```
"Juvenile arrests in Delhi 2020"
"Minor crime in Mumbai"
"Child arrests Bangalore"
"Top 3 cities for juvenile crime"
"Boys vs girls arrests in Delhi"
```

### 9. Government Data
```
"Government crime data 2020"
"National crime statistics"
"India total arrests"
"Show me government data"
```

### 10. Foreign Crime Queries
```
"Foreign crime 2020"
"Foreign tourists vs other foreigners 2019"
"Murder foreign crime 2020"
"Rape foreign crime 2019"
"Human trafficking foreign 2020"
"Foreign crime trend all years"
"Foreign crime 2019 vs 2020"
"Tourist crime breakdown 2020"
```

## Advanced Features

### Fuzzy Matching
The chatbot automatically corrects misspellings:
- "Deli" → Delhi
- "Mumbay" → Mumbai
- "Bangalor" → Bangalore
- "Chenai" → Chennai

### Time Range Extraction
Multiple ways to specify time ranges:
- "from 2016 to 2020"
- "between 2016 and 2020"
- "2016-2020"
- "2016 to 2020"

### Top N Extraction
Flexible ways to ask for rankings:
- "top 5 cities"
- "top 10"
- "first 3 cities"
- "5 highest"

### Clarification Requests
If your query is ambiguous, the chatbot will ask for clarification:
```
You: "Show me crime data"
Bot: "Your query is too general. Please specify a city, year, or type of information."
```

### Smart Suggestions
The chatbot provides context-aware suggestions:
```
You: "Deli arrests" (misspelled)
Bot: "Did you mean: Delhi, Dehradun, Daman?"
```

## Response Types

### 1. Simple Data Response
```json
{
  "type": "city",
  "title": "Total Arrests - Delhi (2020)",
  "data": {
    "Arrests": 45000
  },
  "insight": "Delhi recorded 45,000 arrests in 2020."
}
```

### 2. Comparison Response
```json
{
  "type": "multi_city",
  "title": "Total Arrest Comparison - 2020",
  "data": {
    "Delhi": 45000,
    "Mumbai": 52000
  },
  "insight": "Mumbai leads with 52,000 arrests..."
}
```

### 3. Trend Response
```json
{
  "type": "trend_analysis",
  "title": "Arrest Trend - Delhi (2016-2020)",
  "data": {
    "2016": 38000,
    "2019": 42000,
    "2020": 45000
  },
  "insight": "Arrests increased by 18.4%..."
}
```

### 4. Ranking Response
```json
{
  "type": "ranking",
  "title": "City Rankings by Arrests - 2020",
  "data": [
    {"rank": 1, "city": "Mumbai", "arrests": 52000},
    {"rank": 2, "city": "Delhi", "arrests": 45000}
  ]
}
```

### 5. Error Response with Suggestions
```json
{
  "type": "error",
  "summary": "City not found",
  "suggestions": [
    "Did you mean: Delhi, Dehradun?",
    "Try: 'Show arrests in Delhi 2020'"
  ]
}
```

## Tips for Best Results

### 1. Be Specific
✅ Good: "Show male arrests in Delhi 2020"
❌ Vague: "Show me data"

### 2. Use Natural Language
✅ Good: "Compare Delhi and Mumbai arrests in 2020"
✅ Good: "What are the arrests in Delhi?"
✅ Good: "Show me the trend for Bangalore"

### 3. Specify Time Periods
✅ Good: "Delhi arrests from 2016 to 2020"
✅ Good: "Show me 2020 data"

### 4. Use Keywords
Keywords that help: compare, trend, top, highest, lowest, male, female, juvenile, government, foreign

### 5. Ask Follow-up Questions
The chatbot provides suggestions for related queries you might want to ask.

## Common Use Cases

### Use Case 1: City Analysis
```
1. "Show arrests in Delhi 2020"
2. "Compare Delhi with national average"
3. "What's Delhi's percentile rank?"
4. "Gender breakdown for Delhi"
```

### Use Case 2: Multi-City Comparison
```
1. "Compare Delhi, Mumbai, and Bangalore 2020"
2. "Which city has highest arrests?"
3. "Show me top 5 cities"
```

### Use Case 3: Trend Analysis
```
1. "Show trend for Delhi from 2016 to 2020"
2. "How did arrests change over time?"
3. "Year over year growth"
```

### Use Case 4: Gender Analysis
```
1. "Male vs female arrests in Delhi"
2. "Gender breakdown for Mumbai"
3. "Male to female ratio"
```

## Troubleshooting

### Problem: "City not found"
**Solution:** Check spelling or try fuzzy matching. The bot will suggest similar cities.

### Problem: "Invalid year"
**Solution:** Available years are 2016, 2019, and 2020 only.

### Problem: "I couldn't understand the query"
**Solution:** Try rephrasing with more specific details (city, year, type of data).

### Problem: Low confidence response
**Solution:** The bot will ask for clarification. Provide more details.

## Examples by Complexity

### Beginner Level
- "Delhi arrests 2020"
- "Mumbai male arrests"
- "Top 5 cities"

### Intermediate Level
- "Compare Delhi and Mumbai arrests in 2020"
- "Show trend for Bangalore from 2016 to 2020"
- "Gender breakdown for Chennai 2019"

### Advanced Level
- "Compare Delhi, Mumbai, and Kolkata from 2016 to 2020"
- "Show me percentile rank and comparison with average for Delhi"
- "Analyze gender gap and trend for Bangalore"

## API Integration

### Making a Request
```python
import requests

response = requests.post('http://localhost:5000/chat', json={
    "message": "Compare Delhi and Mumbai arrests in 2020"
})

data = response.json()
print(data['insight'])
```

### Handling Responses
```python
if data['type'] == 'error':
    print("Error:", data['summary'])
    print("Suggestions:", data['suggestions'])
elif data['type'] == 'multi_city':
    print("Title:", data['title'])
    print("Data:", data['data'])
    print("Insight:", data['insight'])
```

## Best Practices

1. **Start Simple**: Begin with basic queries and build up to complex ones
2. **Use Suggestions**: Follow the bot's suggestions for related queries
3. **Check Responses**: Review the response type to understand what data you received
4. **Iterate**: If the first query doesn't work, rephrase based on error messages
5. **Explore**: Try different query patterns to discover all features

## Getting Help

If you're stuck, try:
- "What data do you have?"
- "Which years are available?"
- "Show me available cities"
- "Help"

The chatbot will provide information about available data and example queries.
