"""
FastAPI Web Application for BhoomiSetu Agricultural AI Agent
Provides web interface and REST API endpoints
"""

import os
import json
import asyncio
from typing import Dict, Optional, List
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ValidationError
import uvicorn
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agents.agri_agent import agri_agent

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="BhoomiSetu - Agricultural AI Advisor",
    description="AI-powered agricultural advisor for Indian farmers",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic models for API
class Coordinates(BaseModel):
    latitude: float
    longitude: float

class QueryRequest(BaseModel):
    query: str
    location: Optional[str] = None
    crop_type: Optional[str] = None
    soil_type: Optional[str] = None
    language: Optional[str] = "en"
    coordinates: Optional[Coordinates] = None

class QueryResponse(BaseModel):
    response: str
    query_type: Optional[str] = "general"
    language: Optional[str] = "en"
    timestamp: Optional[datetime] = None

class WeatherRequest(BaseModel):
    location: str

class PriceRequest(BaseModel):
    commodity: Optional[str] = None

# In-memory session storage (in production, use Redis or database)
user_sessions = {}

async def get_city_from_coordinates(latitude: float, longitude: float) -> str:
    """Get city name from coordinates using reverse geocoding"""
    try:
        import requests
        api_key = os.getenv('OPENWEATHER_API_KEY', '9f842d56fca036534c0a651a6dd6f6fb')
        url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={latitude}&lon={longitude}&limit=1&appid={api_key}"
        
        response = requests.get(url)
        data = response.json()
        
        if data and len(data) > 0:
            return data[0].get('name', 'Unknown')
        return 'Unknown'
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        return 'Unknown'

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_interface(request: Request):
    """Serve the chat interface"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process agricultural query via API"""
    try:
        # Debug logging
        print(f"DEBUG: Received query request: {request.dict()}")
        
        # Determine location from coordinates if not provided
        location = request.location
        if not location and request.coordinates:
            # Get city name from coordinates using reverse geocoding
            location = await get_city_from_coordinates(request.coordinates.latitude, request.coordinates.longitude)
        
        # Prepare user context
        user_context = {
            "crop_type": request.crop_type,
            "soil_type": request.soil_type,
            "language": request.language,
            "location": location,
            "coordinates": request.coordinates.dict() if request.coordinates else None
        }
        
        print(f"DEBUG: User context: {user_context}")
        
        # Always try to use AI agent (now supports Grok as fallback)
        response = await agri_agent.process_query(
            query=request.query,
            location=location,
            user_context=user_context
        )
        
        # Classify query type
        query_type = agri_agent.classify_query(request.query)
        
        print(f"DEBUG: Response generated: {response[:100]}...")
        
        return QueryResponse(
            response=response,
            query_type=query_type,
            language=request.language or "en",
            timestamp=datetime.now()
        )
    
    except ValueError as ve:
        print(f"DEBUG: Validation error: {ve}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        print(f"DEBUG: General error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def extract_location_from_query(query: str) -> str:
    """Extract location from query text"""
    query_lower = query.lower()
    
    # Common Indian cities and places for quick matching
    indian_cities = [
        'mumbai', 'delhi', 'bangalore', 'bengaluru', 'chennai', 'kolkata', 'hyderabad',
        'pune', 'ahmedabad', 'jaipur', 'surat', 'lucknow', 'kanpur', 'nagpur',
        'indore', 'thane', 'bhopal', 'visakhapatnam', 'patna', 'vadodara',
        'ghaziabad', 'ludhiana', 'agra', 'nashik', 'faridabad', 'meerut',
        'rajkot', 'kalyan', 'vasai', 'varanasi', 'srinagar', 'aurangabad',
        'dhanbad', 'amritsar', 'navi mumbai', 'allahabad', 'howrah', 'ranchi',
        'gwalior', 'jabalpur', 'coimbatore', 'vijayawada', 'jodhpur', 'madurai',
        'raipur', 'kota', 'guwahati', 'chandigarh', 'solapur', 'hubballi'
    ]
    
    # First try to find known cities
    for city in indian_cities:
        if city in query_lower:
            return city.title()
    
    # If no known city found, use regex patterns
    import re
    patterns = [
        r'(?:weather|temperature|rain|climate|price|cost).*?(?:in|at|for)\s+([a-zA-Z][a-zA-Z\s]{1,20}?)(?:\s|$|\?)',
        r'(?:in|at)\s+([a-zA-Z][a-zA-Z\s]{1,20}?)(?:\s+(?:today|tomorrow|now)|$|\?)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, query_lower)
        for match in matches:
            location = match.strip()
            # Clean up and validate
            location = re.sub(r'\b(?:today|tomorrow|now|current|the|is|like|what|how|why|when)\b', '', location).strip()
            if location and len(location) > 2 and len(location.split()) <= 3:
                return location.title()
    
    return None

def get_nearby_regions(location: str) -> list:
    """Get nearby regions/keywords for a given location"""
    nearby_map = {
        'vijayawada': ['krishna', 'guntur', 'andhra pradesh', 'amaravati', 'machilipatnam', 'eluru',
                      'krishnai', 'madanapalli', 'tirupati', 'nellore', 'ongole', 'rajahmundry',
                      'kakinada', 'visakhapatnam', 'chittoor', 'kadapa', 'kurnool', 'anantapur'],
        'hyderabad': ['telangana', 'secunderabad', 'cyberabad', 'rangareddy', 'medchal',
                     'nizamabad', 'warangal', 'karimnagar', 'khammam', 'mahbubnagar'],
        'bangalore': ['bengaluru', 'karnataka', 'mysore', 'tumkur', 'ramanagara',
                     'hassan', 'mandya', 'kolar', 'chikkaballapur', 'chitradurga'],
        'chennai': ['tamil nadu', 'kanchipuram', 'tiruvallur', 'chengalpattu',
                   'vellore', 'madurai', 'coimbatore', 'salem', 'tirunelveli'],
        'mumbai': ['maharashtra', 'thane', 'pune', 'nashik', 'aurangabad',
                  'solapur', 'kolhapur', 'sangli', 'satara', 'ahmednagar'],
        'delhi': ['new delhi', 'gurgaon', 'noida', 'faridabad', 'ghaziabad',
                 'meerut', 'muzaffarnagar', 'saharanpur', 'moradabad', 'aligarh'],
        'kolkata': ['west bengal', 'howrah', 'hooghly', 'north 24 parganas',
                   'south 24 parganas', 'nadia', 'murshidabad', 'burdwan'],
        'pune': ['maharashtra', 'mumbai', 'nashik', 'satara', 'sangli',
                'aurangabad', 'solapur', 'kolhapur', 'ahmednagar'],
        'ahmedabad': ['gujarat', 'gandhinagar', 'vadodara', 'surat', 'rajkot',
                     'anand', 'bharuch', 'jamnagar', 'bhavnagar', 'junagadh'],
        'jaipur': ['rajasthan', 'jodhpur', 'udaipur', 'ajmer', 'alwar',
                  'sikar', 'bharatpur', 'bikaner', 'kota', 'churu'],
        'lucknow': ['uttar pradesh', 'kanpur', 'agra', 'varanasi', 'allahabad',
                   'meerut', 'bareilly', 'aligarh', 'moradabad', 'gorakhpur'],
        'bhopal': ['madhya pradesh', 'indore', 'jabalpur', 'gwalior', 'ujjain',
                  'sagar', 'ratlam', 'dewas', 'khandwa', 'burhanpur'],
        'patna': ['bihar', 'gaya', 'muzaffarpur', 'darbhanga', 'bhagalpur',
                 'purnia', 'katihar', 'begusarai', 'samastipur'],
        'thiruvananthapuram': ['kerala', 'kochi', 'kozhikode', 'thrissur', 'kollam',
                              'alappuzha', 'kottayam', 'idukki', 'ernakulam'],
        'bhubaneswar': ['odisha', 'cuttack', 'puri', 'rourkela', 'sambalpur',
                       'berhampur', 'balasore', 'koraput', 'kalahandi'],
        # Additional specific entries for your area
        'penamaluru': ['krishna', 'guntur', 'andhra pradesh', 'madanapalli', 'krishnai', 'tirupati'],
        'guntur': ['andhra pradesh', 'vijayawada', 'krishna', 'madanapalli', 'tirupati', 'ongole'],
        'krishna': ['andhra pradesh', 'vijayawada', 'guntur', 'madanapalli', 'krishnai']
    }
    
    return nearby_map.get(location.lower(), [])

async def handle_query_without_ai(query: str, location: str, user_context: dict) -> str:
    """Handle queries when OpenAI is not configured"""
    query_lower = query.lower()
    
    # Extract location from query if not provided
    if not location:
        location = extract_location_from_query(query)
    
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
        else:
            return "Please specify a location for weather information. Example: 'weather in Mumbai'"
    
    # Price queries
    elif any(word in query_lower for word in ["price", "cost", "rate", "market"]):
        try:
            # Extract commodity if mentioned
            commodities = ["onion", "tomato", "potato", "rice", "wheat", "cotton", "sugarcane", "banana", "apple", "maize", "groundnut"]
            commodity = None
            for c in commodities:
                if c in query_lower:
                    commodity = c
                    break
            
            # Extract location from query - prioritize query location over auto-detected location
            query_location = extract_location_from_query(query)
            final_location = query_location if query_location else location
            
            print(f"DEBUG: Query location extracted: '{query_location}', Auto-detected: '{location}', Final: '{final_location}'")
            
            price_data = await agri_agent.get_commodity_prices(commodity, final_location)
            if "error" not in price_data:
                data = price_data.get("data", [])
                if data:
                    response = f"💰 Current Market Prices"
                    if commodity:
                        response += f" for {commodity.title()}"
                    if final_location:
                        response += f" in {final_location}"
                    response += ":\n\n"
                    
                    # Filter by location if specified
                    filtered_data = data
                    if final_location:
                        # First try exact location match
                        filtered_data = [record for record in data 
                                       if final_location.lower() in record.get("market", "").lower() or 
                                          final_location.lower() in record.get("state", "").lower() or
                                          final_location.lower() in record.get("district", "").lower()]
                        
                        print(f"DEBUG: Exact match for '{final_location}': found {len(filtered_data)} records")
                        
                        # If no exact match, try partial matches with nearby regions
                        if not filtered_data:
                            # For major cities, check nearby regions
                            nearby_keywords = get_nearby_regions(final_location.lower())
                            print(f"DEBUG: Nearby keywords for '{final_location}': {nearby_keywords}")
                            for keyword in nearby_keywords:
                                filtered_data = [record for record in data 
                                               if keyword in record.get("market", "").lower() or 
                                                  keyword in record.get("state", "").lower() or
                                                  keyword in record.get("district", "").lower()]
                                if filtered_data:
                                    print(f"DEBUG: Found {len(filtered_data)} records for keyword '{keyword}'")
                                    break
                        
                        # If still no match, fallback to general data
                        if not filtered_data:
                            print(f"DEBUG: No matches found, falling back to general data")
                            filtered_data = data[:5]
                    
                    for record in filtered_data[:5]:  # Show first 5 records
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
    
    # Irrigation queries
    elif any(word in query_lower for word in ["irrigate", "water", "irrigation"]):
        return ("🌱 **Irrigation Guidance:**\n\n"
                "• **Check soil moisture** before watering\n"
                "• **Morning hours (6-8 AM)** are best for irrigation\n"
                "• **Avoid watering during hot afternoon**\n"
                "• **Water deeply but less frequently** for most crops\n"
                "• **Check weather forecast** - avoid watering before rain\n\n"
                "For specific crop advice, mention your crop type!")
    
    # Loan/finance queries
    elif any(word in query_lower for word in ["loan", "credit", "finance", "scheme", "subsidy"]):
        return ("💳 **Agricultural Finance Options:**\n\n"
                "**Central Schemes:**\n"
                "• **PM-KISAN**: ₹6,000/year direct income support\n"
                "• **KCC (Kisan Credit Card)**: Crop loans at 7% interest\n"
                "• **PMFBY**: Crop insurance scheme\n\n"
                "**How to Apply:**\n"
                "• Visit nearest bank branch\n"
                "• Contact local agricultural officer\n"
                "• Apply online at pmkisan.gov.in\n\n"
                "Required: Aadhaar, land records, bank account")
    
    # Crop queries
    elif any(word in query_lower for word in ["crop", "seed", "variety", "plant", "sow"]):
        return ("🌾 **Crop Selection Tips:**\n\n"
                "• **Consider your soil type** (black, red, alluvial)\n"
                "• **Check rainfall pattern** in your area\n"
                "• **Choose disease-resistant varieties**\n"
                "• **Consider market demand** and prices\n"
                "• **Consult local agricultural extension officer**\n\n"
                "Popular crops by season:\n"
                "• **Kharif**: Rice, cotton, sugarcane\n"
                "• **Rabi**: Wheat, mustard, gram")
    
    # General response
    else:
        return ("🌾 **BhoomiSetu Agricultural Advisor**\n\n"
                "I can help you with:\n"
                "• **Weather forecasts** - 'weather in [city]'\n"
                "• **Market prices** - 'tomato prices'\n"
                "• **Irrigation advice** - 'when to water crops'\n"
                "• **Government schemes** - 'loan information'\n"
                "• **Crop guidance** - 'which seeds to plant'\n\n"
                "Try asking specific questions!")

@app.post("/api/weather")
async def get_weather(request: WeatherRequest):
    """Get weather data for location"""
    try:
        weather_data = await agri_agent.get_weather_data(request.location)
        return JSONResponse(content=weather_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prices")
async def get_prices(request: PriceRequest):
    """Get commodity prices"""
    try:
        price_data = await agri_agent.get_commodity_prices(request.commodity, request.location if hasattr(request, 'location') else None)
        return JSONResponse(content=price_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crops")
async def get_crop_info():
    """Get information about supported crops"""
    return JSONResponse(content=agri_agent.crop_knowledge)

@app.get("/api/schemes")
async def get_financial_schemes():
    """Get information about financial schemes"""
    return JSONResponse(content=agri_agent.financial_schemes)

@app.post("/chat")
async def chat_submit(
    request: Request, 
    message: str = Form("", description="User message"), 
    location: str = Form("", description="User location"),
    latitude: str = Form("", description="Latitude coordinate"),
    longitude: str = Form("", description="Longitude coordinate")
):
    """Handle chat form submission - returns JSON for AJAX requests"""
    try:
        # Debug logging
        print(f"DEBUG: Chat form submission - message: '{message}', location: '{location}', latitude: '{latitude}', longitude: '{longitude}'")
        
        # Validate that message is not empty
        if not message or message.strip() == "":
            print("DEBUG: Empty message received")
            return {"response": "Please enter a message to get started!"}
        
        # Determine location from coordinates if not provided
        if not location and latitude and longitude:
            try:
                location = await get_city_from_coordinates(float(latitude), float(longitude))
                print(f"DEBUG: Location from coordinates: {location}")
            except ValueError as e:
                print(f"DEBUG: Invalid coordinates: {e}")
                pass  # Invalid coordinates
        
        # Process the message
        user_context = {
            "location": location,
            "coordinates": {
                "latitude": float(latitude) if latitude else None,
                "longitude": float(longitude) if longitude else None
            } if latitude and longitude else None
        }
        
        print(f"DEBUG: User context: {user_context}")
        
        # Always try to use AI agent (now supports Grok as fallback)
        response = await agri_agent.process_query(
            query=message,
            location=location,
            user_context=user_context
        )
        
        print(f"DEBUG: Full response generated:")
        print(f"DEBUG: {response}")
        print(f"DEBUG: Response length: {len(response)} characters")
        
        # Return JSON response for AJAX requests
        return {"response": response}
    
    except Exception as e:
        print(f"DEBUG: Chat error: {e}")
        print(f"DEBUG: Chat error type: {type(e)}")
        return {"response": f"Sorry, I encountered an error: {str(e)}"}

@app.get("/weather/{location}")
async def weather_page(request: Request, location: str):
    """Weather information page"""
    try:
        weather_data = await agri_agent.get_weather_data(location)
        return templates.TemplateResponse("weather.html", {
            "request": request,
            "location": location,
            "weather": weather_data
        })
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e)
        })

@app.get("/prices")
async def prices_page(request: Request):
    """Market prices page"""
    try:
        price_data = await agri_agent.get_commodity_prices(user_location="Vijayawada")
        return templates.TemplateResponse("prices.html", {
            "request": request,
            "prices": price_data
        })
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e)
        })

@app.get("/schemes")
async def schemes_page(request: Request):
    """Financial schemes page"""
    return templates.TemplateResponse("schemes.html", {
        "request": request,
        "schemes": agri_agent.financial_schemes
    })

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
