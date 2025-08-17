"""
Quick test to verify OpenAI JSON parsing fix
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.agri_agent import AgricultureAIAgent

async def test_openai_parsing():
    print("🧪 Testing OpenAI JSON Parsing Fix")
    print("=" * 50)
    
    agent = AgricultureAIAgent()
    
    # Test query that previously failed
    test_query = "my crops are dying due to high temperature what to do"
    
    print(f"Testing query: '{test_query}'")
    print("-" * 40)
    
    try:
        # Test the enhanced AI classification directly
        result = await agent.classify_query_with_openai(test_query)
        print(f"✅ Classification successful:")
        print(f"   Intent: {result.get('intent', 'Unknown')}")
        print(f"   Commodity: {result.get('commodity', 'None')}")
        print(f"   Location: {result.get('location', 'None')}")
        print(f"   Confidence: {result.get('confidence', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Classification still failing: {e}")
        # Try to see what the raw response looks like
        if hasattr(agent, 'openai_client') and agent.openai_client:
            try:
                prompt = f"""
Analyze this Indian agricultural query and provide JSON response:
Query: "{test_query}"

Return ONLY valid JSON in this exact format:
{{
  "intent": "weather_agriculture",
  "commodity": null,
  "location": null,
  "specific_question": "extracted question",
  "recommended_action": "suggested action",
  "context_needed": ["item1", "item2"],
  "urgent": false,
  "confidence": 0.85
}}"""
                
                response = await agent.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=500
                )
                
                raw_response = response.choices[0].message.content.strip()
                print(f"🔍 Raw OpenAI response:")
                print(f"'{raw_response}'")
                print(f"Length: {len(raw_response)}")
                print(f"Starts with: '{raw_response[:20]}'")
                print(f"Ends with: '{raw_response[-20:]}'")
                
            except Exception as inner_e:
                print(f"❌ Raw API call also failed: {inner_e}")

if __name__ == "__main__":
    asyncio.run(test_openai_parsing())
