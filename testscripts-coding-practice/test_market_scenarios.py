#!/usr/bin/env python3
"""
Test enhanced market logic with different price scenarios
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agri_agent import AgricultureAIAgent

async def test_market_scenarios():
    """Test different market pricing scenarios"""
    agent = AgricultureAIAgent()
    
    test_scenarios = [
        {
            "scenario": "Low Local Price - Should Sell in Mandi",
            "query": "If today market price of tomatoes is ₹15/kg and my transport cost is ₹2/kg, should I sell now or wait for prices to rise?",
            "expected": "SELL IN MANDI"
        },
        {
            "scenario": "High Local Price - Should Sell Locally", 
            "query": "If today market price of tomatoes is ₹45/kg and my transport cost is ₹3/kg, should I sell now or wait for prices to rise?",
            "expected": "SELL LOCALLY"
        },
        {
            "scenario": "Price Without Transport Cost",
            "query": "If today market price of tomatoes is ₹20/kg, should I sell now or wait for prices to rise?",
            "expected": "Price comparison"
        },
        {
            "scenario": "Regular Price Query",
            "query": "What is the current price of tomatoes?",
            "expected": "Standard market prices"
        }
    ]
    
    print("🧪 TESTING ENHANCED MARKET LOGIC SCENARIOS")
    print("=" * 70)
    
    for i, test in enumerate(test_scenarios, 1):
        print(f"\n{i}. {test['scenario'].upper()}")
        print("-" * 60)
        print(f"Query: {test['query']}")
        print(f"Expected: {test['expected']}")
        
        try:
            result = await agent.process_query(test['query'], location='Vijayawada')
            
            # Check if it has personalized recommendation
            has_recommendation = any(rec in result for rec in [
                "SELL IN MANDI", "SELL LOCALLY", "MANDI SLIGHTLY BETTER"
            ])
            
            # Check if it shows profit calculation
            has_calculation = "Extra profit:" in result or "net price:" in result
            
            print(f"✅ HAS RECOMMENDATION: {has_recommendation}")
            print(f"✅ HAS CALCULATION: {has_calculation}")
            
            # Show first part of response
            if "🎯 DIRECT ANSWER" in result:
                direct_part = result.split("📋 DETAILED")[0]
                print(f"📝 DIRECT ANSWER PREVIEW:")
                # Remove HTML tags for cleaner preview
                import re
                clean_text = re.sub(r'<[^>]+>', '', direct_part)
                print(clean_text[:300] + "...")
            else:
                print(f"📝 RESPONSE PREVIEW: {result[:200]}...")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()
    
    print("=" * 70)
    print("🏁 ENHANCED MARKET LOGIC TESTS COMPLETED")

if __name__ == "__main__":
    asyncio.run(test_market_scenarios())
