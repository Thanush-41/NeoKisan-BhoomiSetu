"""
Core Agricultural AI Agent
Handles multilingual queries about farming, weather, crops, financing, and policies
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
import openai
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgricultureAIAgent:
    def __init__(self):
        print("🤖 DEBUG: Initializing AgricultureAIAgent...")
        
        # Initialize OpenAI client (if available)
        openai_key = os.getenv('OPENAI_API_KEY')
        print(f"🔑 DEBUG: OpenAI key found: {bool(openai_key and openai_key != 'your_openai_api_key_here')}")
        if openai_key and openai_key != 'your_openai_api_key_here':
            self.openai_client = openai.OpenAI(api_key=openai_key)
        else:
            self.openai_client = None
            
        # Initialize Groq API settings
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        print(f"🔑 DEBUG: Groq key found: {bool(self.groq_api_key)}")
        if self.groq_api_key:
            print(f"🔑 DEBUG: Groq key starts with: {self.groq_api_key[:10]}...")
        self.groq_base_url = "https://api.groq.com/openai/v1"
        
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.data_gov_api_key = os.getenv('DATA_GOV_API_KEY')
        
        # Initialize knowledge base
        self.crop_knowledge = self._load_crop_knowledge()
        self.financial_schemes = self._load_financial_schemes()
        
        print("✅ DEBUG: AgricultureAIAgent initialization complete")

    def _load_crop_knowledge(self) -> Dict:
        """Load crop-specific knowledge base"""
        return {
            "rice": {
                "water_requirement": "1200-1500mm",
                "growth_stages": ["germination", "tillering", "booting", "flowering", "maturity"],
                "critical_irrigation": ["tillering", "flowering"],
                "diseases": ["blast", "blight", "sheath_rot"],
                "varieties": {
                    "short_duration": ["IR64", "Swarna", "BPT5204"],
                    "medium_duration": ["MTU1010", "JGL1798"],
                    "long_duration": ["Tellahamsa", "WGL44"]
                }
            },
            "wheat": {
                "water_requirement": "450-650mm",
                "growth_stages": ["germination", "tillering", "jointing", "booting", "flowering", "maturity"],
                "critical_irrigation": ["crown_root_initiation", "tillering", "flowering"],
                "diseases": ["rust", "blight", "smut"],
                "varieties": {
                    "early_sowing": ["HD2967", "DBW88"],
                    "late_sowing": ["HD3086", "PBW725"],
                    "heat_tolerant": ["HD2932", "WH1105"]
                }
            },
            "cotton": {
                "water_requirement": "700-1300mm",
                "growth_stages": ["germination", "squaring", "flowering", "boll_development", "maturity"],
                "critical_irrigation": ["flowering", "boll_development"],
                "diseases": ["bollworm", "whitefly", "leaf_curl"],
                "varieties": {
                    "bt_cotton": ["RCH2", "Mahyco_MRC7017"],
                    "non_bt": ["Suraj", "LRA5166"],
                    "hybrid": ["RCH773", "Ankur3028"]
                }
            }
        }

    def _load_financial_schemes(self) -> Dict:
        """Load government schemes and financial options"""
        return {
            "central_schemes": {
                "PM_KISAN": {
                    "description": "Direct income support to farmers",
                    "amount": "Rs. 6000 per year",
                    "eligibility": "All landholding farmers",
                    "application": "Online at pmkisan.gov.in"
                },
                "KCC": {
                    "description": "Kisan Credit Card for crop loans",
                    "interest_rate": "7% (with subsidy 4%)",
                    "eligibility": "Farmers, tenant farmers, SHGs",
                    "application": "Any nationalized bank"
                },
                "PMFBY": {
                    "description": "Crop insurance scheme",
                    "premium": "2% for Kharif, 1.5% for Rabi",
                    "coverage": "All crops, all risks",
                    "application": "Through banks or online"
                }
            },
            "state_schemes": {
                "telangana": {
                    "rythu_bandhu": "Rs. 10,000 per acre per year",
                    "rythu_bima": "Life insurance for farmers"
                },
                "andhra_pradesh": {
                    "ysr_rythu_bharosa": "Rs. 13,500 per year",
                    "zero_interest_loans": "Up to Rs. 1 lakh"
                }
            }
        }

    async def detect_language(self, text: str) -> str:
        """Detect the language of input text using OpenAI"""
        try:
            # Simple language detection based on script
            if any('\u0900' <= c <= '\u097F' for c in text):
                return 'hi'  # Hindi
            elif any('\u0C00' <= c <= '\u0C7F' for c in text):
                return 'te'  # Telugu
            else:
                return 'en'  # Default to English
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return 'en'  # Default to English

    async def translate_text(self, text: str, target_lang: str = 'en') -> str:
        """Translate text using OpenAI (simplified)"""
        try:
            if target_lang == 'en':
                return text
            
            # For now, return the original text
            # In production, you could use OpenAI for translation
            return text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    async def get_weather_data(self, location: str) -> Dict:
        """Fetch weather data from OpenWeather API"""
        try:
            # Current weather
            current_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.weather_api_key}&units=metric"
            current_response = requests.get(current_url)
            current_data = current_response.json()
            
            # 5-day forecast
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={self.weather_api_key}&units=metric"
            forecast_response = requests.get(forecast_url)
            forecast_data = forecast_response.json()
            
            return {
                "current": {
                    "temperature": current_data["main"]["temp"],
                    "humidity": current_data["main"]["humidity"],
                    "description": current_data["weather"][0]["description"],
                    "wind_speed": current_data["wind"]["speed"],
                    "pressure": current_data["main"]["pressure"]
                },
                "forecast": forecast_data["list"][:5]  # Next 5 forecasts
            }
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return {"error": "Unable to fetch weather data"}

    async def get_commodity_prices(self, commodity: str = None) -> Dict:
        """Fetch commodity prices from data.gov.in API"""
        try:
            url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
            params = {
                "api-key": self.data_gov_api_key,
                "format": "json",
                "limit": 100
            }
            
            if commodity:
                params["filters[commodity]"] = commodity
                
            response = requests.get(url, params=params)
            data = response.json()
            
            return {
                "status": "success",
                "data": data.get("records", []),
                "count": len(data.get("records", []))
            }
        except Exception as e:
            logger.error(f"Commodity price API error: {e}")
            return {"error": "Unable to fetch commodity prices"}

    def classify_query(self, query: str) -> str:
        """Classify the type of agricultural query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["irrigate", "water", "irrigation", "watering"]):
            return "irrigation"
        elif any(word in query_lower for word in ["seed", "variety", "crop", "plant", "sow"]):
            return "crop_selection"
        elif any(word in query_lower for word in ["weather", "temperature", "rain", "climate"]):
            return "weather"
        elif any(word in query_lower for word in ["price", "market", "sell", "cost", "profit"]):
            return "market"
        elif any(word in query_lower for word in ["loan", "credit", "scheme", "subsidy", "finance", "money"]):
            return "finance"
        elif any(word in query_lower for word in ["disease", "pest", "fungus", "insect", "spray"]):
            return "pest_disease"
        else:
            return "general"

    async def process_query(self, query: str, location: str = None, user_context: Dict = None) -> str:
        """Main method to process agricultural queries"""
        try:
            print(f"🤖 DEBUG: Processing query: '{query}' | Location: '{location}'")
            
            # Detect and translate if needed
            detected_lang = await self.detect_language(query)
            english_query = query
            if detected_lang != 'en':
                english_query = await self.translate_text(query, 'en')
            
            # Classify query type
            query_type = self.classify_query(english_query)
            print(f"🤖 DEBUG: Query type classified as: '{query_type}'")
            
            # Gather relevant data based on query type
            context_data = {}
            
            if location:
                weather_data = await self.get_weather_data(location)
                context_data["weather"] = weather_data
            
            if query_type in ["market", "crop_selection"]:
                commodity_data = await self.get_commodity_prices()
                context_data["prices"] = commodity_data
            
            # Generate response based on query type
            if query_type == "irrigation":
                response = await self._handle_irrigation_query(english_query, context_data, user_context)
            elif query_type == "crop_selection":
                response = await self._handle_crop_selection_query(english_query, context_data, user_context)
            elif query_type == "weather":
                response = await self._handle_weather_query(english_query, context_data, user_context)
            elif query_type == "market":
                response = await self._handle_market_query(english_query, context_data, user_context)
            elif query_type == "finance":
                response = await self._handle_finance_query(english_query, context_data, user_context)
            elif query_type == "pest_disease":
                response = await self._handle_pest_disease_query(english_query, context_data, user_context)
            else:
                response = await self._handle_general_query(english_query, context_data, user_context)
            
            # Translate back to original language if needed
            if detected_lang != 'en':
                response = await self.translate_text(response, detected_lang)
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return "I'm sorry, I encountered an error while processing your query. Please try again."

    async def _handle_irrigation_query(self, query: str, context_data: Dict, user_context: Dict) -> str:
        """Handle irrigation-related queries"""
        try:
            weather_info = context_data.get("weather", {})
            crop_type = user_context.get("crop_type", "general") if user_context else "general"
            soil_conditions = user_context.get("soil_conditions", "unknown") if user_context else "unknown"
            
            prompt = f"""
            You are an expert agricultural advisor specializing in irrigation management.
            
            Weather Data: {json.dumps(weather_info, indent=2)}
            Crop Type: {crop_type}
            Soil Conditions: {soil_conditions}
            
            Farmer's Question: {query}
            
            Provide practical, actionable advice about irrigation timing and methods. Consider:
            - Current weather conditions and forecast
            - Crop growth stage and water requirements
            - Soil moisture and drainage
            - Water conservation techniques
            - Cost-effective irrigation methods
            
            Answer in simple, clear language that a farmer can understand and implement.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert agricultural advisor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Irrigation query error: {e}")
            return "I can help with irrigation advice. Please provide your location and crop type for better recommendations."

    async def _handle_crop_selection_query(self, query: str, context_data: Dict, user_context: Dict) -> str:
        """Handle crop selection queries"""
        try:
            weather_info = context_data.get("weather", {})
            price_info = context_data.get("prices", {})
            region = user_context.get("region", "unknown") if user_context else "unknown"
            soil_type = user_context.get("soil_type", "unknown") if user_context else "unknown"
            
            prompt = f"""
            You are an expert agricultural advisor specializing in crop selection and planning.
            
            Weather Forecast: {json.dumps(weather_info, indent=2)}
            Soil Type: {soil_type}
            Region: {region}
            Current Market Prices: {json.dumps(price_info, indent=2)}
            
            Farmer's Question: {query}
            
            Recommend suitable crop varieties considering:
            - Climate resilience and weather patterns
            - Soil compatibility and nutrient requirements
            - Market demand and price trends
            - Disease resistance and pest management
            - Input costs and profitability
            
            Provide specific variety names when possible and explain your reasoning.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert agricultural advisor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Crop selection query error: {e}")
            return "I can help you choose the right crop varieties. Please provide your location and soil type for better recommendations."

    async def _handle_weather_query(self, query: str, context_data: Dict, user_context: Dict) -> str:
        """Handle weather-related queries"""
        weather_info = context_data.get("weather", {})
        
        if "error" in weather_info:
            return "I couldn't fetch current weather data. Please check your location and try again."
        
        current = weather_info.get("current", {})
        forecast = weather_info.get("forecast", [])
        
        response = f"Current Weather:\n"
        response += f"🌡️ Temperature: {current.get('temperature', 'N/A')}°C\n"
        response += f"💧 Humidity: {current.get('humidity', 'N/A')}%\n"
        response += f"🌤️ Conditions: {current.get('description', 'N/A')}\n"
        response += f"💨 Wind Speed: {current.get('wind_speed', 'N/A')} m/s\n\n"
        
        if forecast:
            response += "5-Day Forecast:\n"
            for i, day in enumerate(forecast[:5]):
                date = datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')
                temp = day['main']['temp']
                desc = day['weather'][0]['description']
                response += f"{date}: {temp}°C, {desc}\n"
        
        return response

    async def _handle_market_query(self, query: str, context_data: Dict, user_context: Dict) -> str:
        """Handle market price queries"""
        price_info = context_data.get("prices", {})
        
        if "error" in price_info:
            return "I couldn't fetch current market prices. Please try again later."
        
        data = price_info.get("data", [])
        
        if not data:
            return "No market price data available at the moment."
        
        response = "Current Market Prices:\n\n"
        
        # Group by commodity
        commodities = {}
        for record in data[:10]:  # Limit to 10 records
            commodity = record.get("commodity", "Unknown")
            market = record.get("market", "Unknown")
            price = record.get("modal_price", "N/A")
            
            if commodity not in commodities:
                commodities[commodity] = []
            commodities[commodity].append(f"{market}: ₹{price}")
        
        for commodity, prices in commodities.items():
            response += f"📈 {commodity}:\n"
            for price in prices[:3]:  # Limit to 3 markets per commodity
                response += f"  • {price}\n"
            response += "\n"
        
        return response

    async def _handle_finance_query(self, query: str, context_data: Dict, user_context: Dict) -> str:
        """Handle financial and scheme queries"""
        try:
            location = user_context.get("location", "unknown") if user_context else "unknown"
            schemes = json.dumps(self.financial_schemes, indent=2)
            credit_options = "Banks, NBFCs, Cooperative societies, SHGs"
            
            prompt = f"""
            You are an expert in agricultural finance and government schemes.
            
            Available Schemes: {schemes}
            Credit Options: {credit_options}
            Location: {location}
            
            Farmer's Question: {query}
            
            Provide information about:
            - Relevant government schemes and subsidies
            - Loan options and eligibility criteria
            - Application processes and required documents
            - Interest rates and repayment terms
            - Contact details for local offices
            
            Make the information actionable and location-specific.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in agricultural finance."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Finance query error: {e}")
            return "I can help with information about agricultural loans and government schemes. Please specify your location for more relevant information."

    async def _handle_pest_disease_query(self, query: str, context_data: Dict, user_context: Dict) -> str:
        """Handle pest and disease queries"""
        crop_type = user_context.get("crop_type", "general") if user_context else "general"
        
        response = f"For {crop_type} pest and disease management:\n\n"
        
        if crop_type.lower() in self.crop_knowledge:
            diseases = self.crop_knowledge[crop_type.lower()].get("diseases", [])
            response += f"Common diseases in {crop_type}:\n"
            for disease in diseases:
                response += f"• {disease.title()}\n"
            response += "\n"
        
        response += "General recommendations:\n"
        response += "• Regular field monitoring\n"
        response += "• Use disease-resistant varieties\n"
        response += "• Follow integrated pest management (IPM)\n"
        response += "• Consult local agricultural extension officer\n"
        response += "• Use recommended pesticides as per label instructions\n"
        
        return response

    async def _call_groq_api(self, messages: List[Dict], is_agricultural: bool = True) -> str:
        """Call Groq API for general or agricultural questions"""
        try:
            print(f"🚀 DEBUG: Calling Groq API with {len(messages)} messages")
            print(f"🚀 DEBUG: Groq API key available: {bool(self.groq_api_key)}")
            
            if not self.groq_api_key:
                print("❌ DEBUG: No Groq API key found")
                return "AI service is temporarily unavailable. Please try again later."
                
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            # Adjust system message based on query type
            if is_agricultural:
                system_msg = "You are an expert agricultural advisor helping Indian farmers. Provide practical, actionable advice in simple language. Focus on Indian farming conditions, crops, and practices."
            else:
                system_msg = "You are a knowledgeable and helpful AI assistant. Provide accurate, clear, and useful information on any topic. Be friendly and conversational while maintaining accuracy."
            
            # Update system message if present
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] = system_msg
            else:
                messages.insert(0, {"role": "system", "content": system_msg})
            
            payload = {
                "messages": messages,
                "model": "llama3-8b-8192",  # Using Groq's Llama model
                "stream": False,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            print(f"🚀 DEBUG: Sending request to: {self.groq_base_url}/chat/completions")
            print(f"🚀 DEBUG: Payload: {payload}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.groq_base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                print(f"🚀 DEBUG: Groq response status: {response.status_code}")
                print(f"🚀 DEBUG: Groq response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"🚀 DEBUG: Groq response successful")
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    print(f"❌ DEBUG: Groq API error: {response.status_code} - {response.text}")
                    return "I'm sorry, I'm having trouble processing your request right now. Please try again."
                    
        except Exception as e:
            print(f"❌ DEBUG: Groq API call exception: {e}")
            return "I'm sorry, I encountered an error while processing your question. Please try again."

    async def _handle_general_query(self, query: str, context_data: Dict, user_context: Dict) -> str:
        """Handle general queries - both agricultural and non-agricultural"""
        try:
            print(f"🧠 DEBUG: Handling general query: '{query}'")
            
            # Determine if this is an agricultural query
            agricultural_keywords = [
                'crop', 'plant', 'farm', 'agriculture', 'soil', 'irrigation', 'pest', 'disease',
                'fertilizer', 'seed', 'harvest', 'cultivation', 'rice', 'wheat', 'cotton',
                'tomato', 'onion', 'potato', 'market', 'price', 'weather', 'rain', 'season',
                'kharif', 'rabi', 'loan', 'scheme', 'subsidy', 'insurance', 'water'
            ]
            
            query_lower = query.lower()
            is_agricultural = any(keyword in query_lower for keyword in agricultural_keywords)
            print(f"🧠 DEBUG: Is agricultural query: {is_agricultural}")
            
            messages = [
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            # Add location context if available
            if user_context and user_context.get('location'):
                location_context = f"User location: {user_context['location']}"
                if context_data.get('weather'):
                    weather = context_data['weather']
                    location_context += f"\nCurrent weather: {weather.get('temp')}°C, {weather.get('description')}"
                
                messages.insert(0, {
                    "role": "system",
                    "content": f"Context: {location_context}"
                })
            
            # Try OpenAI first if available, otherwise use Grok
            if self.openai_client:
                print("🧠 DEBUG: Trying OpenAI first...")
                try:
                    if is_agricultural:
                        system_content = "You are an expert agricultural advisor helping Indian farmers. Provide practical, actionable advice in simple language. Focus on Indian farming conditions, crops, and practices."
                    else:
                        system_content = "You are a knowledgeable and helpful AI assistant. Provide accurate, clear, and useful information on any topic. Be friendly and conversational while maintaining accuracy."
                    
                    openai_messages = [
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": query}
                    ]
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=openai_messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                    
                    print("✅ DEBUG: OpenAI response successful")
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    print(f"⚠️ DEBUG: OpenAI failed, falling back to Groq: {e}")
                    # Fall through to Groq
            
            # Use Groq API
            print("🧠 DEBUG: Using Groq API...")
            return await self._call_groq_api(messages, is_agricultural)
            
        except Exception as e:
            print(f"❌ DEBUG: General query error: {e}")
            if any(keyword in query.lower() for keyword in ['crop', 'farm', 'agriculture']):
                return "I'm here to help with your agricultural questions. Could you please be more specific about what you'd like to know?"
            else:
                return "I'm here to help answer your questions. Could you please rephrase or provide more details?"

# Initialize the agent
agri_agent = AgricultureAIAgent()
