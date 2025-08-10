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
from openai import AsyncOpenAI
import httpx
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgricultureAIAgent:
    def __init__(self):
        print("🤖 DEBUG: Initializing AgricultureAIAgent...")
        
        # Initialize OpenAI client (if available)
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key != 'your_openai_api_key_here':
            self.openai_client = AsyncOpenAI(api_key=openai_key)
        else:
            self.openai_client = None
            
        # Initialize Groq API settings
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if self.groq_api_key:
            print(f"🔑 DEBUG: Groq key starts with: {self.groq_api_key[:10]}...")
        self.groq_base_url = "https://api.groq.com/openai/v1"
        
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.data_gov_api_key = os.getenv('DATA_GOV_API_KEY')
        
        # Initialize knowledge base
        self.crop_knowledge = self._load_crop_knowledge()
        self.financial_schemes = self._load_financial_schemes()
        
        # Initialize soil data
        self.soil_data = self._load_soil_data()
        self.location_soil_mapping = self._get_location_soil_mapping()
        
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

    def _load_soil_data(self) -> Dict:
        """Load soil dataset from CSV file"""
        try:
            import pandas as pd
            import os
            
            # Path to the soil dataset
            csv_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data_core.csv")
            
            if not os.path.exists(csv_file_path):
                print(f"⚠️ DEBUG: Soil dataset not found at {csv_file_path}")
                return {}
            
            # Load the dataset
            soil_df = pd.read_csv(csv_file_path)
            print(f"📊 DEBUG: Loaded soil dataset with {len(soil_df)} records")
            
            # Group data by soil type and crop type for quick lookup
            soil_data = {}
            
            for soil_type in soil_df['Soil Type'].unique():
                soil_data[soil_type.lower()] = {
                    'crops': {},
                    'characteristics': {
                        'temperature_range': [
                            soil_df[soil_df['Soil Type'] == soil_type]['Temparature'].min(),
                            soil_df[soil_df['Soil Type'] == soil_type]['Temparature'].max()
                        ],
                        'humidity_range': [
                            soil_df[soil_df['Soil Type'] == soil_type]['Humidity'].min(),
                            soil_df[soil_df['Soil Type'] == soil_type]['Humidity'].max()
                        ],
                        'moisture_range': [
                            soil_df[soil_df['Soil Type'] == soil_type]['Moisture'].min(),
                            soil_df[soil_df['Soil Type'] == soil_type]['Moisture'].max()
                        ]
                    }
                }
                
                # Group crop recommendations by soil type
                soil_crops = soil_df[soil_df['Soil Type'] == soil_type]
                for _, row in soil_crops.iterrows():
                    crop = row['Crop Type'].lower()
                    if crop not in soil_data[soil_type.lower()]['crops']:
                        soil_data[soil_type.lower()]['crops'][crop] = []
                    
                    soil_data[soil_type.lower()]['crops'][crop].append({
                        'fertilizer': row['Fertilizer Name'],
                        'nitrogen': row['Nitrogen'],
                        'potassium': row['Potassium'],
                        'phosphorous': row['Phosphorous'],
                        'ideal_temp': row['Temparature'],
                        'ideal_humidity': row['Humidity'],
                        'ideal_moisture': row['Moisture']
                    })
            
            print(f"✅ DEBUG: Processed soil data for {len(soil_data)} soil types")
            return soil_data
            
        except Exception as e:
            print(f"❌ DEBUG: Error loading soil data: {e}")
            return {}

    def _get_location_soil_mapping(self) -> Dict:
        """Map Indian locations to predominant soil types"""
        return {
            # Andhra Pradesh
            "vijayawada": "black",
            "guntur": "black", 
            "visakhapatnam": "red",
            "tirupati": "red",
            "nellore": "clayey",
            "kadapa": "red",
            "kurnool": "black",
            "anantapur": "red",
            "chittoor": "red",
            "east godavari": "clayey",
            "west godavari": "clayey",
            "krishna": "black",
            "prakasam": "sandy",
            "srikakulam": "red",
            "vizianagaram": "red",
            
            # Telangana
            "hyderabad": "black",
            "warangal": "black",
            "nizamabad": "black",
            "karimnagar": "black",
            "khammam": "red",
            "mahbubnagar": "red",
            "rangareddy": "black",
            "medak": "black",
            "nalgonda": "black",
            "adilabad": "black",
            
            # Karnataka
            "bangalore": "red",
            "bengaluru": "red",
            "mysore": "red",
            "hubli": "black",
            "belgaum": "black",
            "mangalore": "red",
            "gulbarga": "black",
            "davangere": "red",
            "bellary": "red",
            "bijapur": "black",
            
            # Tamil Nadu
            "chennai": "red",
            "coimbatore": "red",
            "madurai": "black",
            "salem": "red",
            "tirupur": "red",
            "erode": "red",
            "vellore": "red",
            "thanjavur": "clayey",
            "tiruchirappalli": "black",
            "kanyakumari": "red",
            
            # Maharashtra
            "mumbai": "red",
            "pune": "black",
            "nagpur": "black",
            "aurangabad": "black",
            "solapur": "black",
            "nashik": "black",
            "kolhapur": "red",
            "satara": "red",
            "sangli": "black",
            "latur": "black",
            
            # Gujarat
            "ahmedabad": "sandy",
            "surat": "black",
            "vadodara": "black",
            "rajkot": "black",
            "bhavnagar": "black",
            "gandhinagar": "sandy",
            
            # Rajasthan
            "jaipur": "sandy",
            "jodhpur": "sandy",
            "udaipur": "red",
            "kota": "black",
            "bikaner": "sandy",
            "ajmer": "sandy",
            
            # Uttar Pradesh
            "lucknow": "loamy",
            "kanpur": "loamy",
            "agra": "loamy",
            "varanasi": "loamy",
            "meerut": "loamy",
            "allahabad": "loamy",
            "prayagraj": "loamy",
            
            # Punjab
            "ludhiana": "loamy",
            "amritsar": "loamy",
            "jalandhar": "loamy",
            "patiala": "loamy",
            "bathinda": "loamy",
            
            # Haryana
            "gurgaon": "loamy",
            "faridabad": "loamy",
            "panipat": "loamy",
            "ambala": "loamy",
            "karnal": "loamy",
            
            # Default mappings
            "delhi": "loamy",
            "new delhi": "loamy",
            "kolkata": "clayey",
            "bhubaneswar": "red",
            "patna": "loamy",
            "ranchi": "red",
            "guwahati": "red",
            "imphal": "red",
            "agartala": "clayey"
        }

    def _format_response_for_chat(self, response: str) -> str:
        """Format response with HTML for proper rendering in web chat interface"""
        if not response:
            return response
        
        import re
        
        # First, handle bold text properly
        response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response)
        
        # Convert markdown headers to HTML with proper spacing
        response = re.sub(r'^### (.*?)$', r'<br><br><strong>\1</strong>', response, flags=re.MULTILINE)
        response = re.sub(r'^## (.*?)$', r'<br><br><strong>\1</strong>', response, flags=re.MULTILINE)
        response = re.sub(r'^# (.*?)$', r'<br><br><strong>\1</strong>', response, flags=re.MULTILINE)
        
        # Format bullet points - handle both - and • 
        response = re.sub(r'^- (.*?)$', r'<br>• \1', response, flags=re.MULTILINE)
        response = re.sub(r'^• (.*?)$', r'<br>• \1', response, flags=re.MULTILINE)
        
        # Format numbered lists
        response = re.sub(r'^(\d+)\. (.*?)$', r'<br><br>\1. \2', response, flags=re.MULTILINE)
        
        # Convert regular newlines to HTML breaks
        response = re.sub(r'\n\s*\n', '<br><br>', response)  # Double newlines
        response = re.sub(r'\n', '<br>', response)  # Single newlines
        
        # Clean up multiple breaks
        response = re.sub(r'(<br>\s*){3,}', '<br><br>', response)
        
        # Remove leading breaks
        response = re.sub(r'^(<br>\s*)+', '', response)
        
        return response.strip()

    def get_soil_data_for_location(self, location: str) -> Dict:
        """Get soil type and characteristics for a given location"""
        try:
            if not hasattr(self, 'soil_data'):
                self.soil_data = self._load_soil_data()
            
            if not hasattr(self, 'location_soil_mapping'):
                self.location_soil_mapping = self._get_location_soil_mapping()
            
            # Clean and normalize location name
            location_clean = location.lower().strip()
            
            # Find soil type for location
            soil_type = None
            for loc, soil in self.location_soil_mapping.items():
                if loc in location_clean or location_clean in loc:
                    soil_type = soil
                    break
            
            # Default to black soil if location not found (common in India)
            if not soil_type:
                soil_type = "black"
                print(f"🌍 DEBUG: Location '{location}' not found in mapping, defaulting to black soil")
            
            # Get soil characteristics and crop recommendations
            soil_info = self.soil_data.get(soil_type, {})
            
            result = {
                "location": location,
                "soil_type": soil_type.title(),
                "characteristics": soil_info.get('characteristics', {}),
                "suitable_crops": list(soil_info.get('crops', {}).keys()),
                "crop_recommendations": soil_info.get('crops', {})
            }
            
            print(f"🌱 DEBUG: Soil data for {location}: {soil_type.title()} soil with {len(result['suitable_crops'])} suitable crops")
            return result
            
        except Exception as e:
            print(f"❌ DEBUG: Error getting soil data for {location}: {e}")
            return {
                "location": location,
                "soil_type": "Mixed",
                "characteristics": {},
                "suitable_crops": [],
                "crop_recommendations": {}
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

    def _get_current_season(self) -> str:
        """Get current agricultural season based on month"""
        month = datetime.now().month
        if month in [6, 7, 8, 9]:  # June-September
            return "Kharif (Monsoon season)"
        elif month in [10, 11, 12, 1, 2, 3]:  # October-March
            return "Rabi (Winter season)"
        else:  # April-May
            return "Zaid (Summer season)"

    async def get_weather_data(self, location: str) -> Dict:
        """Fetch weather data from OpenWeather API"""
        try:
            print(f"🌤️ DEBUG: Starting weather fetch for location: '{location}'")
            
            # Current weather
            current_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.weather_api_key}&units=metric"
            print(f"🌐 DEBUG: Making API request to: {current_url}")
            
            current_response = requests.get(current_url)
            print(f"📡 DEBUG: Weather API response status: {current_response.status_code}")
            
            if current_response.status_code != 200:
                current_data = current_response.json()
                print(f"❌ DEBUG: Weather API error response: {current_data}")
                error_message = current_data.get("message", "Unknown error")
                print(f"⚠️ DEBUG: Weather API failed: {error_message}")
                return {"error": f"Weather API error: {error_message}"}
            
            current_data = current_response.json()
            print(f"✅ DEBUG: Successfully fetched current weather data")
            print(f"📍 DEBUG: Location found: {current_data.get('name', 'Unknown')}, {current_data.get('sys', {}).get('country', 'Unknown')}")
            print(f"🌡️ DEBUG: Temperature: {current_data['main']['temp']}°C")
            print(f"🌤️ DEBUG: Conditions: {current_data['weather'][0]['description']}")
            
            # 5-day forecast
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={self.weather_api_key}&units=metric"
            print(f"🌐 DEBUG: Fetching forecast from: {forecast_url}")
            
            forecast_response = requests.get(forecast_url)
            print(f"📡 DEBUG: Forecast API response status: {forecast_response.status_code}")
            
            forecast_data = {}
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                print(f"✅ DEBUG: Successfully fetched forecast data with {len(forecast_data.get('list', []))} entries")
            else:
                print(f"⚠️ DEBUG: Forecast API failed with status {forecast_response.status_code}")
            
            location_name = current_data.get("name", location)
            country = current_data.get("sys", {}).get("country", "")
            full_location = f"{location_name}, {country}" if country else location_name
            
            print(f"✅ DEBUG: Weather data compiled for: {full_location}")
            
            return {
                "location": {
                    "name": full_location,
                    "requested": location
                },
                "current": {
                    "temperature": current_data["main"]["temp"],
                    "humidity": current_data["main"]["humidity"],
                    "description": current_data["weather"][0]["description"],
                    "wind_speed": current_data["wind"]["speed"],
                    "pressure": current_data["main"]["pressure"]
                },
                "forecast": forecast_data.get("list", [])[:5] if forecast_response.status_code == 200 else []
            }
        except requests.exceptions.RequestException as e:
            print(f"🌐 DEBUG: Network error during weather fetch: {e}")
            logger.error(f"Weather API network error: {e}")
            return {"error": f"Network error: Unable to reach weather service"}
        except KeyError as e:
            print(f"📊 DEBUG: Missing expected data in weather response: {e}")
            logger.error(f"Weather API data error: {e}")
            return {"error": "Weather data format error"}
        except Exception as e:
            print(f"❌ DEBUG: Unexpected error in weather fetch: {e}")
            logger.error(f"Weather API error: {e}")
            return {"error": f"Weather service error: {str(e)}"}

    async def _parse_csv_manually(self, commodity: str = None, user_location: str = None) -> Dict:
        """Manual CSV parsing fallback when pandas is not available"""
        try:
            import csv
            import os
            
            # Path to the comprehensive CSV file
            csv_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                       "9ef84268-d588-465a-a308-a864a43d0070 (2).csv")
            
            print(f"🔍 DEBUG: Manual CSV parsing from: {csv_file_path}")
            
            if not os.path.exists(csv_file_path):
                print(f"⚠️ DEBUG: CSV file not found at {csv_file_path}")
                return {"error": "Local market data file not found"}
            
            all_records = []
            
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                # Check column names
                fieldnames = csv_reader.fieldnames
                print(f"🔍 DEBUG: CSV columns: {fieldnames}")
                
                for row in csv_reader:
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    
                    # Extract data with flexible column naming
                    state = row.get('State', '').strip()
                    district = row.get('District', '').strip()
                    market = row.get('Market', '').strip()
                    commodity_name = row.get('Commodity', '').strip()
                    variety = row.get('Variety', '').strip()
                    grade = row.get('Grade', '').strip()
                    arrival_date = row.get('Arrival_Date', '').strip()
                    
                    # Handle different possible column names for prices
                    min_price = (row.get('Min_x0020_Price', '') or 
                               row.get('Min Price', '') or 
                               row.get('Min_Price', '')).strip()
                    max_price = (row.get('Max_x0020_Price', '') or 
                               row.get('Max Price', '') or 
                               row.get('Max_Price', '')).strip()
                    modal_price = (row.get('Modal_x0020_Price', '') or 
                                 row.get('Modal Price', '') or 
                                 row.get('Modal_Price', '')).strip()
                    
                    # Filter by commodity if specified
                    if commodity:
                        commodity_variations = {
                            'tomato': ['Tomato'],
                            'onion': ['Onion'],
                            'potato': ['Potato'],
                            'rice': ['Paddy(Dhan)(Common)', 'Rice'],
                            'wheat': ['Wheat'],
                            'cotton': ['Cotton'],
                            'groundnut': ['Groundnut'],
                            'maize': ['Maize'],
                            'chilli': ['Dry Chillies', 'Green Chilli'],
                            'turmeric': ['Turmeric'],
                            'banana': ['Banana'],
                            'mango': ['Mango'],
                            'coconut': ['Coconut']
                        }
                        
                        search_terms = commodity_variations.get(commodity.lower(), [commodity])
                        
                        # Check if commodity matches
                        matches = False
                        for term in search_terms:
                            if term.lower() in commodity_name.lower():
                                matches = True
                                break
                        
                        if not matches:
                            continue
                    
                    # Create record
                    record = {
                        "state": state,
                        "district": district,
                        "market": market,
                        "commodity": commodity_name,
                        "variety": variety,
                        "grade": grade,
                        "arrival_date": arrival_date,
                        "min_price": min_price,
                        "max_price": max_price,
                        "modal_price": modal_price
                    }
                    
                    # Add state priority
                    priority_states = ["Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu", "Kerala"]
                    if state in priority_states:
                        record["_state_priority"] = priority_states.index(state)
                    else:
                        record["_state_priority"] = 99
                    
                    all_records.append(record)
            
            print(f"✅ DEBUG: Manual parsing completed, {len(all_records)} records loaded")
            
            # Get available states
            available_states = list(set(record.get("state", "") for record in all_records))
            print(f"🌍 DEBUG: Available states: {sorted(available_states)}")
            
            # Sort by location relevance
            if user_location and all_records:
                def location_score(record):
                    state = record.get("state", "").lower()
                    market = record.get("market", "").lower()
                    district = record.get("district", "").lower()
                    state_priority = record.get("_state_priority", 99)
                    arrival_date = record.get("arrival_date", "")
                    
                    score = 0
                    
                    # State priority (lower number = higher priority)
                    score += (10 - state_priority) * 10000
                    
                    # Date freshness bonus
                    if arrival_date and "05/08/2025" in arrival_date:
                        score += 5000
                    
                    # Location matching for Vijayawada users
                    if user_location.lower() == "vijayawada":
                        if "andhra pradesh" in state:
                            score += 20000
                        if "krishna" in district.lower():
                            score += 15000
                        elif any(nearby in district.lower() for nearby in ["guntur", "west godavari", "east godavari"]):
                            score += 10000
                    
                    # General location matching
                    if user_location and user_location.lower() in market.lower():
                        score += 12000
                    elif user_location and user_location.lower() in district.lower():
                        score += 8000
                    
                    return score
                
                all_records.sort(key=location_score, reverse=True)
                
                # Debug top results
                print(f"🔄 DEBUG: Top 3 markets after manual sorting:")
                for i, record in enumerate(all_records[:3]):
                    market = record.get("market", "Unknown")
                    district = record.get("district", "Unknown")
                    state = record.get("state", "Unknown")
                    commodity_name = record.get("commodity", "Unknown")
                    price = record.get("modal_price", "N/A")
                    print(f"   {i+1}. {market}, {district}, {state} - {commodity_name}: ₹{price}")
            
            return {
                "status": "success",
                "data": all_records,
                "count": len(all_records),
                "available_states": available_states,
                "has_local_data": any(record.get("_state_priority", 99) < 5 for record in all_records)
            }
            
        except Exception as e:
            print(f"⚠️ DEBUG: Manual CSV parsing error: {e}")
            return {"error": f"Error parsing CSV file: {e}"}

    async def classify_query_with_openai(self, query: str, location: str = None, user_context: Dict = None) -> Dict:
        """Use OpenAI for advanced query understanding and intent classification"""
        try:
            if not self.openai_client:
                return await self.classify_query_with_groq(query)
            
            # Get current context
            current_date = datetime.now().strftime("%B %d, %Y")
            current_season = self._get_current_season()
            user_location = location or (user_context.get("location") if user_context else "India")
            
            prompt = f"""You are an expert agricultural AI assistant for Indian farmers. Analyze this query and provide comprehensive classification and recommendations.

Current Context:
- Date: {current_date}
- Season: {current_season}
- User Location: {user_location}
- Weather: {"Available" if self.weather_api_key else "Not available"}

Query: "{query}"

Please analyze and respond with a JSON object containing:

1. "intent": Classify as one of:
   - "weather": Pure weather information queries
   - "weather_agriculture": Weather-related queries with crop/farming context (survival, protection, adaptation)
   - "price": Market price inquiries
   - "crop_advice": Seed varieties, planting advice, farming practices
   - "disease": Pest/disease identification or treatment
   - "financial": Loans, schemes, affordability
   - "general": General agricultural questions

2. "commodity": Extract any crop/commodity mentioned (standardized names like "rice", "wheat", "tomato")

3. "location": Extract location mentioned, or use user's location. Handle typos and common variations.

4. "specific_question": Rephrase the query to be more specific and actionable

5. "recommended_action": Suggest what specific information would help the farmer

6. "context_needed": List what additional context would improve the response

7. "urgent": true/false - is this time-sensitive (pest attack, weather alert, etc.)

8. "confidence": 0-1 score for classification accuracy

Examples:
- "can i afford market to improve" → Focus on financial analysis and improvement suggestions
- "what seed variety suits my region in unpredictable weather" → Focus on climate-resilient varieties for the region
- "disease in my tomato plants" → Focus on disease identification and treatment

Provide actionable, region-specific advice based on Indian agricultural practices."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            print(f"🤖 DEBUG: OpenAI classification response: {result_text}")
            
            # Handle markdown code blocks in response
            if result_text.startswith('```json'):
                # Extract JSON from markdown code block
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    result_text = result_text[json_start:json_end]
            elif result_text.startswith('```'):
                # Handle generic code blocks
                lines = result_text.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith('{') or in_json:
                        in_json = True
                        json_lines.append(line)
                        if line.strip().endswith('}'):
                            break
                result_text = '\n'.join(json_lines)
            
            import json
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            print(f"❌ DEBUG: OpenAI classification failed: {e}")
            return await self.classify_query_with_groq(query)

    async def classify_query_with_groq(self, query: str) -> Dict:
        """Use Groq AI to intelligently classify queries and extract location/commodity info with typo correction"""
        try:
            from groq import Groq
            
            client = Groq(api_key=self.groq_api_key)
            
            prompt = f"""
