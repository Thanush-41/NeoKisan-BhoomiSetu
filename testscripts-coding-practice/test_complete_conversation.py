#!/usr/bin/env python3
"""
Complete test for conversation context retention functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agri_agent import AgricultureAIAgent

async def test_complete_conversation():
    """Test a complete conversation flow with context retention"""
    agent = AgricultureAIAgent()
    
    print("🧪 TESTING COMPLETE CONVERSATION CONTEXT RETENTION")
    print("=" * 70)
    
    conversation_history = []
    
    # Conversation sequence
    queries = [
        "What crops should I grow this season?",
        "What fertilizer schedule should I follow for the crop you recommended?",
        "You mentioned rice earlier - what about pest control?",
        "Based on your earlier advice, when should I harvest?",
        "What's the expected yield for the variety you suggested?"
    ]
    
    location = "Krishna"
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. USER: {query}")
        print("-" * 60)
        
        try:
            # Process query with conversation history
            response = await agent.process_query(
                query=query,
                location=location,
                conversation_history=conversation_history
            )
            
            print(f"🤖 AGENT:")
            # Clean and preview response
            import re
            clean_response = re.sub(r'<[^>]+>', '', response)
            preview = clean_response[:400] + "..." if len(clean_response) > 400 else clean_response
            print(preview)
            
            # Add messages to conversation history
            conversation_history.append({
                "role": "user",
                "content": query
            })
            conversation_history.append({
                "role": "assistant", 
                "content": response
            })
            
            print(f"\n📊 Conversation history: {len(conversation_history)} messages")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()
    
    print("=" * 70)
    print("🎉 COMPLETE CONVERSATION TEST COMPLETED")
    print(f"Final conversation history: {len(conversation_history)} messages")

if __name__ == "__main__":
    asyncio.run(test_complete_conversation())
