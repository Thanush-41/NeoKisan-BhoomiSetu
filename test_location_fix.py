#!/usr/bin/env python3
"""Test script to verify location fix in agricultural AI agent"""

import requests
import json

def test_location_fix():
    """Test that the location parameter is correctly used for weather queries"""
    
    # Test data
    url = "http://localhost:8000/chat"
    data = {
        'message': 'Tomorrow weather forecast for my area?',
        'location': 'Vijayawada, Andhra Pradesh, IN',
        'latitude': '',
        'longitude': '',
        'conversation_history': '[]',
        'language': 'en'
    }
    
    print("🧪 Testing location fix for agricultural AI agent...")
    print(f"📍 Sending query: '{data['message']}'")
    print(f"🌍 With location: '{data['location']}'")
    print()
    
    try:
        # Send request
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result.get('response', '')
        
        print("📝 AI Response Analysis:")
        print("=" * 50)
        
        # Check for location mentions
        if 'Vijayawada' in ai_response or 'విజయవాడ' in ai_response:
            print("✅ SUCCESS: Correct location (Vijayawada) found in response!")
        elif 'Innichen' in ai_response or 'Italy' in ai_response:
            print("❌ ISSUE: Wrong location (Innichen/Italy) still appearing!")
        else:
            print("🔍 No specific location found in response")
        
        # Show first part of response
        print("\n📄 Response Preview (first 400 chars):")
        print("-" * 40)
        print(ai_response[:400] + "..." if len(ai_response) > 400 else ai_response)
        
        # Look for weather data
        if 'weather' in ai_response.lower() or 'temperature' in ai_response.lower():
            print("\n🌤️ Weather information found in response")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_location_fix()