Analyze this agricultural query and extract information with typo correction:
Query: "{query}"

IMPORTANT: Fix common typos in city names:
- "banglore" → "bangalore"
- "deli" → "delhi"  
- "mumbay" → "mumbai"
- "chenai" → "chennai"
- "kolkatta" → "kolkata"
- "hyderabd" → "hyderabad"
- "vijayawda" → "vijayawada"
- "guntur" → "guntur"
- "vizag" → "visakhapatnam"

SPECIAL HANDLING for location words:
- If query contains "here", "current location", "my location" → set location to null
- Only extract specific city/place names, not generic location words

Please respond in JSON format with:
1. "intent": "price" | "weather" | "weather_agriculture" | "general"
2. "commodity": extracted commodity name (standardized)
3. "location": extracted location (corrected spelling) OR null if "here"/"current location"
4. "corrected_query": query with typos fixed
5. "confidence": 0-1 score

Intent Classification Guidelines:
- "weather": Pure weather information requests
- "weather_agriculture": Weather queries with farming/crop context (survival, protection, adaptation)
- "price": Market price inquiries
- "general": Other agricultural questions

Examples:
- "weather in banglore" → {{"intent": "weather", "commodity": null, "location": "bangalore", "corrected_query": "weather in bangalore", "confidence": 0.95}}
- "how to survive my crops for this temperature" → {{"intent": "weather_agriculture", "commodity": null, "location": null, "corrected_query": "how to survive my crops for this temperature", "confidence": 0.9}}
- "weather here" → {{"intent": "weather", "commodity": null, "location": null, "corrected_query": "weather here", "confidence": 0.95}}
- "tomaot price in bangalor" → {{"intent": "price", "commodity": "tomato", "location": "bangalore", "corrected_query": "tomato price in bangalore", "confidence": 0.9}}
- "protect crops from heat" → {{"intent": "weather_agriculture", "commodity": null, "location": null, "corrected_query": "protect crops from heat", "confidence": 0.85}}

