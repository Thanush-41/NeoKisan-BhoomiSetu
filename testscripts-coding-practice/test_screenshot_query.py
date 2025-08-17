"""
Test formatting specifically for the query from the screenshot
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.agri_agent import AgricultureAIAgent

async def test_screenshot_query():
    print("🧪 Testing Query from Screenshot")
    print("=" * 45)
    
    agent = AgricultureAIAgent()
    
    # Test the exact query from the screenshot
    test_query = "Best crops for kharif season"
    location = "Vijayawada"
    
    print(f"Query: '{test_query}'")
    print(f"Location: {location}")
    print("-" * 45)
    
    try:
        response = await agent.process_query(test_query, location)
        print("✅ IMPROVED RESPONSE:")
        print("=" * 45)
        print(response)
        print("=" * 45)
        
        # Check formatting improvements
        if "IMMEDIATE ACTIONS" in response:
            print("✅ Clear section headers found")
        if "\n\n" in response:
            print("✅ Proper paragraph spacing found")
        if response.count("\n") > 10:
            print("✅ Good line breaks for readability")
        else:
            print("⚠️ May need more line breaks")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_screenshot_query())
