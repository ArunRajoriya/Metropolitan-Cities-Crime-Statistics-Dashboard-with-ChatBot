#!/usr/bin/env python3
"""
Test script for Bangalore trend analysis fixes
"""

import requests
import json

def test_bangalore_trend_fixes():
    """Test that Bangalore trend queries now work properly"""
    
    base_url = "http://127.0.0.1:5000"
    
    test_cases = [
        {
            "name": "Bangalore trend from 2016 to 2020",
            "query": "Show me the trend for Bangalore from 2016 to 2020",
            "expected_success": True,
            "expected_type": "city_trend"
        },
        {
            "name": "Bangalore trend without years",
            "query": "Show me the trend for Bangalore",
            "expected_success": True,
            "expected_type": "city_trend"
        },
        {
            "name": "Bangalore trend from 2016",
            "query": "Show me the trend for Bangalore from 2016",
            "expected_success": True,
            "expected_type": "city_trend"
        },
        {
            "name": "Bengaluru trend (alternate spelling)",
            "query": "Bengaluru trend analysis",
            "expected_success": True,
            "expected_type": "city_trend"
        }
    ]
    
    print("🧪 Testing Bangalore Trend Analysis Fixes")
    print("=" * 70)
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Query: '{test_case['query']}'")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"message": test_case['query']},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                response_type = data.get("type", "unknown")
                
                # Check if it's an error (old behavior)
                if data.get("type") in ["error", "clarification"]:
                    print("   ❌ FAIL: Still showing error/clarification")
                    print(f"   📝 Message: {data.get('summary', 'No message')}")
                
                # Check if it provides trend data (new behavior)
                elif response_type == test_case["expected_type"] or "trend" in response_type:
                    print("   ✅ SUCCESS: Providing trend analysis")
                    print(f"   📊 Type: {response_type}")
                    print(f"   📝 Title: {data.get('title', 'No title')}")
                    
                    # Check if data is present
                    if data.get("data"):
                        years = list(data["data"].keys())
                        print(f"   📅 Years: {', '.join(sorted(years))}")
                        
                        # Check values
                        values = list(data["data"].values())
                        if all(isinstance(v, (int, float)) and v > 0 for v in values):
                            print(f"   📈 Values: {[f'{v:,}' for v in values]}")
                        else:
                            print(f"   ⚠️  Values: {values}")
                    
                    # Check insight
                    if data.get("insight"):
                        print(f"   💡 Insight: {data['insight'][:80]}...")
                    
                    passed += 1
                
                else:
                    print(f"   ⚠️  UNEXPECTED: Got type '{response_type}'")
                    print(f"   📝 Title: {data.get('title', 'No title')}")
            
            else:
                print(f"   ❌ HTTP ERROR: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 70)
    print(f"🏁 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Bangalore trend analysis is now working!")
    elif passed >= total * 0.75:
        print("✅ Most tests passed! Significant improvement achieved.")
    else:
        print("⚠️  Some issues remain. Check failed tests above.")
    
    return passed == total

if __name__ == "__main__":
    test_bangalore_trend_fixes()