Response (JSON only):
"""
            
            print(f"🤖 DEBUG: Sending query to Groq AI: '{query}'")
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            import json
            result_text = response.choices[0].message.content.strip()
            print(f"🤖 DEBUG: Groq raw response: {result_text}")
            
            # Clean up the response - remove markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            # Try to find JSON within the response
            try:
                # Look for the first { and last } to extract JSON
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_text = result_text[start_idx:end_idx+1]
                    result = json.loads(json_text)
                else:
                    result = json.loads(result_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract just the JSON part
                lines = result_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        result = json.loads(line)
                        break
                else:
                    raise
            
            print(f"🤖 DEBUG: Groq parsed result: {result}")
            
            # Log typo correction
            original_location = None
            corrected_location = result.get("location")
            if "location" in query.lower() or " in " in query.lower():
                # Extract original location from query
                query_parts = query.lower().split(" in ")
                if len(query_parts) > 1:
                    original_location = query_parts[-1].strip()
                    if original_location != corrected_location:
                        print(f"🔧 DEBUG: Typo corrected: '{original_location}' → '{corrected_location}'")
            
            return result
            
        except Exception as e:
            print(f"⚠️ DEBUG: Groq classification failed: {e}")
            # Fallback to simple classification with manual typo correction
            query_lower = query.lower()
            
            # Manual typo corrections
            location = None
            if " in " in query_lower:
                location_part = query_lower.split(" in ")[-1].strip()
                location_corrections = {
                    "banglore": "bangalore",
                    "bangalor": "bangalore", 
                    "bangaluru": "bangalore",
                    "deli": "delhi",
                    "mumbay": "mumbai",
                    "chenai": "chennai",
                    "kolkatta": "kolkata",
                    "hyderabd": "hyderabad",
                    "vijayawda": "vijayawada",
                    "vizag": "visakhapatnam"
                }
                location = location_corrections.get(location_part, location_part)
                if location != location_part:
                    print(f"🔧 DEBUG: Manual typo correction: '{location_part}' → '{location}'")
            
            return {
                "intent": "price" if any(word in query_lower for word in ["price", "rate", "cost", "market"]) else 
                         "weather" if any(word in query_lower for word in ["weather", "rain", "temperature"]) else "general",
                "commodity": None,
                "location": location,
                "corrected_query": query,
                "confidence": 0.5
            }

    async def get_commodity_prices(self, commodity: str = None, user_location: str = None, original_query: str = None) -> Dict:
        """Intelligent hybrid system: Try API first, fallback to CSV with location awareness and AI classification"""
        try:
            print(f"🧠 DEBUG: Starting intelligent price search...")
            print(f"🧠 DEBUG: Commodity: {commodity}, Location: {user_location}, Query: {original_query}")
            
            # Step 1: Use Groq AI to analyze query if provided
            groq_result = None
            if original_query:
                groq_result = await self.classify_query_with_groq(original_query)
                if groq_result.get("intent") != "price":
                    print(f"🧠 DEBUG: Query intent is {groq_result.get('intent')}, not price-related")
                    return {"error": "Query is not price-related", "intent": groq_result.get("intent")}
                
                # Extract better commodity and location from AI
                if not commodity and groq_result.get("commodity"):
                    commodity = groq_result.get("commodity")
                    print(f"🧠 DEBUG: AI extracted commodity: {commodity}")
                
                if not user_location and groq_result.get("location"):
                    user_location = groq_result.get("location")
                    print(f"🧠 DEBUG: AI extracted location: {user_location}")
            
            # Step 2: Parse specific location requests (e.g., "tomato price in bangalore")
            target_state = None
            target_city = None
            if user_location:
                location_mapping = {
                    "bangalore": {"state": "Karnataka", "city": "Bangalore"},
                    "bengaluru": {"state": "Karnataka", "city": "Bangalore"},
                    "delhi": {"state": "Delhi", "city": "Delhi"},
                    "mumbai": {"state": "Maharashtra", "city": "Mumbai"},
                    "kolkata": {"state": "West Bengal", "city": "Kolkata"},
                    "chennai": {"state": "Tamil Nadu", "city": "Chennai"},
                    "hyderabad": {"state": "Telangana", "city": "Hyderabad"},
                    "vijayawada": {"state": "Andhra Pradesh", "city": "Vijayawada"},
                    "visakhapatnam": {"state": "Andhra Pradesh", "city": "Visakhapatnam"},
                    "guntur": {"state": "Andhra Pradesh", "city": "Guntur"},
                    "tirupati": {"state": "Andhra Pradesh", "city": "Tirupati"}
                }
                
                location_key = user_location.lower()
                if location_key in location_mapping:
                    target_state = location_mapping[location_key]["state"]
                    target_city = location_mapping[location_key]["city"]
                    print(f"🧠 DEBUG: Specific location request - State: {target_state}, City: {target_city}")
            
            # Step 3: Try API first for states that have data
            api_states = ["Bihar", "Gujarat", "Haryana", "Jammu and Kashmir", "Kerala", "Uttarakhand"]
            should_try_api = (not target_state or target_state in api_states or 
                            (target_state and target_state not in ["Andhra Pradesh", "Telangana"]))
            
            api_result = None
            if should_try_api:
                print(f"🌐 DEBUG: Trying API first...")
                try:
                    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
                    params = {
                        "api-key": "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b",
                        "format": "json",
                        "limit": 1000
                    }
                    
                    if commodity:
                        params["filters[commodity]"] = commodity.title()
                    if target_state:
                        params["filters[state]"] = target_state
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                api_data = await response.json()
                                if api_data.get("records"):
                                    print(f"✅ DEBUG: API returned {len(api_data['records'])} records")
                                    api_result = {
                                        "status": "success",
                                        "data": api_data["records"],
                                        "count": len(api_data["records"]),
                                        "source": "api"
                                    }
                                else:
                                    print(f"⚠️ DEBUG: API returned no records")
                            else:
                                print(f"⚠️ DEBUG: API request failed with status {response.status}")
                except Exception as e:
                    print(f"⚠️ DEBUG: API request failed: {e}")
            
            # Step 4: Use CSV data (always as fallback or primary for AP/Telangana)
            csv_result = None
            try:
                try:
                    import pandas as pd
                    use_pandas = True
                except ImportError:
                    print("⚠️ DEBUG: Pandas not available, using built-in CSV reader")
                    import csv
                    use_pandas = False
                
                import os
                
                # Path to the comprehensive CSV file
                csv_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                           "9ef84268-d588-465a-a308-a864a43d0070 (2).csv")
                
                print(f"📊 DEBUG: Loading CSV data from: {csv_file_path}")
                
                if os.path.exists(csv_file_path):
                    if use_pandas:
                        df = pd.read_csv(csv_file_path)
                        print(f"✅ DEBUG: Loaded {len(df)} records from CSV using pandas")
                        
                        # Filter by target state if specified
                        if target_state:
                            df = df[df['State'].str.contains(target_state, case=False, na=False)]
                            print(f"🎯 DEBUG: Filtered to {len(df)} records for state: {target_state}")
                    else:
                        # Fallback to built-in csv module
                        with open(csv_file_path, 'r', encoding='utf-8') as file:
                            csv_reader = csv.DictReader(file)
                            df_data = list(csv_reader)
                        print(f"✅ DEBUG: Loaded {len(df_data)} records from CSV using built-in csv")
                        
                        # Filter by target state if specified
                        if target_state:
                            df_data = [row for row in df_data if target_state.lower() in row.get('State', '').lower()]
                            print(f"🎯 DEBUG: Filtered to {len(df_data)} records for state: {target_state}")
                    
                    # Filter by commodity if specified
                    if commodity:
                        commodity_variations = {
                            'tomato': ['Tomato'],
                            'onion': ['Onion'],
                            'potato': ['Potato'],
                            'rice': ['Paddy(Dhan)(Common)', 'Rice'],
                            'wheat': ['Wheat'],
                            'cotton': ['Cotton'],
                            'groundnut': ['Groundnut'],
                            'maize': ['Maize'],
                            'chilli': ['Dry Chillies', 'Green Chilli'],
                            'turmeric': ['Turmeric'],
                            'banana': ['Banana'],
                            'mango': ['Mango'],
                            'coconut': ['Coconut']
                        }
                        
                        search_terms = commodity_variations.get(commodity.lower(), [commodity])
                        
                        if use_pandas:
                            commodity_filter = df['Commodity'].str.contains('|'.join(search_terms), case=False, na=False)
                            df = df[commodity_filter]
                            print(f"🎯 DEBUG: Filtered to {len(df)} records for commodity: {commodity}")
                        else:
                            # Filter using built-in csv data
                            filtered_data = []
                            for row in df_data:
                                commodity_val = row.get('Commodity', '')
                                if any(term.lower() in commodity_val.lower() for term in search_terms):
                                    filtered_data.append(row)
                            df_data = filtered_data
                            print(f"🎯 DEBUG: Filtered to {len(df_data)} records for commodity: {commodity}")
                    
                    # Process results
                    if use_pandas and not df.empty:
                        # Convert to records and sort by relevance
                        csv_records = []
                        for _, row in df.iterrows():
                            record = {
                                "state": row['State'],
                                "district": row['District'], 
                                "market": row['Market'],
                                "commodity": row['Commodity'],
                                "variety": row['Variety'],
                                "grade": row['Grade'],
                                "arrival_date": row['Arrival_Date'],
                                "min_price": row['Min_x0020_Price'],
                                "max_price": row['Max_x0020_Price'],
                                "modal_price": row['Modal_x0020_Price']
                            }
                            csv_records.append(record)
                    elif not use_pandas and df_data:
                        # Process using built-in csv data
                        csv_records = []
                        for row in df_data:
                            record = {
                                "state": row.get('State', ''),
                                "district": row.get('District', ''), 
                                "market": row.get('Market', ''),
                                "commodity": row.get('Commodity', ''),
                                "variety": row.get('Variety', ''),
                                "grade": row.get('Grade', ''),
                                "arrival_date": row.get('Arrival_Date', ''),
                                "min_price": row.get('Min_x0020_Price', ''),
                                "max_price": row.get('Max_x0020_Price', ''),
                                "modal_price": row.get('Modal_x0020_Price', '')
                            }
                            csv_records.append(record)
                    
                    if csv_records:
                        # Sort by location relevance
                        if user_location or target_city:
                            def location_score(record):
                                score = 0
                                state = record.get("state", "").lower()
                                market = record.get("market", "").lower()
                                district = record.get("district", "").lower()
                                
                                # Exact location matches
                                if target_city and target_city.lower() in market.lower():
                                    score += 50000
                                elif target_city and target_city.lower() in district.lower():
                                    score += 30000
                                elif user_location and user_location.lower() in market.lower():
                                    score += 40000
                                elif user_location and user_location.lower() in district.lower():
                                    score += 25000
                                
                                # State priority for AP/Telangana users
                                if user_location and user_location.lower() in ["vijayawada", "guntur", "tirupati"]:
                                    if "andhra pradesh" in state:
                                        score += 20000
                                    elif "telangana" in state:
                                        score += 15000
                                
                                return score
                            
                            csv_records.sort(key=location_score, reverse=True)
                        
                        csv_result = {
                            "status": "success",
                            "data": csv_records,
                            "count": len(csv_records),
                            "source": "csv"
                        }
                        print(f"✅ DEBUG: CSV processed {len(csv_records)} relevant records")
                    else:
                        print(f"⚠️ DEBUG: No matching records in CSV")
                else:
                    print(f"⚠️ DEBUG: CSV file not found")
            except Exception as e:
                print(f"⚠️ DEBUG: CSV processing failed: {e}")
            
            # Step 5: Intelligent result selection
            if target_state and target_state in ["Andhra Pradesh", "Telangana"] and csv_result:
                # Prioritize CSV for AP/Telangana
                print(f"🎯 DEBUG: Using CSV data for {target_state}")
                return csv_result
            elif api_result and api_result.get("count", 0) > 0:
                # Use API if available
                print(f"🌐 DEBUG: Using API data")
                return api_result
            elif csv_result and csv_result.get("count", 0) > 0:
                # Fallback to CSV
                print(f"📊 DEBUG: Falling back to CSV data")
                return csv_result
            else:
                # No data found
                return {
                    "status": "success",
                    "data": [],
                    "count": 0,
                    "source": "none",
                    "message": f"No price data found for {commodity or 'requested commodity'}" + 
                              (f" in {target_state or user_location}" if target_state or user_location else "")
                }
            
        except Exception as e:
            print(f"⚠️ DEBUG: Error in intelligent price search: {e}")
            return {"error": f"Error in price search: {e}"}

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
        """Main method to process agricultural queries with enhanced AI understanding"""
        try:
            print(f"🤖 DEBUG: Processing query: '{query}' | Location: '{location}'")
            
            # Detect and translate if needed
            detected_lang = await self.detect_language(query)
            english_query = query
            if detected_lang != 'en':
                english_query = await self.translate_text(query, 'en')
            
            # Use enhanced AI classification (OpenAI if available, fallback to Groq)
            print(f"📝 DEBUG: Starting enhanced AI classification for query: '{english_query}'")
            ai_classification = await self.classify_query_with_openai(english_query, location, user_context)
            
            query_type = ai_classification.get("intent", "general")
            ai_commodity = ai_classification.get("commodity")
            ai_location = ai_classification.get("location")
            specific_question = ai_classification.get("specific_question", english_query)
            recommended_action = ai_classification.get("recommended_action", "")
            is_urgent = ai_classification.get("urgent", False)
            
            print(f"🤖 DEBUG: Enhanced AI classification results:")
            print(f"   Intent: {query_type}")
            print(f"   Commodity: {ai_commodity}")
            print(f"   Location: {ai_location}")
            print(f"   Specific Question: {specific_question}")
            print(f"   Urgent: {is_urgent}")
            
            # Use AI-extracted location if not provided
            effective_location = location or ai_location or (user_context.get("location") if user_context else None)
            print(f"🤖 DEBUG: Effective location: {effective_location}")
            
            # Gather relevant data based on query type
            context_data = {"ai_classification": ai_classification}
            
            # ALWAYS fetch weather data for the effective location first
            print(f"🌤️ DEBUG: Fetching weather data for location: {effective_location}")
            if effective_location:
                weather_data = await self.get_weather_data(effective_location)
                context_data["weather"] = weather_data
                print(f"🌤️ DEBUG: Weather data fetched for {effective_location}")
                
                # ALWAYS fetch soil data for the effective location
                print(f"🌱 DEBUG: Fetching soil data for location: {effective_location}")
                soil_data = self.get_soil_data_for_location(effective_location)
                context_data["soil"] = soil_data
                print(f"🌱 DEBUG: Soil data fetched for {effective_location}: {soil_data.get('soil_type', 'Unknown')} soil")
            else:
                # Use fallback location for weather and soil data
                fallback_location = "Vijayawada"
                weather_data = await self.get_weather_data(fallback_location)
                context_data["weather"] = weather_data
                print(f"🌤️ DEBUG: Using fallback weather data for {fallback_location}")
                
                soil_data = self.get_soil_data_for_location(fallback_location)
                context_data["soil"] = soil_data
                print(f"🌱 DEBUG: Using fallback soil data for {fallback_location}: {soil_data.get('soil_type', 'Unknown')} soil")
            
            # Route to appropriate handlers with weather context already available
            if query_type == "weather":
                response = await self._handle_weather_query(english_query, context_data, user_context)
            elif query_type == "weather_agriculture":
                # Handle weather-agriculture hybrid queries with comprehensive advice
                print(f"🌾 DEBUG: Weather-agriculture query detected, providing comprehensive advice")
                response = await self._handle_weather_agriculture_query(english_query, context_data, user_context)
            elif query_type == "price":
                # For price queries, pass AI-extracted data for location-aware processing
                print(f"💰 DEBUG: Price query detected with AI data:")
                print(f"💰 DEBUG: - Commodity: {ai_commodity}")
                print(f"💰 DEBUG: - Location: {ai_location}")
                print(f"💰 DEBUG: - Original query: '{english_query}'")
                
                # Update user context with AI-extracted location if available
                if ai_location and user_context:
                    user_context["ai_location"] = ai_location
                elif ai_location and not user_context:
                    user_context = {"ai_location": ai_location}
                
                response = await self._handle_market_query(english_query, context_data, user_context)
            elif query_type == "crop_advice":
                response = await self._handle_crop_advice_query(specific_question, context_data, user_context, effective_location)
            elif query_type == "financial":
                response = await self._handle_financial_query(specific_question, context_data, user_context, effective_location)
            elif query_type == "disease":
                response = await self._handle_disease_query(specific_question, context_data, user_context, effective_location)
            else:
                # Enhanced general query handling with context (weather already fetched)
                response = await self._handle_general_query_with_context(specific_question, context_data, user_context, effective_location)
            
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
            
            # Use Groq API for the response
            if self.groq_api_key:
                print("💧 DEBUG: Using Groq for irrigation query")
                messages = [
                    {"role": "system", "content": "You are an expert agricultural advisor specializing in irrigation management for Indian farmers."},
                    {"role": "user", "content": prompt}
                ]
                return await self._call_groq_api(messages)
            elif self.openai_client:
                print("💧 DEBUG: Using OpenAI for irrigation query")
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
            else:
                print("⚠️ DEBUG: No AI API available for irrigation")
                return "I can help with irrigation advice. Please provide your location and crop type for better recommendations."
                
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
            
            # Use Groq API for the response
            if self.groq_api_key:
                print("🌾 DEBUG: Using Groq for crop selection query")
                messages = [
                    {"role": "system", "content": "You are an expert agricultural advisor specializing in crop selection for Indian farmers."},
                    {"role": "user", "content": prompt}
                ]
                return await self._call_groq_api(messages)
            elif self.openai_client:
                print("🌾 DEBUG: Using OpenAI for crop selection query")
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
            else:
                print("⚠️ DEBUG: No AI API available for crop selection")
                return "I can help you choose the right crop varieties. Please provide your location and soil type for better recommendations."
                
        except Exception as e:
            logger.error(f"Crop selection query error: {e}")
            return "I can help you choose the right crop varieties. Please provide your location and soil type for better recommendations."

    async def _handle_weather_query(self, query: str, context_data: Dict, user_context: Dict) -> str:
        """Handle weather-related queries with intelligent crop advice integration"""
        weather_info = context_data.get("weather", {})
        
        print(f"🌤️ DEBUG: Weather handler received data: {weather_info.keys() if weather_info else 'No data'}")
        
        if "error" in weather_info:
            error_msg = weather_info.get("error", "Unknown error")
            print(f"❌ DEBUG: Weather error in handler: {error_msg}")
            
            # Provide helpful error messages based on error type
            if "not found" in error_msg.lower() or "404" in error_msg:
                return f"🌍 I couldn't find weather data for that location. Please check the city name and try again.\n\n💡 Try: 'weather in bangalore' or 'weather in delhi'"
            elif "network" in error_msg.lower():
                return "🌐 I'm having trouble connecting to the weather service. Please try again in a moment."
            else:
                return f"🌤️ I couldn't fetch current weather data: {error_msg}\n\n💡 Please check your location and try again."
        
        current = weather_info.get("current", {})
        forecast = weather_info.get("forecast", [])
        location_name = weather_info.get("location", {}).get("name", "Unknown Location")
        
        print(f"🌤️ DEBUG: Formatting weather response for: {location_name}")
        print(f"🌤️ DEBUG: Current temp: {current.get('temperature', 'N/A')}°C")
        
        # Check if query mentions crops, survival, agriculture, or farming - use AI for advice
        agricultural_keywords = [
            'crop', 'crops', 'survive', 'survival', 'plant', 'plants', 'farming', 'farm',
            'cultivation', 'harvest', 'irrigation', 'seed', 'seeds', 'protect', 'protection',
            'stress', 'damage', 'yield', 'growth', 'soil', 'fertilizer', 'pesticide',
            'rice', 'wheat', 'cotton', 'tomato', 'onion', 'potato', 'maize', 'corn',
            'sugarcane', 'groundnut', 'chilli', 'turmeric', 'banana', 'mango'
        ]
        
        query_lower = query.lower()
        has_agricultural_context = any(keyword in query_lower for keyword in agricultural_keywords)
        
        print(f"🌾 DEBUG: Agricultural context detected: {has_agricultural_context}")
        
        # Start with weather information
        response = f"🌍 **Weather for {location_name}**\n\n"
        response += f"**Current Conditions:**\n"
        response += f"🌡️ Temperature: {current.get('temperature', 'N/A')}°C\n"
        response += f"💧 Humidity: {current.get('humidity', 'N/A')}%\n"
        response += f"🌤️ Conditions: {current.get('description', 'N/A')}\n"
        response += f"💨 Wind Speed: {current.get('wind_speed', 'N/A')} m/s\n\n"
        
        if forecast:
            response += "**5-Day Forecast:**\n"
            for i, day in enumerate(forecast[:5]):
                date = datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')
                temp = day['main']['temp']
                desc = day['weather'][0]['description']
                response += f"{date}: {temp}°C, {desc}\n"
            response += "\n"
        
        # If agricultural context detected, add AI-generated advice
        if has_agricultural_context:
            print(f"🤖 DEBUG: Generating agricultural advice for weather query")
            # Get soil data for better agricultural advice
            soil_info = self.get_soil_data_for_location(location_name)
            ai_advice = await self._generate_agricultural_weather_advice(query, weather_info, soil_info, location_name)
            if ai_advice:
                response += "---\n\n"
                response += "🌾 **Agricultural Advice:**\n\n"
                response += ai_advice
        
        print(f"✅ DEBUG: Weather response formatted successfully")
        return response

    async def _generate_agricultural_weather_advice(self, query: str, weather_info: Dict, soil_info: Dict, location_name: str) -> str:
        """Generate agricultural advice based on weather conditions and soil data using AI"""
        try:
            current = weather_info.get("current", {})
            forecast = weather_info.get("forecast", [])
            
            # Prepare weather context for AI
            weather_context = {
                "location": location_name,
                "current_temp": current.get("temperature", "N/A"),
                "humidity": current.get("humidity", "N/A"),
                "conditions": current.get("description", "N/A"),
                "wind_speed": current.get("wind_speed", "N/A"),
                "pressure": current.get("pressure", "N/A")
            }
            
            # Add forecast summary
            if forecast:
                forecast_summary = []
                for day in forecast[:5]:
                    date = datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')
                    temp = day['main']['temp']
                    desc = day['weather'][0]['description']
                    forecast_summary.append(f"{date}: {temp}°C, {desc}")
                weather_context["forecast"] = forecast_summary
            
            # Prepare soil context
            soil_context = {
                "soil_type": soil_info.get("soil_type", "Mixed"),
                "suitable_crops": soil_info.get("suitable_crops", []),
                "characteristics": soil_info.get("characteristics", {})
            }
            
            # Create comprehensive prompt for agricultural advice
            prompt = f"""
