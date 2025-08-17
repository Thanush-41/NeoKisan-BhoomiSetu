#!/usr/bin/env python3
"""Test the improved query-specific agricultural advice"""

import asyncio
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.agents.agri_agent import AgricultureAIAgent

async def test_different_queries():
    """Test different types of agricultural queries"""
    
    # Create agent instance
    agent = AgricultureAIAgent()
    
    # Test queries with different focus areas
    test_queries = [
        {
            "query": "What is the best crop to plant in Vijayawada with soil nutrients N=40, P=25, K=30 during the Kharif season?",
            "location": "Vijayawada",
            "description": "Nutrient-specific query"
        },
        {
            "query": "What's the best seed variety for unpredictable rainfall?",
            "location": "Vijayawada", 
            "description": "Weather-resistant variety query"
        },
        {
            "query": "When should I harvest my cotton crop?",
            "location": "Vijayawada",
            "description": "Timing-specific query"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"🌾 TEST {i}: {test['description']}")
        print(f"📝 Query: {test['query']}")
        print(f"📍 Location: {test['location']}")
        print('='*80)
        
        try:
            response = await agent.process_query(
                query=test["query"],
                location=test["location"]
            )
            print(f"✅ Response Preview (first 200 chars):")
            print(response[:200] + "..." if len(response) > 200 else response)
            print("\n")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_different_queries())
