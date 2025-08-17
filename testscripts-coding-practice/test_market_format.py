import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.agri_agent import AgricultureAIAgent

async def test_market_price_format():
    agent = AgricultureAIAgent()
    
    # Test market price query to check the new format
    test_query = "What's the current market price of maize in the nearest mandi?"
    
    print("🧪 TESTING MARKET PRICE RESPONSE FORMAT")
    print("=" * 60)
    print(f"Query: {test_query}")
    print("-" * 50)
    
    response = await agent.process_query(
        query=test_query,
        location="Vijayawada"
    )
    
    # Check if the response has the direct answer format
    has_direct_answer = "🎯 DIRECT ANSWER" in response
    has_detailed_info = "📋 DETAILED MARKET INFORMATION" in response
    has_per_kg_price = "per kg" in response
    
    print(f"✅ HAS DIRECT ANSWER SECTION: {has_direct_answer}")
    print(f"✅ HAS DETAILED MARKET INFO: {has_detailed_info}")
    print(f"✅ HAS PER KG PRICES: {has_per_kg_price}")
    
    # Show first few lines of response
    lines = response.split('\n')
    response_preview = '\n'.join(lines[:15])
    print(f"\n📝 RESPONSE PREVIEW:\n{response_preview}...")
    
    if has_direct_answer and has_per_kg_price:
        print("\n🎉 SUCCESS: Market price responses now have direct answer format with per kg prices!")
    else:
        print("\n⚠️ FORMAT ISSUE: Missing direct answer or per kg prices")

if __name__ == "__main__":
    asyncio.run(test_market_price_format())
