#!/usr/bin/env python3
"""Test the enhanced AI weather response system"""

import asyncio
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.agents.agri_agent import AgricultureAIAgent

async def test_weather_queries():
    """Test different types of weather queries"""
    
    # Create agent instance
    agent = AgricultureAIAgent()
    
    # Test queries with different day requests
    test_queries = [
        {
            "query": "What will be the weather in my village for the next 7 days?",
            "location": "Vijayawada",
            "description": "7-day weather request (API only provides 5)"
        },
        {
            "query": "How's the weather looking for my crops this week?",
            "location": "Bangalore", 
            "description": "Agricultural weather query"
        },
        {
            "query": "Give me 5 day weather forecast",
            "location": "Delhi",
            "description": "Exact 5-day request"
        },
        {
            "query": "Will it rain tomorrow for planting seeds?",
            "location": "Mumbai",
            "description": "Agricultural timing query"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"🌤️ TEST {i}: {test['description']}")
        print(f"📝 Query: {test['query']}")
        print(f"📍 Location: {test['location']}")
        print('='*80)
        
        try:
            response = await agent.process_query(
                query=test["query"],
                location=test["location"]
            )
            print(f"✅ AI Weather Response:")
            print(response)
            print("\n")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_weather_queries())