You are an expert agricultural advisor for Indian farmers. Based on the current weather conditions, soil data, and farmer's question, provide practical, actionable advice.

Weather Information for {location_name}:
- Current Temperature: {weather_context['current_temp']}°C
- Humidity: {weather_context['humidity']}%
- Conditions: {weather_context['conditions']}
- Wind Speed: {weather_context['wind_speed']} m/s
- Pressure: {weather_context.get('pressure', 'N/A')} hPa

5-Day Forecast:
{chr(10).join(weather_context.get('forecast', ['No forecast available']))}

Soil Information for {location_name}:
- Soil Type: {soil_context['soil_type']}
- Suitable Crops: {', '.join(soil_context['suitable_crops'][:8]) if soil_context['suitable_crops'] else 'Various crops'}

Farmer's Question: "{query}"

Please provide specific, actionable advice considering:
1. Immediate actions needed based on current weather and soil conditions
2. Crop protection measures for the given temperature and soil type
3. Irrigation recommendations specific to {soil_context['soil_type']} soil
4. Disease/pest prevention tips relevant to current weather and soil conditions
5. Timing for agricultural activities
6. Any weather-related stress management for crops in {soil_context['soil_type']} soil
7. Fertilizer recommendations based on soil type

Focus on practical solutions that Indian farmers can implement immediately. Consider common crops suitable for {soil_context['soil_type']} soil like {', '.join(soil_context['suitable_crops'][:5]) if soil_context['suitable_crops'] else 'rice, wheat, cotton'}.

