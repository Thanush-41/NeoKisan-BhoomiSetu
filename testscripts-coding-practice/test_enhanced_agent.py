#!/usr/bin/env python3
"""
Test script to verify the enhanced agricultural agent with soil data integration
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.agri_agent import AgricultureAIAgent

async def test_soil_integration():
    """Test the enhanced agent with soil data integration"""
    
    print("🧪 Testing Enhanced Agricultural Agent with Soil Data")
    print("=" * 60)
    
    # Initialize the agent
    agent = AgricultureAIAgent()
    
    # Test soil data functionality
    print("\n🌱 Testing Soil Data Functionality:")
    print("-" * 40)
    
    test_locations = ["Vijayawada", "Bangalore", "Guntur", "Delhi"]
    
    for location in test_locations:
        soil_data = agent.get_soil_data_for_location(location)
        print(f"📍 {location}:")
        print(f"   Soil Type: {soil_data.get('soil_type', 'Unknown')}")
        print(f"   Suitable Crops: {', '.join(soil_data.get('suitable_crops', [])[:5])}")
        print()
    
    # Test enhanced query processing
    test_cases = [
        {
            "query": "how to survive my crops for this temperatures",
            "location": "Vijayawada",
            "description": "Enhanced crop survival query with weather + soil"
        },
        {
            "query": "what seeds to plant in my area", 
            "location": "Bangalore",
            "description": "Seed selection with soil recommendations"
        },
        {
            "query": "how to improve yield of rice",
            "location": "Guntur",
            "description": "Yield optimization with soil-specific advice"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        print(f"Location: {test_case['location']}")
        print("-" * 40)
        
        try:
            # Set up user context
            user_context = {
                "location": test_case["location"],
                "coordinates": {"latitude": 16.484238, "longitude": 80.679161}
            }
            
            # Process the query
            response = await agent.process_query(
                query=test_case["query"],
                location=test_case["location"],
                user_context=user_context
            )
            
            print(f"✅ Enhanced Response:")
            print(response[:500] + "..." if len(response) > 500 else response)
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            print("\n" + "="*60)
    
    print("\n🎉 Enhanced testing completed!")

if __name__ == "__main__":
    asyncio.run(test_soil_integration())
