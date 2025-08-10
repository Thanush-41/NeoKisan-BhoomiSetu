#!/usr/bin/env python3
"""
Test script to verify conversation context retention functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agri_agent import AgricultureAIAgent

async def test_context_retention():
    """Test conversation context retention with follow-up questions"""
    agent = AgricultureAIAgent()
    
    # Simulate a conversation history
    conversation_history = [
        {
            "role": "user",
            "content": "What crops should I grow this season in my area?"
        },
        {
            "role": "assistant", 
            "content": "🎯 DIRECT ANSWER\nFor Krishna district in Kharif season, I recommend growing **rice** as your primary crop. It's well-suited to your black soil and current weather conditions.\n\n📋 DETAILED RECOMMENDATIONS\n\n**Recommended Crops:**\n1. **Rice (Primary)** - Varieties: BPT 5204, Swarna\n2. **Maize** - Alternative option\n3. **Cotton** - Cash crop option\n\n**Planting Time:** June-July\n**Expected Yield:** 25-30 quintals per acre for rice"
        },
        {
            "role": "user",
            "content": "What about irrigation requirements?"
        },
        {
            "role": "assistant",
            "content": "🎯 DIRECT ANSWER\nFor rice cultivation, you'll need regular irrigation. Rice requires standing water for most of its growth period.\n\n📋 DETAILED RECOMMENDATIONS\n\n**Rice Irrigation Schedule:**\n- Initial flooding: 2-3 inches after transplanting\n- Maintain 2-3 inches water throughout vegetative stage\n- Drain 1 week before harvest\n\n**Water Requirements:** 1200-1500mm total"
        }
    ]
    
    print("🧪 TESTING CONVERSATION CONTEXT RETENTION")
    print("=" * 60)
    
    # Test context-dependent follow-up questions
    test_queries = [
        "What fertilizer schedule should I follow for the crop you recommended?",
        "Based on your earlier suggestion, what are the common diseases I should watch out for?",
        "You mentioned BPT 5204 variety - what's the seed rate for this?",
        "Following your advice on rice, when should I start land preparation?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. TESTING CONTEXT QUERY")
        print("-" * 40)
        print(f"Query: {query}")
        print(f"Conversation History: {len(conversation_history)} messages")
        
        try:
            result = await agent.process_query(
                query=query, 
                location='Krishna',
                conversation_history=conversation_history
            )
            
            # Check if it referenced previous context
            context_indicators = [
                "rice", "BPT 5204", "recommended", "suggested", "mentioned earlier",
                "crop you", "variety you", "as discussed"
            ]
            
            has_context_reference = any(indicator.lower() in result.lower() for indicator in context_indicators)
            
            print(f"✅ HAS CONTEXT REFERENCE: {has_context_reference}")
            print(f"📝 RESPONSE PREVIEW:")
            
            # Show first part of response (clean HTML for preview)
            import re
            clean_text = re.sub(r'<[^>]+>', '', result)
            preview = clean_text[:250] + "..." if len(clean_text) > 250 else clean_text
            print(preview)
            
            # Add this query to conversation history for next iteration
            conversation_history.append({"role": "user", "content": query})
            conversation_history.append({"role": "assistant", "content": result})
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()
    
    print("=" * 60)
    print("🏁 CONTEXT RETENTION TESTS COMPLETED")

if __name__ == "__main__":
    asyncio.run(test_context_retention())
