"""
Main application runner for BhoomiSetu
Handles both web and Telegram bot interfaces
"""

import os
import asyncio
import threading
import uvicorn
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

def run_telegram_bot():
    """Run Telegram bot in a separate thread"""
    try:
        import asyncio
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from src.telegram.bot import TelegramBot
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        print(f"Error starting Telegram bot: {e}")

def run_web_app():
    """Run FastAPI web application"""
    try:
        uvicorn.run(
            "src.web.main:app",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8000)),
            reload=True
        )
    except Exception as e:
        print(f"Error starting web app: {e}")

def main():
    """Main function to start both services"""
    print("🌾 Starting BhoomiSetu Agricultural AI Advisor...")
    
    # Check required environment variables
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'OPENWEATHER_API_KEY',
        'DATA_GOV_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and add the missing variables.")
        return
    
    print("✅ Environment variables loaded successfully")
    
    # Start Telegram bot in a separate thread
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    print("🤖 Telegram bot started")
    
    # Start web application (main thread)
    print("🌐 Starting web application...")
    print(f"🔗 Web interface: http://localhost:{os.getenv('PORT', 8000)}")
    print(f"🤖 Telegram bot: https://t.me/neokisan_bot")
    
    run_web_app()

if __name__ == "__main__":
    main()
