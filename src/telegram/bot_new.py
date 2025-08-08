"""
Telegram Bot for BhoomiSetu Agricultural AI Agent
Handles user interactions via Telegram messaging with automatic location detection
"""

import os
import logging
import asyncio
import requests
from typing import Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters, 
    ContextTypes
)
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agents.agri_agent import agri_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.user_sessions = {}  # Store user context
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command and immediately ask for location"""
        user = update.effective_user
        user_id = user.id
        
        # Initialize user session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        
        welcome_message = f"""🌾 **Welcome to BhoomiSetu, {user.first_name}!** 🌾

I'm your AI-powered agricultural advisor. I can help you with:

🌱 **Crop Management**
• When to irrigate your crops
• Which seed varieties to choose
• Pest and disease identification

🌤️ **Weather Information**
• Real-time weather updates
• 5-day forecasts
• Agricultural alerts

💰 **Market Intelligence**
• Current commodity prices
• Price trends and forecasts
• Best markets to sell

🏛️ **Government Schemes**
• Agricultural loans and subsidies
• Insurance schemes
• Direct benefit transfers

📍 **To provide personalized advice, I need your location first.**"""
        
        # Send welcome message
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        
        # Immediately ask for location
        await self.ask_for_location(update, context)

    async def ask_for_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask user for their location with sharing button"""
        keyboard = [[KeyboardButton("📍 Share My Location", request_location=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        location_message = """🌍 **Share Your Location**

To provide accurate weather forecasts and local market prices, please share your location:

1️⃣ **Tap the button below** to share your current GPS location
2️⃣ **Or type your city**: `/location Mumbai`

This helps me give you:
• 🌤️ Local weather forecasts
• 💰 Nearby market prices
• 🌾 Region-specific farming advice"""
        
        await update.message.reply_text(
            location_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle shared location from Telegram"""
        user_id = update.effective_user.id
        location = update.message.location
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        
        # Store coordinates
        self.user_sessions[user_id]['coordinates'] = {
            'latitude': location.latitude,
            'longitude': location.longitude
        }
        
        # Get city name from coordinates
        try:
            api_key = os.getenv('OPENWEATHER_API_KEY')
            if not api_key:
                await update.message.reply_text("Weather service is not configured. Please try again later.")
                return
            url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={location.latitude}&lon={location.longitude}&limit=1&appid={api_key}"
            
            response = requests.get(url)
            data = response.json()
            
            if data and len(data) > 0:
                city_name = data[0].get('name', 'Unknown')
                state = data[0].get('state', '')
                country = data[0].get('country', '')
                
                self.user_sessions[user_id]['location'] = city_name
                
                # Get weather for confirmation
                weather_data = await agri_agent.get_weather_data(city_name)
                
                if "error" not in weather_data:
                    current = weather_data.get("current", {})
                    await update.message.reply_text(
                        f"📍 **Location detected:** {city_name}, {state}\n\n"
                        f"🌤️ **Current Weather:**\n"
                        f"🌡️ Temperature: {current.get('temperature', 'N/A')}°C\n"
                        f"☁️ Conditions: {current.get('description', 'N/A')}\n"
                        f"💧 Humidity: {current.get('humidity', 'N/A')}%\n"
                        f"💨 Wind: {current.get('wind_speed', 'N/A')} m/s\n\n"
                        f"✅ Perfect! Now I can provide weather and market information for your area.\n\n"
                        f"Try asking: 'weather today' or 'tomato prices'",
                        reply_markup=ReplyKeyboardRemove(),
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        f"📍 **Location detected:** {city_name}, {state}\n"
                        f"✅ Location saved for personalized advice!\n\n"
                        f"Now ask me anything about farming!",
                        reply_markup=ReplyKeyboardRemove(),
                        parse_mode='Markdown'
                    )
                    
        except Exception as e:
            logger.error(f"Location processing error: {e}")
            await update.message.reply_text(
                f"📍 Location received! Coordinates: {location.latitude:.4f}, {location.longitude:.4f}\n"
                f"✅ I'll use this for weather and market information.\n\n"
                f"Now ask me anything about farming!",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode='Markdown'
            )

    async def set_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /location command"""
        user_id = update.effective_user.id
        
        if context.args:
            location = ' '.join(context.args)
            
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {}
            
            self.user_sessions[user_id]['location'] = location
            
            # Get weather for the location to verify
            try:
                weather_data = await agri_agent.get_weather_data(location)
                if "error" not in weather_data:
                    current = weather_data.get("current", {})
                    await update.message.reply_text(
                        f"📍 Location set to: **{location}**\n\n"
                        f"Current weather:\n"
                        f"🌡️ {current.get('temperature', 'N/A')}°C\n"
                        f"🌤️ {current.get('description', 'N/A')}\n"
                        f"💧 Humidity: {current.get('humidity', 'N/A')}%\n\n"
                        f"✅ Perfect! Now ask me anything about farming!",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        f"📍 Location set to: **{location}**\n"
                        f"⚠️ Could not fetch weather data. Please check the spelling.\n\n"
                        f"Still, I can help with general farming advice!",
                        parse_mode='Markdown'
                    )
            except Exception as e:
                logger.error(f"Location setting error: {e}")
                await update.message.reply_text(
                    f"📍 Location set to: **{location}**\n"
                    f"✅ Location saved for personalized advice!",
                    parse_mode='Markdown'
                )
        else:
            # Ask for location sharing
            await self.ask_for_location(update, context)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        message = update.message.text
        
        # Check if user has location set
        user_location = self.user_sessions.get(user_id, {}).get('location')
        
        # If no location is set, ask for it first
        if not user_location:
            await update.message.reply_text(
                "📍 I notice you haven't shared your location yet. This helps me provide accurate weather and market prices for your area."
            )
            await self.ask_for_location(update, context)
            return
        
        try:
            # Process the query using our AI agent
            user_context = self.user_sessions.get(user_id, {})
            
            # Check if OpenAI is configured
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key or openai_key == 'your_openai_api_key_here':
                response = await self.handle_query_without_ai(message, user_location, user_context)
            else:
                response = await agri_agent.process_query(
                    query=message,
                    location=user_location,
                    user_context=user_context
                )
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Message handling error: {e}")
            await update.message.reply_text(
                "Sorry, I encountered an error processing your message. Please try again or ask a different question."
            )

    async def handle_query_without_ai(self, query: str, location: str, user_context: dict) -> str:
        """Handle queries when OpenAI is not configured"""
        query_lower = query.lower()
        
        # Weather queries
        if any(word in query_lower for word in ["weather", "temperature", "rain", "climate"]):
            if location:
                try:
                    weather_data = await agri_agent.get_weather_data(location)
                    if "error" not in weather_data:
                        current = weather_data.get("current", {})
                        return f"🌤️ Current Weather in {location}:\n\n" \
                               f"🌡️ Temperature: {current.get('temperature', 'N/A')}°C\n" \
                               f"☁️ Conditions: {current.get('description', 'N/A')}\n" \
                               f"💧 Humidity: {current.get('humidity', 'N/A')}%\n" \
                               f"💨 Wind Speed: {current.get('wind_speed', 'N/A')} m/s"
                    else:
                        return f"Sorry, I couldn't fetch weather data for {location}. Please check the location name."
                except Exception as e:
                    return f"Error fetching weather data: {str(e)}"
        
        # Price queries
        elif any(word in query_lower for word in ["price", "cost", "rate", "market"]):
            try:
                commodities = ["onion", "tomato", "potato", "rice", "wheat", "cotton", "sugarcane"]
                commodity = None
                for c in commodities:
                    if c in query_lower:
                        commodity = c
                        break
                
                price_data = await agri_agent.get_commodity_prices(commodity, user_location="Vijayawada")
                if "error" not in price_data:
                    data = price_data.get("data", [])
                    if data:
                        response = f"💰 Current Market Prices"
                        if commodity:
                            response += f" for {commodity.title()}"
                        response += ":\n\n"
                        
                        for record in data[:5]:
                            commodity_name = record.get("commodity", "Unknown")
                            market = record.get("market", "Unknown")
                            price = record.get("modal_price", "N/A")
                            response += f"📈 {commodity_name} at {market}: ₹{price}/quintal\n"
                        return response
                    else:
                        return "No current price data available."
                else:
                    return "Sorry, I couldn't fetch price data at the moment."
            except Exception as e:
                return f"Error fetching price data: {str(e)}"
        
        # General response
        else:
            return ("🌾 **BhoomiSetu Agricultural Advisor**\n\n"
                    "I can help you with:\n"
                    "• **Weather forecasts** - 'weather today'\n"
                    "• **Market prices** - 'tomato prices'\n"
                    "• **Irrigation advice** - 'when to water crops'\n"
                    "• **Government schemes** - 'loan information'\n"
                    "• **Crop guidance** - 'which seeds to plant'\n\n"
                    "Try asking specific questions!")

    def run(self):
        """Start the Telegram bot"""
        # Create application
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("location", self.set_location))
        application.add_handler(MessageHandler(filters.LOCATION, self.handle_location))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start the bot
        application.run_polling()

# Create bot instance
telegram_bot = TelegramBot()

if __name__ == "__main__":
    telegram_bot.run()
