"""
Test Telegram Bot functionality for BhoomiSetu
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_telegram_setup():
    """Test Telegram bot setup without actually running it"""
    print("🤖 Testing Telegram Bot Setup...")
    
    # Check token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return False
    
    print(f"✅ Bot token found: ...{token[-8:]}")
    
    # Test import
    try:
        from telegram import Bot
        print("✅ python-telegram-bot library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import telegram: {e}")
        return False
    
    # Test bot creation
    try:
        bot = Bot(token=token)
        print("✅ Bot object created successfully")
    except Exception as e:
        print(f"❌ Failed to create bot: {e}")
        return False
    
    # Test bot info (requires internet)
    try:
        print("📡 Testing bot connection...")
        bot_info = await bot.get_me()
        print(f"✅ Bot connected successfully!")
        print(f"   Bot name: {bot_info.first_name}")
        print(f"   Bot username: @{bot_info.username}")
        print(f"   Bot ID: {bot_info.id}")
        return True
    except Exception as e:
        print(f"⚠️  Could not connect to bot (check internet): {e}")
        return False

def test_agent_simple():
    """Test agricultural agent basic functionality"""
    print("\n🌾 Testing Agricultural Agent...")
    
    try:
        import sys
        sys.path.append('src')
        from agents.agri_agent import agri_agent
        print("✅ Agricultural agent imported")
        
        # Test basic query classification
        test_queries = [
            "When should I irrigate my crops?",
            "What are tomato prices today?", 
            "How can I get a loan?",
            "What's the weather like?"
        ]
        
        for query in test_queries:
            query_type = agri_agent.classify_query(query)
            print(f"   '{query}' → {query_type}")
        
        return True
    except Exception as e:
        print(f"❌ Agricultural agent test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🌾 BhoomiSetu Telegram Bot Test")
    print("=" * 50)
    
    # Test basic functionality
    agent_ok = test_agent_simple()
    
    # Test telegram setup
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    telegram_ok = loop.run_until_complete(test_telegram_setup())
    
    print("\n" + "=" * 50)
    if agent_ok and telegram_ok:
        print("✅ All tests passed!")
        print("\n🚀 To start the Telegram bot:")
        print("   python src/telegram/bot.py")
        print("\n💬 Chat with your bot:")
        print("   https://t.me/neokisan_bot")
    else:
        print("❌ Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main()
