import asyncio
import sys
import os
sys.path.append('src')
from agents.agri_agent import AgricultureAIAgent

async def test_agent():
    try:
        agent = AgricultureAIAgent()
        response = await agent.process_query('What crops are good for winter?', 'Delhi')
        print(f'✅ Agent working! Response length: {len(response)}')
        print(f'First 100 chars: {response[:100]}...')
        return True
    except Exception as e:
        print(f'❌ Agent error: {e}')
        return False

if __name__ == "__main__":
    result = asyncio.run(test_agent())
    print(f'Test result: {result}')
