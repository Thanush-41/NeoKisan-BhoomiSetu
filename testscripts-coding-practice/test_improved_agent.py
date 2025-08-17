#!/usr/bin/env python3
"""
Test script to verify the improved agricultural agent functionality
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.agri_agent import AgricultureAIAgent

async def test_crop_survival_query():
    """Test the improved query handling for crop survival questions"""
    
    print("🧪 Testing Improved Agricultural Agent")
    print("=" * 50)
    
    # Initialize the agent
    agent = AgricultureAIAgent()
    
    # Test cases with different types of queries
    test_cases = [
        {
            "query": "how to survive my crops for this temperatures",
            "location": "Vijayawada",
            "description": "Original query from logs - should trigger weather_agriculture intent"
        },
        {
            "query": "weather in bangalore", 
            "location": "Bangalore",
            "description": "Pure weather query - should trigger weather intent"
        },
        {
            "query": "protect my tomato plants from heat",
            "location": "Chennai",
            "description": "Agricultural protection query - should trigger weather_agriculture intent"
        },
        {
            "query": "rice price in guntur",
            "location": "Guntur", 
            "description": "Price query - should trigger price intent"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        print(f"Location: {test_case['location']}")
        print("-" * 30)
        
        try:
            # Set up user context
            user_context = {
                "location": test_case["location"],
                "coordinates": {"latitude": 16.484238, "longitude": 80.679161}  # Sample coordinates
            }
            
            # Process the query
            response = await agent.process_query(
                query=test_case["query"],
                location=test_case["location"],
                user_context=user_context
            )
            
            print(f"✅ Response received:")
            print(response)
            print("\n" + "="*50)
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            print("\n" + "="*50)
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_crop_survival_query())