Keep the response concise but comprehensive, using simple language that farmers can understand.
Never ask for additional information - provide direct, actionable advice based on the available weather and soil data.
"""

            # Try Groq first, then OpenAI as fallback
            if self.groq_api_key:
                print("🌾 DEBUG: Using Groq for agricultural weather advice with soil data")
                messages = [
                    {"role": "system", "content": "You are an expert agricultural advisor for Indian farmers. Provide well-structured advice with clear sections. Use simple text formatting with proper line spacing. Start each major section on a new line with clear headings. Add blank lines between sections for better readability. Focus on practical, actionable advice."},
                    {"role": "user", "content": prompt}
                ]
                response = await self._call_groq_api(messages)
                return self._format_response_for_chat(response)
            elif self.openai_client:
                print("🌾 DEBUG: Using OpenAI for agricultural weather advice with soil data")
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert agricultural advisor for Indian farmers. Provide well-structured advice with clear sections. Use simple text formatting with proper line spacing. Start each major section on a new line with clear headings. Add blank lines between sections for better readability. Focus on practical, actionable advice."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=700,
                    temperature=0.7
                )
                response_text = response.choices[0].message.content.strip()
                return self._format_response_for_chat(response_text)
            else:
                print("⚠️ DEBUG: No AI API available for agricultural advice")
                # Provide basic advice based on temperature and soil
                temp = current.get("temperature")
                soil_type = soil_info.get("soil_type", "Mixed")
                if temp and isinstance(temp, (int, float)):
                    if temp > 35:
                        return f"🌡️ **High Temperature Alert for {soil_type} Soil:**\n\nIncrease irrigation frequency, provide shade for crops, avoid midday field work. Consider mulching to retain soil moisture in {soil_type.lower()} soil."
                    elif temp < 10:
                        return f"❄️ **Low Temperature Alert for {soil_type} Soil:**\n\nProtect crops from cold stress, avoid watering in evening, consider covering sensitive plants. {soil_type} soil retains heat differently."
                    else:
                        return f"🌱 **Moderate Weather for {soil_type} Soil:**\n\nGood conditions for most farming activities. Monitor soil moisture and adjust irrigation based on {soil_type.lower()} soil characteristics."
                return f"🌾 **Agricultural Guidance:**\n\nMonitor your crops closely and adjust irrigation based on current weather conditions and {soil_type.lower()} soil characteristics."
                
        except Exception as e:
            logger.error(f"Agricultural weather advice generation error: {e}")
            print(f"❌ DEBUG: Error generating agricultural advice: {e}")
            return "🌾 **Agricultural Guidance:**\n\nBased on current weather and soil conditions, monitor your crops closely and adjust irrigation as needed."

    async def _handle_weather_agriculture_query(self, query: str, context_data: Dict, user_context: Dict) -> str:
        """Handle weather-agriculture hybrid queries with comprehensive advice"""
        try:
            weather_info = context_data.get("weather", {})
            soil_info = context_data.get("soil", {})
            
            if "error" in weather_info:
                return f"I couldn't fetch weather data, but I can still provide general agricultural advice. {await self._generate_general_agricultural_advice(query)}"
            
            current = weather_info.get("current", {})
            forecast = weather_info.get("forecast", [])
            location_name = weather_info.get("location", {}).get("name", "Unknown Location")
            
            # Generate comprehensive agricultural advice with weather and soil context
            ai_advice = await self._generate_comprehensive_agricultural_advice(query, weather_info, soil_info, location_name)
            
            # Build response with weather summary + soil info + detailed advice
            response = f"🌍 WEATHER & AGRICULTURAL ADVISORY FOR {location_name.upper()}\n\n"
            
            # Brief weather summary
            response += f"📊 CURRENT CONDITIONS: {current.get('temperature', 'N/A')}°C, "
            response += f"{current.get('description', 'N/A')}, {current.get('humidity', 'N/A')}% humidity\n\n"
            
            # Add soil information
            if soil_info:
                response += f"🌱 SOIL TYPE: {soil_info.get('soil_type', 'Unknown')} soil\n"
                suitable_crops = soil_info.get('suitable_crops', [])
                if suitable_crops:
                    response += f"🌾 SUITABLE CROPS: {', '.join(suitable_crops[:5]).title()}\n"
            response += "\n"
            
            # Add forecast summary if available
            if forecast:
                response += f"📅 FORECAST: "
                for i, day in enumerate(forecast[:3]):  # Show 3 days
                    date = datetime.fromtimestamp(day['dt']).strftime('%m/%d')
                    temp = day['main']['temp']
                    response += f"{date}: {temp}°C"
                    if i < 2:
                        response += ", "
                response += "\n\n"
            
            # Add comprehensive agricultural advice
            response += "🌾 AGRICULTURAL ADVISORY:\n\n"
            response += ai_advice
            
            return response
            
        except Exception as e:
            logger.error(f"Weather-agriculture query error: {e}")
            return "I can provide agricultural advice. Please specify your crop type and location for better recommendations."

    async def _generate_comprehensive_agricultural_advice(self, query: str, weather_info: Dict, soil_info: Dict, location_name: str) -> str:
        """Generate comprehensive agricultural advice considering weather, soil, location, and query context"""
        try:
            current = weather_info.get("current", {})
            forecast = weather_info.get("forecast", [])
            
            # Analyze query for specific agricultural context
            query_lower = query.lower()
            crop_keywords = ['rice', 'wheat', 'cotton', 'tomato', 'onion', 'potato', 'maize', 'sugarcane', 'groundnut']
            detected_crops = [crop for crop in crop_keywords if crop in query_lower]
            
            action_keywords = {
                'survive': 'crop survival and stress management',
                'protect': 'crop protection measures',
                'irrigation': 'irrigation scheduling and water management',
                'harvest': 'harvest timing and post-harvest care',
                'plant': 'planting guidelines and timing',
                'fertilizer': 'fertilization strategies',
                'pest': 'pest and disease management',
                'seed': 'seed selection and sowing guidance',
                'yield': 'yield optimization strategies'
            }
            
            detected_actions = [action for keyword, action in action_keywords.items() if keyword in query_lower]
            
            # Build detailed weather context
            weather_analysis = f"""
