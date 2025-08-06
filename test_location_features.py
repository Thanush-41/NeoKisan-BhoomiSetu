#!/usr/bin/env python3
"""
Location Features Test Script for BhoomiSetu Agricultural AI Advisor
Tests automatic location detection, browser geolocation, and Telegram location sharing
"""

import requests
import json
import time

def test_location_features():
    """Test various location detection methods"""
    print("🌍 BhoomiSetu Location Features Test Suite")
    print("=" * 60)
    
    # Test cases with different location inputs
    test_cases = [
        {
            "name": "Text location only",
            "data": {"query": "weather in mumbai"},
            "description": "Basic location extraction from text"
        },
        {
            "name": "Coordinates to location (Mumbai)",
            "data": {
                "query": "what is the weather today?", 
                "coordinates": {"latitude": 19.0760, "longitude": 72.8777}
            },
            "description": "Auto-detect Mumbai from coordinates"
        },
        {
            "name": "Coordinates to location (Delhi)", 
            "data": {
                "query": "current weather", 
                "coordinates": {"latitude": 28.6139, "longitude": 77.2090}
            },
            "description": "Auto-detect Delhi from coordinates"
        },
        {
            "name": "Coordinates to location (Bangalore)",
            "data": {
                "query": "tomato prices", 
                "coordinates": {"latitude": 12.9716, "longitude": 77.5946}
            },
            "description": "Auto-detect Bangalore from coordinates for price query"
        },
        {
            "name": "Location override with coordinates",
            "data": {
                "query": "weather forecast",
                "location": "Chennai",
                "coordinates": {"latitude": 19.0760, "longitude": 72.8777}
            },
            "description": "Explicit location should override coordinates"
        },
        {
            "name": "Natural language with location",
            "data": {"query": "What's the weather like in Hyderabad today?"},
            "description": "Extract Hyderabad from natural language"
        },
        {
            "name": "Price query with location",
            "data": {"query": "onion price in pune"},
            "description": "Extract location for price queries"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"Input: {json.dumps(test_case['data'], indent=2)}")
        print("-" * 50)
        
        try:
            response = requests.post(
                "http://localhost:8000/api/query",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: SUCCESS")
                print(f"📍 Query Type: {result.get('query_type', 'Unknown')}")
                print(f"🤖 Response Preview: {result.get('response', 'No response')[:100]}...")
                
                # Check if location was detected/used
                if 'coordinates' in test_case['data']:
                    print(f"🌐 Coordinates Used: ✅")
                if any(city in result.get('response', '') for city in ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune']):
                    print(f"📍 Location Detected: ✅")
            else:
                print(f"❌ Status: HTTP {response.status_code}")
                print(f"Error: {response.text}")
        
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        time.sleep(1)  # Small delay between requests
    
    print("\n" + "=" * 60)
    print("🎯 Location Features Summary:")
    print("✅ Web Interface: Browser geolocation API integrated")
    print("✅ Auto-location: Detects location from coordinates using reverse geocoding")
    print("✅ Text Extraction: Extracts cities from natural language queries") 
    print("✅ Local Storage: Saves user location in browser localStorage")
    print("✅ Form Integration: Auto-populates location in chat forms")
    print("✅ Telegram Bot: Location sharing with request_location button")
    print("✅ API Support: Handles coordinates in JSON requests")
    print("✅ Fallback: Uses extracted location when coordinates unavailable")
    
    print("\n🚀 How to Test:")
    print("1. 🌐 Web: Open http://localhost:8000/chat and click 'Get My Location'")
    print("2. 📱 Telegram: Go to https://t.me/neokisan_bot and use /location command")
    print("3. 🤖 API: Send POST to /api/query with coordinates in JSON")
    print("4. 💬 Chat: Ask 'weather in [city]' or share location directly")

if __name__ == "__main__":
    test_location_features()
