"""
Test script to verify BhoomiSetu dependencies and basic functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        from telegram import Update
        from telegram.ext import Application
        print("✅ python-telegram-bot imported successfully")
    except ImportError as e:
        print(f"❌ python-telegram-bot import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test if environment variables are configured"""
    print("\nTesting environment variables...")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'OPENWEATHER_API_KEY', 
        'DATA_GOV_API_KEY'
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * (len(value) - 4)}{value[-4:]}")
        else:
            print(f"❌ {var}: Not set")
            all_good = False
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key != 'your_openai_api_key_here':
        print(f"✅ OPENAI_API_KEY: {'*' * (len(openai_key) - 4)}{openai_key[-4:]}")
    else:
        print("⚠️  OPENAI_API_KEY: Please set your OpenAI API key in .env file")
        
    return all_good

def test_agent_import():
    """Test if the agricultural agent can be imported"""
    print("\nTesting agricultural agent...")
    
    try:
        sys.path.append('src')
        from agents.agri_agent import agri_agent
        print("✅ Agricultural agent imported successfully")
        return True
    except Exception as e:
        print(f"❌ Agricultural agent import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🌾 BhoomiSetu - System Check")
    print("=" * 50)
    
    imports_ok = test_imports()
    env_ok = test_environment()
    agent_ok = test_agent_import()
    
    print("\n" + "=" * 50)
    if imports_ok and env_ok and agent_ok:
        print("✅ All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Set your OpenAI API key in the .env file")
        print("2. Run: python main.py")
        print("3. Visit: http://localhost:8000")
        print("4. Chat with bot: https://t.me/neokisan_bot")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
if __name__ == "__main__":
    main()
