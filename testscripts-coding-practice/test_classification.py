#!/usr/bin/env python3
"""
Simple test script to verify the improved agricultural agent functionality
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import only the agent without the web server
from src.agents.agri_agent import AgricultureAIAgent

async def test_classification():
    """Test the improved query classification"""
    
    print("🧪 Testing Improved Agricultural Agent Classification")
    print("=" * 60)
    
    # Initialize the agent
    agent = AgricultureAIAgent()
    
    # Test queries
    test_queries = [
        "how to survive my crops for this temperatures",
        "weather in vijayawada", 
        "protect my tomato plants from heat",
        "rice price in guntur"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        print("-" * 40)
        
        try:
            # Test classification
            if agent.groq_api_key:
                classification = await agent.classify_query_with_groq(query)
                print(f"✅ Classification: {classification}")
                
                # Test weather data fetch
                if "location" in classification and classification["location"]:
                    weather = await agent.get_weather_data(classification["location"])
                    print(f"🌤️ Weather data available: {'Yes' if 'current' in weather else 'Error'}")
                
            else:
                print("⚠️ No Groq API key available")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Classification testing completed!")

if __name__ == "__main__":
    asyncio.run(test_classification())
