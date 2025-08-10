import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.agri_agent import AgricultureAIAgent

async def test_specific_responses():
    agent = AgricultureAIAgent()
    
    # Test cases with different specific questions
    test_queries = [
        "Which crop is best for my soil with N=40, P=25, K=30?",
        "What's the best seed variety for unpredictable rainfall?", 
        "Should I irrigate my wheat crop this week based on the forecast?",
        "How much fertilizer should I apply to tomatoes?"
    ]
    
    print("🧪 TESTING SPECIFIC QUERY RESPONSES")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. QUERY: {query}")
        print("-" * 50)
        
        response = await agent.process_query(
            query=query,
            location="Vijayawada"
        )
        
        response_text = response
        lines = response_text.split('\n')
        
        # Check if response is focused
        is_focused = True
        focus_issues = []
        
        # Check for generic sections that shouldn't be there for specific questions
        generic_keywords = [
            "RESOURCE OPTIMIZATION",
            "TIMING RECOMMENDATIONS", 
            "RISK MANAGEMENT",
            "WEATHER RESPONSE STRATEGY"
        ]
        
        for line in lines:
            line_upper = line.upper()
            if any(keyword in line_upper for keyword in generic_keywords):
                # Only flag as unfocused if it's a very specific query
                if any(specific in query.lower() for specific in ["n=", "p=", "k=", "variety for unpredictable"]):
                    focus_issues.append(f"Found generic section: {line.strip()}")
        
        # Check if direct answer exists
        has_direct_answer = "🎯 DIRECT ANSWER" in response_text
        
        print(f"✅ HAS DIRECT ANSWER: {has_direct_answer}")
        print(f"📍 FOCUS SCORE: {'High' if len(focus_issues) == 0 else 'Medium' if len(focus_issues) <= 2 else 'Low'}")
        
        if focus_issues:
            print(f"⚠️  FOCUS ISSUES: {len(focus_issues)} generic sections found")
            for issue in focus_issues[:2]:  # Show first 2 issues
                print(f"   - {issue}")
        
        # Show first few lines of response
        response_preview = '\n'.join(lines[:8])
        print(f"\n📝 RESPONSE PREVIEW:\n{response_preview}...")
        print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_specific_responses())
