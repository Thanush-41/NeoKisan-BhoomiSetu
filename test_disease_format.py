import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.agri_agent import AgricultureAIAgent

async def test_disease_format():
    agent = AgricultureAIAgent()
    
    # Test disease/pest query to check the new format
    test_query = "Is there any pest outbreak expected in my district?"
    
    print("🧪 TESTING DISEASE/PEST RESPONSE FORMAT")
    print("=" * 60)
    print(f"Query: {test_query}")
    print("-" * 50)
    
    response = await agent.process_query(
        query=test_query,
        location="Vijayawada"
    )
    
    # Check if the response has the direct answer format
    has_direct_answer = "🎯 DIRECT ANSWER" in response
    has_detailed_recommendations = "📋 DETAILED RECOMMENDATIONS" in response
    
    print(f"✅ HAS DIRECT ANSWER SECTION: {has_direct_answer}")
    print(f"✅ HAS DETAILED RECOMMENDATIONS: {has_detailed_recommendations}")
    
    # Show first few lines of response
    lines = response.split('\n')
    response_preview = '\n'.join(lines[:10])
    print(f"\n📝 RESPONSE PREVIEW:\n{response_preview}...")
    
    if has_direct_answer and has_detailed_recommendations:
        print("\n🎉 SUCCESS: Disease/pest responses now have the direct answer format!")
    else:
        print("\n⚠️ FORMAT ISSUE: Missing direct answer or detailed recommendations sections")

if __name__ == "__main__":
    asyncio.run(test_disease_format())
