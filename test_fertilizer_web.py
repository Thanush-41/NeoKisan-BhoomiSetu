#!/usr/bin/env python3
"""
Test fertilizer recommendations specifically with the web interface
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.agri_agent import AgricultureAIAgent

async def test_fertilizer_in_web_response():
    """Test fertilizer recommendations in web-style responses"""
    print("🌐 Testing fertilizer recommendations in web interface format...")
    
    agent = AgricultureAIAgent()
    
    # Test with typical fertilizer queries
    queries = [
        "What fertilizer should I use for maize in sandy soil?",
        "Best fertilizer for rice cultivation in current weather?",
        "I need NPK recommendations for cotton in black soil",
        "Which fertilizer is good for sugarcane in loamy soil?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*50}")
        print(f"Test {i}: {query}")
        print('='*50)
        
        try:
            # Simulate web request context
            context_data = {
                "weather": {
                    "current": {
                        "temperature": 28 + i,  # Varying temperature
                        "humidity": 70 + i * 5,  # Varying humidity
                        "description": "partly cloudy"
                    }
                },
                "soil": {
                    "soil_type": ["sandy", "loamy", "black", "clayey"][i-1],
                    "suitable_crops": ["maize", "rice", "cotton", "sugarcane"]
                }
            }
            
            response = await agent._generate_comprehensive_agricultural_advice(
                query=query,
                weather_info=context_data["weather"],
                soil_info=context_data["soil"],
                location_name="Hyderabad"
            )
            
            print("📝 Response:")
            print(response)
            
            # Check for fertilizer dataset integration
            if "fertilizer dataset" in response.lower():
                print("\n✅ Fertilizer dataset recommendations included!")
            elif "n-p-k" in response.lower() or "npk" in response.lower():
                print("\n✅ NPK recommendations found!")
            else:
                print("\n⚠️ No obvious fertilizer dataset recommendations found")
                
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_direct_fertilizer_lookup():
    """Test direct fertilizer dataset lookup"""
    print("\n🔍 Testing direct fertilizer dataset lookup...")
    
    agent = AgricultureAIAgent()
    
    # Test various combinations
    test_cases = [
        {"soil": "sandy", "crop": "maize", "temp": 26, "humidity": 52},
        {"soil": "loamy", "crop": "sugarcane", "temp": 29, "humidity": 52},
        {"soil": "black", "crop": "cotton", "temp": 34, "humidity": 65},
        {"soil": "red", "crop": "tobacco", "temp": 32, "humidity": 62}
    ]
    
    for case in test_cases:
        print(f"\n🧪 Testing: {case['crop']} in {case['soil']} soil, {case['temp']}°C, {case['humidity']}%")
        
        recommendations = agent.get_fertilizer_recommendations(
            soil_type=case['soil'],
            crop_type=case['crop'],
            temperature=case['temp'],
            humidity=case['humidity'],
            moisture=50
        )
        
        if recommendations.get('recommendations'):
            for rec in recommendations['recommendations']:
                print(f"  💡 {rec['fertilizer']}: NPK {rec['npk']['nitrogen']}-{rec['npk']['phosphorus']}-{rec['npk']['potassium']}")
                if 'match_score' in rec:
                    print(f"      Match Score: {rec['match_score']}%")
        else:
            print("  ❌ No recommendations found")

if __name__ == "__main__":
    asyncio.run(test_fertilizer_in_web_response())
    asyncio.run(test_direct_fertilizer_lookup())
