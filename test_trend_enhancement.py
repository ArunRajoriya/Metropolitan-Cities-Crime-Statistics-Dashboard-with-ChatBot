#!/usr/bin/env python3
"""
Test script for enhanced trend analysis functionality
"""

import requests
import json

def test_trend_queries():
    """Test various trend queries to ensure they work properly"""
    
    base_url = "http://127.0.0.1:5000"
    
    test_queries = [
        "Show me the trend analysis",
        "trend analysis", 
        "What's the trend?",
        "Display trend",
        "Give me trend analysis",
        "Show me arrest trends",
        "National trend analysis"
    ]
    
    print("🧪 Testing Enhanced Trend Analysis Functionality")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"message": query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if it's asking for clarification (old behavior)
                if data.get("type") == "clarification":
                    print("❌ FAILED: Still asking for clarification")
                    print(f"   Response: {data.get('summary', 'No summary')}")
                
                # Check if it provides trend data (new behavior)
                elif data.get("type") in ["multi_year_trend", "top_cities_trend", "comprehensive_trend_analysis"]:
                    print("✅ SUCCESS: Providing trend analysis")
                    print(f"   Type: {data.get('type')}")
                    print(f"   Title: {data.get('title', 'No title')}")
                    
                    # Check if data is present
                    if data.get("data"):
                        print(f"   Data keys: {list(data['data'].keys())}")
                    
                    # Check insight
                    if data.get("insight"):
                        print(f"   Insight: {data['insight'][:100]}...")
                
                else:
                    print(f"⚠️  UNEXPECTED: Got type '{data.get('type')}'")
                    print(f"   Title: {data.get('title', 'No title')}")
            
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ CONNECTION ERROR: {e}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_trend_queries()