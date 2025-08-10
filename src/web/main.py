"""
FastAPI Web Application for BhoomiSetu Agricultural AI Agent
Provides web interface and REST API endpoints
"""

import os
import json
import asyncio
from typing import Dict, Optional, List
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException, Depends, Header, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ValidationError
import uvicorn
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agents.agri_agent import agri_agent
from services.firebase_service import firebase_service
from services.mongodb_service import mongodb_service, startup_mongodb, shutdown_mongodb
from services.crop_disease_service import crop_disease_service
from models.auth_models import (
    UserRegistration, UserLogin, TokenVerification, UserResponse,
    ChatThreadCreate, ChatMessage, ChatThreadResponse, ChatMessageResponse
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="BhoomiSetu - Agricultural AI Advisor",
    description="AI-powered agricultural advisor for Indian farmers",
    version="1.0.0"
)

# Security
security = HTTPBearer(auto_error=False)

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

# Authentication Helper Functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from token"""
    if not credentials:
        return None
    
    token_verification = await firebase_service.verify_token(credentials.credentials)
    if token_verification.get("error"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token_verification

async def require_auth(current_user: dict = Depends(get_current_user)):
    """Require authentication for protected routes"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user

async def get_city_from_coordinates(latitude: float, longitude: float) -> str:
    """Get city name from coordinates using reverse geocoding"""
    try:
        import aiohttp
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            print("WARNING: OPENWEATHER_API_KEY not found in environment")
            return "Unknown Location"
        url = f"https://api.openweathermap.org/geo/1.0/reverse?lat={latitude}&lon={longitude}&limit=1&appid={api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                
                if data and len(data) > 0:
                    return data[0].get('name', 'Unknown')
                return 'Unknown'
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        return "Unknown Location"
        return 'Unknown'

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_interface(request: Request):
    """Serve the chat interface"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def test_auth(request: Request):
    """Serve the authentication test page"""
    return templates.TemplateResponse("test_auth.html", {"request": request})

@app.get("/api/firebase-config")
async def get_firebase_config():
    """Get Firebase configuration for client-side initialization"""
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
    }

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

@app.get("/api/geocode")
async def geocode_location(lat: float, lon: float):
    """Secure server-side geocoding endpoint"""
    try:
        import aiohttp
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenWeather API key not configured")
        
        url = f"https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                
                if data and len(data) > 0:
                    location = data[0]
                    return JSONResponse(content={
                        "city": location.get('name', 'Unknown'),
                        "address": f"{location.get('name', 'Unknown')}, {location.get('state', '')}, {location.get('country', '')}"
                    })
                else:
                    return JSONResponse(content={
                        "city": "Unknown Location",
                        "address": "Unknown Location"
                    })
    except Exception as e:
        print(f"Geocoding error: {e}")
        return JSONResponse(content={
            "city": "Unknown Location", 
            "address": "Unknown Location"
        })

