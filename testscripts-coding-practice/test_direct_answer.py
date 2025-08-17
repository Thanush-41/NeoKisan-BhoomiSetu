#!/usr/bin/env python3
"""
Test script to verify direct answer functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.agri_agent import AgricultureAIAgent

async def test_direct_answers():
    """Test direct answer functionality with specific queries"""
    
    print("🧪 Testing Direct Answer Functionality...")
    print("=" * 60)
    
    agent = AgricultureAIAgent()
    
    # Test cases with specific questions that need direct answers
    test_queries = [
        "Should I irrigate my wheat crop this week based on the forecast?",
        "Which wheat variety is best for Punjab soil?",
        "When should I plant tomatoes in Delhi?",
        "What fertilizer should I use for rice crop?",
        "Can I harvest my cotton crop now?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 50)
        
        try:
            # Test with Delhi as location
            response = await agent.process_query(
                query=query,
                location="Delhi",
                user_context={"preferred_language": "en"}
            )
            
            print("🤖 AI Response:")
            print(response)
            
            # Check if response starts with direct answer
            if "🎯 DIRECT ANSWER" in response or response.startswith("YES") or response.startswith("NO"):
                print("✅ Contains direct answer format")
            else:
                print("❌ Missing direct answer format")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test_direct_answers())
