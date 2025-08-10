import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.agri_agent import AgricultureAIAgent

async def test_api_priority():
    agent = AgricultureAIAgent()
    
    # Test query to check which API is being used
    test_query = "Which crop is best for my soil with N=40, P=25, K=30?"
    
    print("🧪 TESTING API PRIORITY")
    print("=" * 60)
    print(f"Query: {test_query}")
    print("-" * 50)
    
    response = await agent.process_query(
        query=test_query,
        location="Vijayawada"
    )
    
    # The debug logs will show which API is being used
    print("✅ Response received")
    print("📝 Check the logs above to see which API was used")
    print("\nExpected: Should see 'Using OpenAI' messages, not 'Using Groq'")

if __name__ == "__main__":
    asyncio.run(test_api_priority())