Current Weather Analysis for {location_name}:
- Temperature: {current.get('temperature', 'N/A')}°C
- Humidity: {current.get('humidity', 'N/A')}%
- Weather: {current.get('description', 'N/A')}
- Wind: {current.get('wind_speed', 'N/A')} m/s
- Pressure: {current.get('pressure', 'N/A')} hPa
"""
            
            if forecast:
                weather_analysis += "\n5-Day Forecast:\n"
                for day in forecast[:5]:
                    date = datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')
                    temp = day['main']['temp']
                    desc = day['weather'][0]['description']
                    humidity = day['main']['humidity']
                    weather_analysis += f"- {date}: {temp}°C, {desc}, {humidity}% humidity\n"
            
            # Build detailed soil context
            soil_analysis = f"""
Soil Analysis for {location_name}:
- Soil Type: {soil_info.get('soil_type', 'Unknown')}
- Suitable Crops: {', '.join(soil_info.get('suitable_crops', ['General crops']))}
"""
            
            # Add soil characteristics if available
            characteristics = soil_info.get('characteristics', {})
            if characteristics:
                temp_range = characteristics.get('temperature_range', [])
                humidity_range = characteristics.get('humidity_range', [])
                moisture_range = characteristics.get('moisture_range', [])
                
                if temp_range:
                    soil_analysis += f"- Optimal Temperature Range: {temp_range[0]}°C - {temp_range[1]}°C\n"
                if humidity_range:
                    soil_analysis += f"- Optimal Humidity Range: {humidity_range[0]}% - {humidity_range[1]}%\n"
                if moisture_range:
                    soil_analysis += f"- Optimal Moisture Range: {moisture_range[0]}% - {moisture_range[1]}%\n"
            
            # Add specific crop recommendations if available
            crop_recommendations = soil_info.get('crop_recommendations', {})
            if detected_crops and crop_recommendations:
                soil_analysis += "\nCrop-Specific Soil Recommendations:\n"
                for crop in detected_crops:
                    if crop in crop_recommendations:
                        crop_data = crop_recommendations[crop]
                        if crop_data:
                            sample = crop_data[0]  # Take first recommendation
                            soil_analysis += f"- {crop.title()}: {sample.get('fertilizer', 'Standard fertilizer')}, "
                            soil_analysis += f"N-P-K: {sample.get('nitrogen', 0)}-{sample.get('phosphorous', 0)}-{sample.get('potassium', 0)}\n"
            
            # Create comprehensive prompt
            prompt = f"""
You are an expert agricultural consultant with deep knowledge of Indian farming practices, crop management, soil science, and climate adaptation strategies.

{weather_analysis}

{soil_analysis}

Farmer's Question: "{query}"

Context Analysis:
- Detected Crops: {', '.join(detected_crops) if detected_crops else 'General farming'}
- Focus Areas: {', '.join(detected_actions) if detected_actions else 'General agricultural advice'}
- Location: {location_name}

Please provide comprehensive, actionable advice that includes:

1. IMMEDIATE ACTIONS - What the farmer should do today/this week based on current weather and soil conditions

2. CROP-SPECIFIC GUIDANCE - Tailored advice for the crops mentioned or recommend suitable crops for the soil type

3. WEATHER RESPONSE STRATEGY - How to adapt to current and forecasted conditions

4. SOIL MANAGEMENT - Specific advice for the {soil_info.get('soil_type', 'local')} soil type

5. FERTILIZER RECOMMENDATIONS - NPK requirements based on soil and crop type

6. RISK MANAGEMENT - Preventive measures for potential weather and soil-related problems

7. TIMING RECOMMENDATIONS - Best times for various agricultural activities

8. RESOURCE OPTIMIZATION - Water, fertilizer, and labor management tips

Consider:
- Current season and typical crop cycles in the region
- Soil-specific cultivation practices
- Temperature stress thresholds for crops
- Humidity effects on disease development
- Soil moisture management
- Nutrient availability in {soil_info.get('soil_type', 'local')} soil

FORMATTING REQUIREMENTS:
- Use ALL CAPS for main section headers (e.g., "IMMEDIATE ACTIONS")
- Add double line breaks between each major section
- Use numbered lists for actionable steps
- Write in clear, easy-to-read paragraphs
- Keep recommendations specific and practical

