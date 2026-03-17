#!/usr/bin/env python3
"""
Test script for greeting capabilities formatting
"""

import requests
import json

def test_greeting_capabilities():
    """Test that greeting capabilities are properly formatted"""
    
    base_url = "http://127.0.0.1:5000"
    
    test_queries = ["hi", "hello", "hey"]
    
    print("🧪 Testing Greeting Capabilities Formatting")
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
                
                if data.get("type") == "greeting":
                    print("✅ SUCCESS: Greeting response received")
                    print(f"   Summary: {data.get('summary', 'No summary')[:50]}...")
                    
                    # Check capabilities
                    if data.get("capabilities") and isinstance(data["capabilities"], list):
                        print(f"   ✅ Capabilities count: {len(data['capabilities'])}")
                        print("   📋 Capabilities:")
                        for j, capability in enumerate(data["capabilities"][:3], 1):
                            print(f"      {j}. {capability}")
                        if len(data["capabilities"]) > 3:
                            print(f"      ... and {len(data['capabilities']) - 3} more")
                    else:
                        print("   ❌ No capabilities found")
                    
                    # Check example
                    if data.get("example"):
                        print(f"   💡 Example: {data['example'][:50]}...")
                
                else:
                    print(f"⚠️  Got type '{data.get('type')}' instead of 'greeting'")
            
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_greeting_capabilities()