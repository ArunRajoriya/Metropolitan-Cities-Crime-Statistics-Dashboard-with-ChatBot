#!/usr/bin/env python3
"""
Final verification test for all chatbot enhancements
"""

import requests
import json

def test_comprehensive_functionality():
    """Test all enhanced chatbot functionality"""
    
    base_url = "http://127.0.0.1:5000"
    
    test_cases = [
        {
            "name": "Generic Trend Analysis",
            "query": "Show me the trend analysis",
            "expected_type": "comprehensive_trend_analysis",
            "should_have_data": True
        },
        {
            "name": "Crime Suggestions 2016",
            "query": "2016",
            "expected_type": "crime_suggestions",
            "should_have_data": True
        },
        {
            "name": "Crime Suggestions 2019",
            "query": "2019",
            "expected_type": "crime_suggestions", 
            "should_have_data": True
        },
        {
            "name": "City Comparison",
            "query": "Compare Delhi and Mumbai arrests in 2020",
            "expected_type": "multi_city",
            "should_have_data": True
        },
        {
            "name": "Top Cities Query",
            "query": "Top 5 cities by arrests in 2020",
            "expected_type": "top_5",
            "should_have_data": True
        },
        {
            "name": "Natural Language Question",
            "query": "Which city has the most crime?",
            "expected_type": "extreme_city",
            "should_have_data": True
        }
    ]
    
    print("🔍 Final Verification Test - Chatbot Enhancements")
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
                
                # Check if response type matches or is acceptable
                type_match = (
                    response_type == test_case["expected_type"] or
                    response_type.startswith(test_case["expected_type"]) or
                    test_case["expected_type"] in response_type
                )
                
                # Special handling for some cases
                if test_case["name"] == "Natural Language Question":
                    type_match = response_type in ["extreme_city", "highest", "top_1", "city"]
                
                if type_match:
                    print("   ✅ PASS: Correct response type")
                    
                    # Check data presence
                    if test_case["should_have_data"]:
                        if data.get("data"):
                            print("   ✅ PASS: Contains data")
                            passed += 1
                        else:
                            print("   ❌ FAIL: Missing data")
                    else:
                        passed += 1
                    
                    # Show some response details
                    print(f"   📊 Type: {response_type}")
                    print(f"   📝 Title: {data.get('title', 'No title')[:50]}...")
                    
                    if data.get("insight"):
                        print(f"   💡 Insight: {data['insight'][:80]}...")
                
                else:
                    print(f"   ❌ FAIL: Expected '{test_case['expected_type']}', got '{response_type}'")
                    
                    # Show what we got for debugging
                    print(f"   📊 Actual response: {data.get('title', 'No title')}")
            
            else:
                print(f"   ❌ FAIL: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 70)
    print(f"🏁 Final Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Chatbot enhancements are working perfectly!")
    elif passed >= total * 0.8:
        print("✅ Most tests passed! Chatbot is working well with minor issues.")
    else:
        print("⚠️  Some issues detected. Review failed tests above.")
    
    return passed == total

if __name__ == "__main__":
    test_comprehensive_functionality()