Provide practical, implementable solutions using simple language. Include specific timings, quantities, or methods where possible.
Never ask the farmer for additional information - provide direct answers based on the available data.
"""

            # Try Groq first, then OpenAI
            if self.groq_api_key:
                print("🌾 DEBUG: Using Groq for comprehensive agricultural advice with soil data")
                messages = [
                    {"role": "system", "content": "You are an expert agricultural consultant for Indian farmers. Provide well-structured advice with clear sections. Use simple text formatting with proper line spacing. Start each major section on a new line with clear headings. Add blank lines between sections for better readability. Focus on practical, actionable advice."},
                    {"role": "user", "content": prompt}
                ]
                response = await self._call_groq_api(messages)
                # Ensure proper line breaks for chat interface
                return self._format_response_for_chat(response)
            elif self.openai_client:
                print("🌾 DEBUG: Using OpenAI for comprehensive agricultural advice with soil data")
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert agricultural consultant for Indian farmers. Provide well-structured advice with clear sections. Use simple text formatting with proper line spacing. Start each major section on a new line with clear headings. Add blank lines between sections for better readability. Focus on practical, actionable advice."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                response_text = response.choices[0].message.content.strip()
                # Ensure proper line breaks for chat interface
                return self._format_response_for_chat(response_text)
            else:
                return await self._generate_fallback_agricultural_advice_with_soil(query, current, detected_crops, soil_info)
                
        except Exception as e:
            logger.error(f"Comprehensive agricultural advice generation error: {e}")
            return await self._generate_fallback_agricultural_advice_with_soil(query, current, [], soil_info)

    async def _generate_fallback_agricultural_advice(self, query: str, current_weather: Dict, crops: List[str]) -> str:
        """Generate basic agricultural advice when AI APIs are not available"""
        temp = current_weather.get("temperature")
        humidity = current_weather.get("humidity")
        conditions = current_weather.get("description", "").lower()
        
        advice = []
        
        # Temperature-based advice
        if temp and isinstance(temp, (int, float)):
            if temp > 35:
                advice.append("🌡️ **High Temperature Alert:**\n- Increase irrigation frequency\n- Provide shade for young plants\n- Avoid field work during midday\n- Consider mulching to retain soil moisture")
            elif temp < 15:
                advice.append("❄️ **Cool Weather:**\n- Reduce irrigation frequency\n- Protect sensitive crops from cold\n- Good time for land preparation")
            else:
                advice.append("🌱 **Moderate Temperature:** Good conditions for most farming activities")
        
        # Humidity-based advice
        if humidity and isinstance(humidity, (int, float)):
            if humidity > 80:
                advice.append("💧 **High Humidity:** Monitor for fungal diseases, ensure good ventilation")
            elif humidity < 40:
                advice.append("🏜️ **Low Humidity:** Increase irrigation, consider windbreaks")
        
        # Weather condition-based advice
        if "rain" in conditions:
            advice.append("🌧️ **Rainy Conditions:** Avoid fertilizer application, ensure proper drainage")
        elif "clear" in conditions or "sunny" in conditions:
            advice.append("☀️ **Clear Weather:** Good for drying harvest, field operations")
        
        # Crop-specific advice
        if crops:
            advice.append(f"🌾 **For {', '.join(crops)}:** Monitor growth stages and adjust care accordingly")
        
        return "\n\n".join(advice) if advice else "Monitor your crops closely and adjust farming practices based on current weather conditions."

    async def _generate_fallback_agricultural_advice_with_soil(self, query: str, current_weather: Dict, crops: List[str], soil_info: Dict) -> str:
        """Generate basic agricultural advice with soil context when AI APIs are not available"""
        temp = current_weather.get("temperature")
        humidity = current_weather.get("humidity")
        conditions = current_weather.get("description", "").lower()
        soil_type = soil_info.get("soil_type", "Mixed")
        
        advice = []
        
        # Temperature-based advice
        if temp and isinstance(temp, (int, float)):
            if temp > 35:
                advice.append(f"🌡️ **High Temperature Alert for {soil_type} Soil:**\n- Increase irrigation frequency\n- Provide shade for young plants\n- Avoid field work during midday\n- Consider mulching to retain soil moisture")
            elif temp < 15:
                advice.append(f"❄️ **Cool Weather for {soil_type} Soil:**\n- Reduce irrigation frequency\n- Protect sensitive crops from cold\n- Good time for land preparation")
            else:
                advice.append(f"🌱 **Moderate Temperature for {soil_type} Soil:** Good conditions for most farming activities")
        
        # Humidity-based advice
        if humidity and isinstance(humidity, (int, float)):
            if humidity > 80:
                advice.append("💧 **High Humidity:** Monitor for fungal diseases, ensure good ventilation")
            elif humidity < 40:
                advice.append("🏜️ **Low Humidity:** Increase irrigation, consider windbreaks")
        
        # Weather condition-based advice
        if "rain" in conditions:
            advice.append("🌧️ **Rainy Conditions:** Avoid fertilizer application, ensure proper drainage")
        elif "clear" in conditions or "sunny" in conditions:
            advice.append("☀️ **Clear Weather:** Good for drying harvest, field operations")
        
        # Soil-specific advice
        suitable_crops = soil_info.get('suitable_crops', [])
        if suitable_crops:
            advice.append(f"🌾 **Recommended crops for {soil_type} soil:** {', '.join(suitable_crops[:5]).title()}")
        
        # Crop-specific advice
        if crops:
            advice.append(f"🌱 **For {', '.join(crops)}:** Monitor growth stages and adjust care according to {soil_type.lower()} soil requirements")
        
        return "\n\n".join(advice) if advice else f"Monitor your crops closely and adjust farming practices based on current weather conditions and {soil_type.lower()} soil characteristics."

    async def _generate_general_agricultural_advice(self, query: str) -> str:
        """Generate general agricultural advice when weather data is not available"""
        try:
            if self.groq_api_key:
                prompt = f"""
You are an expert agricultural advisor for Indian farmers. The farmer has asked: "{query}"

Provide practical, actionable advice focusing on:
1. General best practices for the mentioned topic
2. Seasonal considerations for Indian agriculture
3. Cost-effective solutions for small farmers
4. Preventive measures and timing recommendations

Keep the response concise but helpful, using simple language.
"""
                messages = [
                    {"role": "system", "content": "You are an expert agricultural advisor for Indian farmers."},
                    {"role": "user", "content": prompt}
                ]
                return await self._call_groq_api(messages)
            else:
                return "Please provide your specific crop type and location for better agricultural recommendations."
        except Exception as e:
            logger.error(f"General agricultural advice error: {e}")
            return "Please specify your crop type and farming challenge for better guidance."

    async def _handle_market_query(self, query: str, context_data: Dict, user_context: Dict) -> str:
        """Handle market price queries with intelligent hybrid API+CSV system"""
        try:
            # Get location - prioritize AI-extracted location for specific location queries
            ai_location = user_context.get("ai_location") if user_context else None
            default_location = user_context.get("location") if user_context else None
            location = ai_location or default_location
            
            print(f"💰 DEBUG: Market query handler - AI location: {ai_location}, Default: {default_location}, Using: {location}")
            
            # Use intelligent commodity prices method with original query for AI analysis
            price_result = await self.get_commodity_prices(
                commodity=None,  # Let AI extract commodity
                user_location=location,
                original_query=query
            )
            
            print(f"💰 DEBUG: Price result received: {price_result.get('source', 'unknown')} with {price_result.get('count', 0)} records")
            
            # Check if query was classified as non-price related
            if "error" in price_result and "not price-related" in price_result.get("error", ""):
                intent = price_result.get("intent", "general")
                if intent == "weather":
                    return "I see you're asking about weather. Let me help you with weather information instead of prices."
                elif intent == "general":
                    return "I see this is a general farming question. I'll help you with agricultural advice."
                else:
                    return "I'll help you with that farming question."
            
            # Handle other errors
            if "error" in price_result:
                return f"I couldn't fetch current market prices: {price_result.get('error', 'Unknown error')}. Please try again later."
            
            data = price_result.get("data", [])
            source = price_result.get("source", "unknown")
            
            if not data:
                message = price_result.get("message", "No market price data available at the moment.")
                return f"{message}\n\n💡 Try asking for a specific commodity like 'tomato price' or 'rice rate in Guntur'."
            
            # Extract commodity and location info for response formatting
            query_lower = query.lower()
            
            # Determine what commodity was found
            found_commodities = list(set(record.get("commodity", "") for record in data[:10]))
            primary_commodity = found_commodities[0] if found_commodities else "commodity"
            
            # Determine location context
            location_context = ""
            if data:
                first_record = data[0]
                state = first_record.get("state", "")
                district = first_record.get("district", "")
                market = first_record.get("market", "")
                
                if market and district:
                    location_context = f"{market}, {district}"
                elif district:
                    location_context = district
                elif state:
                    location_context = state
            
            # Format response based on data source
            if source == "api":
                response = f"🌐 **Live Market Prices** ({primary_commodity.title()})\n"
                response += f"📡 Source: Government API (Real-time data)\n\n"
            elif source == "csv":
                response = f"📊 **Market Prices** ({primary_commodity.title()})\n"
                response += f"📋 Source: Local Market Database\n"
                if location_context:
                    response += f"📍 Area: {location_context}\n"
                response += "\n"
            else:
                response = f"💰 **Market Prices** ({primary_commodity.title()})\n\n"
            
            # Show top 5-8 relevant price records
            count = 0
            max_display = 8
            
            for record in data:
                if count >= max_display:
                    break
                
                commodity = record.get("commodity", "Unknown")
                market = record.get("market", "Unknown Market")
                district = record.get("district", "Unknown District") 
                state = record.get("state", "Unknown State")
                
                # Price information
                modal_price = record.get("modal_price", "N/A")
                min_price = record.get("min_price", "N/A")
                max_price = record.get("max_price", "N/A")
                arrival_date = record.get("arrival_date", "")
                
                # Format location
                if district != "Unknown District" and state != "Unknown State":
                    location_str = f"{market}, {district}, {state}"
                elif state != "Unknown State":
                    location_str = f"{market}, {state}"
                else:
                    location_str = market
                
                # Format price
                if modal_price and modal_price != "N/A":
                    if min_price != "N/A" and max_price != "N/A" and min_price != max_price:
                        price_str = f"₹{modal_price} (₹{min_price}-₹{max_price})"
                    else:
                        price_str = f"₹{modal_price}"
                else:
                    price_str = "Price not available"
                
                # Add date if available
                date_str = f" • {arrival_date}" if arrival_date else ""
                
                response += f"📍 **{location_str}**\n"
                response += f"   💰 {price_str} per quintal{date_str}\n\n"
                
                count += 1
            
            # Add helpful footer
            if count < len(data):
                remaining = len(data) - count
                response += f"📈 *+{remaining} more markets available*\n\n"
            
            # Add data source note
            if source == "api":
                response += "✅ Real-time data from Government API\n"
            elif source == "csv":
                response += "📋 Data from comprehensive market database\n"
                response += "💡 For other states, try: 'tomato price in Kerala' or 'rice rate in Gujarat'\n"
            
            # Add location-specific tip
            if location and location.lower() in ["vijayawada", "guntur", "tirupati"]:
                response += f"🎯 Showing prices relevant to {location.title()}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in market query handling: {e}")
            return "I encountered an error while fetching market prices. Please try again with a specific commodity like 'tomato price' or 'rice rate'."
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
            
            # Use Groq API for the response
            if self.groq_api_key:
                print("💰 DEBUG: Using Groq for finance query")
                messages = [
                    {"role": "system", "content": "You are an expert in agricultural finance and government schemes for Indian farmers."},
                    {"role": "user", "content": prompt}
                ]
                return await self._call_groq_api(messages)
            elif self.openai_client:
                print("💰 DEBUG: Using OpenAI for finance query")
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
            else:
                print("⚠️ DEBUG: No AI API available for finance")
                return "I can help with information about agricultural loans and government schemes. Please specify your location for more relevant information."
                
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
                system_msg = "You are an expert agricultural advisor helping Indian farmers. Provide well-structured advice with clear sections using ALL CAPS for headers. Add proper line breaks between sections for better readability. Focus on practical, actionable advice with numbered lists."
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
                        system_content = "You are an expert agricultural advisor helping Indian farmers. Provide well-structured advice with clear sections using ALL CAPS for headers. Add proper line breaks between sections for better readability. Focus on practical, actionable advice with numbered lists."
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

    async def _handle_crop_advice_query(self, query: str, context_data: Dict, user_context: Dict, location: str) -> str:
        """Enhanced handler for crop advice queries with real weather data"""
        try:
            if not self.openai_client:
                # Fallback to basic crop advice
                return await self._basic_crop_advice(query, location)
            
            # Get current season and detailed weather context
            season = self._get_current_season()
            weather_data = context_data.get("weather", {})
            ai_classification = context_data.get("ai_classification", {})
            
            # Extract detailed weather information
            current_weather = weather_data.get('current', {})
            forecast = weather_data.get('forecast', [])
            
            # Build detailed weather context string
            weather_context = f"""
