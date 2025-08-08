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

Please respond in JSON format with:
1. "intent": "price" | "weather" | "general"
2. "commodity": extracted commodity name (standardized)
3. "location": extracted location (corrected spelling)
4. "corrected_query": query with typos fixed
5. "confidence": 0-1 score

Examples:
- "weather in banglore" → {{"intent": "weather", "commodity": null, "location": "bangalore", "corrected_query": "weather in bangalore", "confidence": 0.95}}
- "tomaot price in bangalor" → {{"intent": "price", "commodity": "tomato", "location": "bangalore", "corrected_query": "tomato price in bangalore", "confidence": 0.9}}
- "weather in deli" → {{"intent": "weather", "commodity": null, "location": "delhi", "corrected_query": "weather in delhi", "confidence": 0.95}}

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
            
            result = json.loads(result_text)
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
                import pandas as pd
                import os
                
                # Path to the comprehensive CSV file
                csv_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                           "9ef84268-d588-465a-a308-a864a43d0070 (2).csv")
                
                print(f"📊 DEBUG: Loading CSV data from: {csv_file_path}")
                
                if os.path.exists(csv_file_path):
                    df = pd.read_csv(csv_file_path)
                    print(f"✅ DEBUG: Loaded {len(df)} records from CSV")
                    
                    # Filter by target state if specified
                    if target_state:
                        df = df[df['State'].str.contains(target_state, case=False, na=False)]
                        print(f"🎯 DEBUG: Filtered to {len(df)} records for state: {target_state}")
                    
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
                        commodity_filter = df['Commodity'].str.contains('|'.join(search_terms), case=False, na=False)
                        df = df[commodity_filter]
                        print(f"🎯 DEBUG: Filtered to {len(df)} records for commodity: {commodity}")
                    
                    if not df.empty:
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
        """Main method to process agricultural queries"""
        try:
            print(f"🤖 DEBUG: Processing query: '{query}' | Location: '{location}'")
            
            # Detect and translate if needed
            detected_lang = await self.detect_language(query)
            english_query = query
            if detected_lang != 'en':
                english_query = await self.translate_text(query, 'en')
            
            # Classify query type using AI if available
            print(f"📝 DEBUG: Starting Groq AI classification for query: '{english_query}'")
            groq_classification = await self.classify_query_with_groq(english_query)
            query_type = groq_classification.get("intent", "general")
            ai_commodity = groq_classification.get("commodity")
            ai_location = groq_classification.get("location")
            
            print(f"🤖 DEBUG: AI classified query type: '{query_type}'")
            print(f"🤖 DEBUG: AI extracted - Commodity: {ai_commodity}, Location: {ai_location}")
            
            # Use AI-extracted location if not provided
            if not location and ai_location:
                location = ai_location
                print(f"🤖 DEBUG: Using AI-extracted location: {location}")
            
            # Gather relevant data based on query type
            context_data = {}
            
            # For weather queries, use the AI-extracted location specifically
            if query_type == "weather" and ai_location:
                # Use AI-extracted location for weather
                weather_location = ai_location
                print(f"🌤️ DEBUG: Weather query detected with AI location: '{weather_location}'")
                print(f"🌤️ DEBUG: Original query: '{query}' → Using location: '{weather_location}'")
                weather_data = await self.get_weather_data(weather_location)
                context_data["weather"] = weather_data
                print(f"🌤️ DEBUG: Weather data fetched, proceeding to handler...")
                response = await self._handle_weather_query(english_query, context_data, user_context)
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
            else:
                # For other queries, fetch weather data with regular location
                if location:
                    weather_data = await self.get_weather_data(location)
                    context_data["weather"] = weather_data
                
                # Route based on keywords
                if any(word in english_query.lower() for word in ["price", "rate", "cost", "market", "sell"]):
                    response = await self._handle_market_query(english_query, context_data, user_context)
                elif any(word in english_query.lower() for word in ["irrigate", "water", "irrigation", "watering"]):
                    response = await self._handle_irrigation_query(english_query, context_data, user_context)
                elif any(word in english_query.lower() for word in ["seed", "variety", "crop", "plant", "sow"]):
                    response = await self._handle_crop_selection_query(english_query, context_data, user_context)
                elif any(word in english_query.lower() for word in ["weather", "temperature", "rain", "climate"]):
                    # For weather queries detected by keywords, also use AI location if available
                    if ai_location:
                        weather_data = await self.get_weather_data(ai_location)
                        context_data["weather"] = weather_data
                    response = await self._handle_weather_query(english_query, context_data, user_context)
                elif any(word in english_query.lower() for word in ["loan", "credit", "scheme", "subsidy", "finance", "money"]):
                    response = await self._handle_finance_query(english_query, context_data, user_context)
                elif any(word in english_query.lower() for word in ["disease", "pest", "fungus", "insect", "spray"]):
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
        """Handle weather-related queries"""
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
        
        print(f"✅ DEBUG: Weather response formatted successfully")
        return response

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
