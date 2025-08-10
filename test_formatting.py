#!/usr/bin/env python3
"""Test the formatting functionality for chat responses"""

import asyncio
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.agents.agri_agent import AgricultureAIAgent

async def test_formatting():
    """Test the formatting of agricultural responses"""
    
    # Create agent instance
    agent = AgricultureAIAgent()
    
    # Sample response with markdown formatting
    sample_response = """### Weather Forecast for Delhi
Today's weather will be sunny with temperatures reaching 32°C.

## Agricultural Recommendations
Based on current weather conditions:

- **Irrigation**: Water your crops early morning
- **Fertilizer**: Apply nitrogen-based fertilizers
- **Pest Control**: Monitor for aphids

1. Check soil moisture levels
2. Adjust irrigation timing
3. Monitor crop health

**Important**: Ensure proper drainage during monsoon season."""

    print("🌾 Original Response:")
    print(sample_response)
    print("\n" + "="*50 + "\n")
    
    # Test the formatting function
    formatted_response = agent._format_response_for_chat(sample_response)
    
    print("🌱 Formatted Response (HTML):")
    print(formatted_response)
    print("\n" + "="*50 + "\n")
    
    # Test a simple query
    print("🌾 Testing actual query...")
    try:
        response = await agent.process_query(
            query="What should I plant in Delhi during summer season?",
            location="Delhi"
        )
        print("📝 Actual Response:")
        print(response)
    except Exception as e:
        print(f"❌ Error during query: {e}")

if __name__ == "__main__":
    asyncio.run(test_formatting())