# Crop Disease Detection Endpoints
@app.post("/api/crop-disease/predict")
async def predict_crop_disease(file: UploadFile = File(...)):
    """Predict plant disease from uploaded image"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image file
        contents = await file.read()
        
        # Get prediction from service
        result = crop_disease_service.predict_disease(contents)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return JSONResponse(content={
            "filename": file.filename,
            "predicted_class": result["predicted_class"],
            "disease_name": result["disease_name"],
            "confidence": result["confidence"],
            "explanation": result["explanation"],
            "all_predictions": result["all_predictions"]
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/crop-disease/classes")
async def get_disease_classes():
    """Get all available plant disease classes"""
    if crop_disease_service.class_indices is None:
        raise HTTPException(status_code=500, detail="Disease classes not loaded")
    
    return JSONResponse(content={
        "classes": list(crop_disease_service.class_indices.keys()),
        "total_classes": len(crop_disease_service.class_indices)
    })

@app.get("/api/crop-disease/info/{disease_name}")
async def get_disease_info(disease_name: str):
    """Get detailed information about a specific disease"""
    info = crop_disease_service.get_disease_info(disease_name)
    return JSONResponse(content=info)

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

@app.get("/weather")
async def weather_default_page(request: Request):
    """Weather information page with default location"""
    try:
        # Default to Mumbai if no location specified
        default_location = "Mumbai"
        weather_data = await agri_agent.get_weather_data(default_location)
        return templates.TemplateResponse("weather.html", {
            "request": request,
            "location": default_location,
            "weather": weather_data
        })
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e)
        })

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

@app.get("/crop-disease")
async def crop_disease_page(request: Request):
    """Crop disease detection page"""
    return templates.TemplateResponse("crop_disease.html", {
        "request": request
    })

# ========================================
# AUTHENTICATION ROUTES
# ========================================

@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    result = await firebase_service.create_user(
        email=user_data.email,
        password=user_data.password,
        display_name=user_data.display_name
    )
    
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result["user"]

@app.post("/api/auth/login", response_model=UserResponse)
async def login_user(user_data: UserLogin):
    """Login user with email and password"""
    result = await firebase_service.sign_in_user(
        email=user_data.email,
        password=user_data.password
    )
    
    if result.get("error"):
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result["user"]

@app.post("/api/auth/verify")
async def verify_token(token_data: TokenVerification):
    """Verify authentication token"""
    result = await firebase_service.verify_token(token_data.token)
    
    if result.get("error"):
        raise HTTPException(status_code=401, detail=result["error"])
    
    return {"valid": True, "user": result}

# MongoDB Chat Endpoints
@app.post("/api/chat/threads")
async def create_chat_thread(
    title: str = Form(...),
    current_user: dict = Depends(require_auth)
):
    """Create a new chat thread"""
    try:
        thread_id = await mongodb_service.create_chat_thread(
            user_id=current_user['uid'],
            title=title
        )
        return {"success": True, "thread_id": thread_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create thread: {str(e)}")

@app.get("/api/chat/threads")
async def get_user_threads(current_user: dict = Depends(require_auth)):
    """Get user's chat threads"""
    try:
        threads = await mongodb_service.get_user_threads(current_user['uid'])
        return {"threads": threads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threads: {str(e)}")

@app.post("/api/chat/threads/{thread_id}/messages")
async def save_message_to_thread(
    thread_id: str,
    content: str = Form(...),
    is_user: bool = Form(...),
    current_user: dict = Depends(require_auth)
):
    """Save a message to a chat thread"""
    try:
        message_id = await mongodb_service.save_message(
            thread_id=thread_id,
            content=content,
            is_user=is_user
        )
        return {"success": True, "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")

@app.get("/api/chat/threads/{thread_id}/messages")
async def get_thread_messages(
    thread_id: str,
    current_user: dict = Depends(require_auth)
):
    """Get messages from a chat thread"""
    try:
        messages = await mongodb_service.get_thread_messages(thread_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@app.delete("/api/chat/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    current_user: dict = Depends(require_auth)
):
    """Delete a chat thread"""
    try:
        success = await mongodb_service.delete_thread(thread_id, current_user['uid'])
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="Thread not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete thread: {str(e)}")

@app.put("/api/chat/threads/{thread_id}")
async def update_thread_title(
    thread_id: str,
    title: str = Form(...),
    current_user: dict = Depends(require_auth)
):
    """Update chat thread title"""
    try:
        success = await mongodb_service.update_thread_title(thread_id, current_user['uid'], title)
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="Thread not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update thread: {str(e)}")

@app.get("/api/chat/stats")
async def get_chat_stats(current_user: dict = Depends(require_auth)):
    """Get chat statistics"""
    try:
        stats = await mongodb_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(require_auth)):
    """Get current user information"""
    user_doc = await firebase_service.get_user_document(current_user["uid"])
    return {
        "uid": current_user["uid"],
        "email": current_user["email"],
        "profile": user_doc
    }

# ========================================
# CHAT THREAD MANAGEMENT ROUTES
# ========================================

@app.post("/api/threads/create")
async def create_thread(
    thread_data: ChatThreadCreate,
    current_user: dict = Depends(require_auth)
):
    """Create a new chat thread"""
    thread_id = await firebase_service.create_chat_thread(
        uid=current_user["uid"],
        title=thread_data.title
    )
    
    if not thread_id:
        raise HTTPException(status_code=500, detail="Failed to create thread")
    
    return {"thread_id": thread_id, "message": "Thread created successfully"}

@app.get("/api/threads")
async def get_user_threads(current_user: dict = Depends(require_auth)):
    """Get all chat threads for the current user"""
    threads = await firebase_service.get_user_threads(current_user["uid"])
    return {"threads": threads}

@app.get("/api/threads/{thread_id}/messages")
async def get_thread_messages(
    thread_id: str,
    current_user: dict = Depends(require_auth)
):
    """Get all messages in a specific thread"""
    messages = await firebase_service.get_thread_messages(thread_id)
    return {"messages": messages}

@app.delete("/api/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    current_user: dict = Depends(require_auth)
):
    """Delete a chat thread"""
    success = await firebase_service.delete_thread(thread_id, current_user["uid"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found or access denied")
    
    return {"message": "Thread deleted successfully"}

@app.post("/api/threads/{thread_id}/messages")
async def save_message_to_thread(
    thread_id: str,
    message_data: ChatMessage,
    current_user: dict = Depends(require_auth)
):
    """Save a chat message to a thread"""
    success = await firebase_service.save_chat_message(
        thread_id=thread_id,
        user_message=message_data.message,
        ai_response="",  # Will be updated after AI response
        location=message_data.location
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save message")
    
    return {"message": "Message saved successfully"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await startup_mongodb()
    crop_disease_service.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up services on shutdown"""
    await shutdown_mongodb()

if __name__ == "__main__":
    uvicorn.run(
        "src.web.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
