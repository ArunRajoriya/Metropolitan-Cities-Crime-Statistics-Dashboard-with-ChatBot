#!/usr/bin/env python3
"""
Test script for crime suggestions functionality
"""

import requests
import json

def test_crime_suggestions():
    """Test that crime suggestions are returned as clickable options"""
    
    base_url = "http://127.0.0.1:5000"
    
    test_queries = [
        "2016",
        "2019", 
        "2020",
        "show me 2016 data",
        "government data 2019"
    ]
    
    print("🧪 Testing Crime Suggestions Functionality")
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
                
                # Check if it returns crime suggestions
                if data.get("type") == "crime_suggestions":
                    print("✅ SUCCESS: Returning crime suggestions")
                    print(f"   Title: {data.get('title', 'No title')}")
                    print(f"   Year: {data.get('year', 'No year')}")
                    
                    # Check if data contains crime list
                    if data.get("data") and isinstance(data["data"], list):
                        print(f"   Crime count: {len(data['data'])}")
                        print(f"   First few crimes: {data['data'][:3]}")
                    else:
                        print("   ❌ No crime data found")
                
                else:
                    print(f"⚠️  Got type '{data.get('type')}' instead of 'crime_suggestions'")
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
    test_crime_suggestions()