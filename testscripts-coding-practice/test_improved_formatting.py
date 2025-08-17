"""
Test the improved formatting for agricultural advice
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.agri_agent import AgricultureAIAgent

async def test_improved_formatting():
    print("🧪 Testing Improved Professional Formatting")
    print("=" * 55)
    
    agent = AgricultureAIAgent()
    
    # Test the same query that showed the markdown formatting issue
    test_query = "what crops will survive for this temperatures"
    location = "Vijayawada"
    
    print(f"Query: '{test_query}'")
    print(f"Location: {location}")
    print("-" * 55)
    
    try:
        response = await agent.process_query(test_query, location)
        print("✅ Enhanced Response with Professional Formatting:")
        print("=" * 55)
        print(response)
        print("=" * 55)
        
        # Check if markdown symbols were removed
        markdown_symbols = ['**', '*', '#', '- ', '* ']
        found_markdown = []
        for symbol in markdown_symbols:
            if symbol in response:
                found_markdown.append(symbol)
        
        if found_markdown:
            print(f"⚠️ Still contains markdown symbols: {found_markdown}")
        else:
            print("✅ No markdown symbols found - Clean professional formatting achieved!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_improved_formatting())