CURRENT WEATHER CONDITIONS:
- Temperature: {current_weather.get('temperature', 'N/A')}°C (feels like {current_weather.get('feels_like', 'N/A')}°C)
- Humidity: {current_weather.get('humidity', 'N/A')}%
- Weather: {current_weather.get('description', 'N/A')}
- Wind Speed: {current_weather.get('wind_speed', 'N/A')} km/h
- Pressure: {current_weather.get('pressure', 'N/A')} hPa
- Visibility: {current_weather.get('visibility', 'N/A')} km
- UV Index: {current_weather.get('uv_index', 'N/A')}"""

            # Add 5-day forecast summary
            if forecast:
                weather_context += "\n\n5-DAY FORECAST:"
                for i, day in enumerate(forecast[:5]):
                    weather_context += f"\nDay {i+1}: {day.get('temperature', 'N/A')}°C, {day.get('description', 'N/A')}, Humidity: {day.get('humidity', 'N/A')}%"
            
            # Build comprehensive context
            prompt = f"""You are an expert agricultural advisor for Indian farmers. You have REAL-TIME weather data for the farmer's location. Use this data to provide specific crop recommendations.

LOCATION: {location or 'India'}
SEASON: {season}
DATE: {datetime.now().strftime('%B %d, %Y')}

{weather_context}

FARMER'S QUESTION: "{query}"

IMPORTANT: You have the ACTUAL current weather conditions and forecast above. Do NOT ask them to consider climate - you already know their climate conditions. Give direct advice based on this real data.

Based on the actual weather conditions shown above, provide:

1. **Immediate Crop Recommendations**: 
   - Specific varieties perfect for current temperature ({current_weather.get('temperature', 'N/A')}°C) and humidity ({current_weather.get('humidity', 'N/A')}%)
   - Varieties that can handle the current weather pattern: {current_weather.get('description', 'N/A')}

2. **Weather-Based Timing**: 
   - Best planting dates considering the 5-day forecast
   - If current conditions are suitable for immediate planting or if they should wait

3. **Risk Assessment**: 
   - How the current weather conditions affect crop success
   - Any weather-related risks in the forecast

4. **Specific Action Plan**: 
   - Exact steps to take this week based on weather
   - Seed varieties with tolerance for current humidity/temperature levels

5. **Regional Varieties**: 
   - Seeds available in {location} that match current conditions
   - Local suppliers and markets

Give SPECIFIC variety names and direct advice. Since you know the exact weather, don't give generic advice about "considering climate" - you already have that data."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=700
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ DEBUG: Crop advice query error: {e}")
            return await self._basic_crop_advice(query, location)

    async def _handle_financial_query(self, query: str, context_data: Dict, user_context: Dict, location: str) -> str:
        """Enhanced handler for financial and affordability queries"""
        try:
            if not self.openai_client:
                return await self._basic_financial_advice(query)
            
            ai_classification = context_data.get("ai_classification", {})
            season = self._get_current_season()
            
            prompt = f"""You are a financial advisor specializing in Indian agriculture. Help farmers with financial planning and affordability.

CONTEXT:
- Location: {location or 'India'}
- Current Season: {season}
- Date: {datetime.now().strftime('%B %d, %Y')}
- Query Classification: {ai_classification}

FARMER'S QUESTION: "{query}"

Please provide:
1. **Cost Analysis**: Break down typical costs for farming improvements
2. **Funding Options**: Government schemes, bank loans, subsidies available
3. **ROI Assessment**: Expected returns and payback periods
4. **Risk Mitigation**: How to minimize financial risks
5. **Step-by-step Plan**: Practical steps to afford improvements

Focus on:
- PM-KISAN, KCC, PMFBY schemes
- State-specific schemes for AP/Telangana if applicable
- Microfinance and SHG options
- Crop insurance and risk management
- Budget-friendly alternatives

Be specific about application processes and eligibility criteria."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=600
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ DEBUG: Financial query error: {e}")
            return await self._basic_financial_advice(query)

    async def _handle_disease_query(self, query: str, context_data: Dict, user_context: Dict, location: str) -> str:
        """Enhanced handler for disease and pest queries"""
        try:
            if not self.openai_client:
                return await self._basic_disease_advice(query)
            
            season = self._get_current_season()
            weather_data = context_data.get("weather", {})
            
            prompt = f"""You are a plant pathologist and pest management expert for Indian agriculture.

CONTEXT:
- Location: {location or 'India'}
- Current Season: {season}
- Weather: {weather_data.get('current', {}).get('description', 'N/A')}
- Temperature: {weather_data.get('current', {}).get('temperature', 'N/A')}°C
- Humidity: {weather_data.get('current', {}).get('humidity', 'N/A')}%

FARMER'S QUESTION: "{query}"

Please provide:
1. **Disease/Pest Identification**: Most likely issues based on symptoms
2. **Immediate Treatment**: Emergency steps to prevent spread
3. **Organic Solutions**: Eco-friendly treatment options
4. **Chemical Treatment**: If necessary, specific products and dosages
5. **Prevention**: How to prevent future occurrences

Consider:
- Weather conditions affecting disease spread
- Regional common pests and diseases
- Integrated Pest Management (IPM) approaches
- Cost-effective solutions for small farmers

Be specific about product names, concentrations, and application methods."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=600
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ DEBUG: Disease query error: {e}")
            return await self._basic_disease_advice(query)

    async def _handle_general_query_with_context(self, query: str, context_data: Dict, user_context: Dict, location: str) -> str:
        """Enhanced general query handler with real weather data"""
        try:
            if not self.openai_client:
                return await self._handle_general_query(query, context_data, user_context)
            
            season = self._get_current_season()
            weather_data = context_data.get("weather", {})
            ai_classification = context_data.get("ai_classification", {})
            
            # Extract detailed weather information
            current_weather = weather_data.get('current', {})
            forecast = weather_data.get('forecast', [])
            
            # Build detailed weather context
            weather_context = f"""
CURRENT WEATHER CONDITIONS FOR {location or 'your location'}:
- Temperature: {current_weather.get('temperature', 'N/A')}°C (feels like {current_weather.get('feels_like', 'N/A')}°C)
- Humidity: {current_weather.get('humidity', 'N/A')}%
- Conditions: {current_weather.get('description', 'N/A')}
- Wind: {current_weather.get('wind_speed', 'N/A')} km/h
- Pressure: {current_weather.get('pressure', 'N/A')} hPa"""

            if forecast:
                weather_context += "\n\nNEXT 3 DAYS FORECAST:"
                for i, day in enumerate(forecast[:3]):
                    weather_context += f"\nDay {i+1}: {day.get('temperature', 'N/A')}°C, {day.get('description', 'N/A')}"
            
            prompt = f"""You are BhoomiSetu, an expert AI agricultural advisor for Indian farmers. You have REAL-TIME weather data for the farmer's location.

LOCATION: {location or 'India'}
SEASON: {season}
DATE: {datetime.now().strftime('%B %d, %Y')}

{weather_context}

FARMER'S QUESTION: "{query}"

IMPORTANT: You have the ACTUAL current weather conditions above. Use this real data in your response. Do NOT give generic advice about "considering weather conditions" - you already know their exact weather.

Guidelines:
- Reference the specific weather conditions (temperature: {current_weather.get('temperature', 'N/A')}°C, humidity: {current_weather.get('humidity', 'N/A')}%, conditions: {current_weather.get('description', 'N/A')})
- Provide advice tailored to these exact conditions
- Consider the forecast when suggesting timing
- Focus on practical, immediate actions
- Include both traditional and modern practices
- Mention relevant government schemes if applicable
- Use simple language accessible to farmers

Since you know the exact weather, give specific, weather-aware recommendations."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=700
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ DEBUG: Enhanced general query error: {e}")
            return await self._handle_general_query(query, context_data, user_context)

    async def _basic_crop_advice(self, query: str, location: str) -> str:
        """Basic crop advice fallback"""
        season = self._get_current_season()
        return f"""🌱 **Crop Advice for {location or 'your region'}**

**Current Season**: {season}

**General Recommendations**:
- For Kharif season: Rice, Cotton, Sugarcane, Maize
- For Rabi season: Wheat, Mustard, Gram, Barley  
- For Zaid season: Fodder crops, Vegetables

**For climate-resilient varieties**:
- Choose drought-tolerant varieties
- Consider short-duration crops for unpredictable weather
- Use certified seeds from authorized dealers

💡 For specific variety recommendations, please mention your exact location and crop preferences."""

    async def _basic_financial_advice(self, query: str) -> str:
        """Basic financial advice fallback"""
        return """💰 **Financial Support Options**

**Government Schemes**:
- **PM-KISAN**: ₹6,000 per year for all farmers
- **KCC**: Crop loans at 4% interest (with subsidy)
- **PMFBY**: Crop insurance at low premium rates

**Steps to Improve Affordability**:
1. Apply for Kisan Credit Card
2. Join Farmer Producer Organizations (FPOs)
3. Use government subsidies for inputs
4. Practice cost-effective farming methods

📞 Visit your nearest bank or agriculture department for applications."""

    async def _basic_disease_advice(self, query: str) -> str:
        """Basic disease advice fallback"""
        return """🏥 **Plant Disease Management**

**Immediate Steps**:
1. Isolate affected plants
2. Remove and destroy infected parts
3. Improve air circulation
4. Reduce moisture if possible

**Common Treatments**:
- Neem oil spray for organic control
- Copper fungicides for fungal diseases
- Consult local agriculture extension officer

**Prevention**:
- Use certified disease-free seeds
- Practice crop rotation
- Maintain field hygiene

🌿 For specific diagnosis, visit your nearest Krishi Vigyan Kendra."""

# Initialize the agent
agri_agent = AgricultureAIAgent()
