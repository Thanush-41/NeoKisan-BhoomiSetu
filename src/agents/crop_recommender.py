"""
Crop Recommendation Agent using OpenAI and ML model
Provides intelligent crop recommendations based on location and soil conditions
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import openai
from openai import AsyncOpenAI
from dotenv import load_dotenv
import json
import logging
import aiohttp
import asyncio

load_dotenv()
logger = logging.getLogger(__name__)

class CropRecommendationAgent:
    def __init__(self):
        """Initialize the Crop Recommendation Agent"""
        print("🌾 Initializing Crop Recommendation Agent...")
        
        # Initialize OpenAI client
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key != 'your_openai_api_key_here':
            try:
                self.openai_client = AsyncOpenAI(api_key=openai_key)
                print("✅ OpenAI client initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            self.openai_client = None
            print("⚠️ OpenAI API key not found. Some features may be limited.")
        
        # Initialize OpenWeather API
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.weather_api_key:
            print("⚠️ OpenWeather API key not found. Will use default weather values.")
        
        # Load and prepare the dataset
        self.dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge", "Crop_recommendation.csv")
        self.model = None
        self.scaler = None
        self.feature_columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        
        # Initialize the ML model
        self._prepare_model()
        
        # Regional soil data for Indian states
        self.regional_soil_data = {
            "punjab": {"N": 85, "P": 50, "K": 45, "ph": 7.2, "temperature": 25, "humidity": 70, "rainfall": 600},
            "haryana": {"N": 80, "P": 48, "K": 43, "ph": 7.5, "temperature": 26, "humidity": 65, "rainfall": 550},
            "uttar pradesh": {"N": 75, "P": 45, "K": 40, "ph": 7.0, "temperature": 27, "humidity": 75, "rainfall": 800},
            "bihar": {"N": 70, "P": 42, "K": 38, "ph": 6.8, "temperature": 28, "humidity": 80, "rainfall": 1200},
            "west bengal": {"N": 65, "P": 40, "K": 35, "ph": 6.5, "temperature": 29, "humidity": 85, "rainfall": 1500},
            "maharashtra": {"N": 60, "P": 35, "K": 30, "ph": 6.0, "temperature": 30, "humidity": 70, "rainfall": 700},
            "karnataka": {"N": 55, "P": 38, "K": 32, "ph": 6.2, "temperature": 28, "humidity": 75, "rainfall": 900},
            "tamil nadu": {"N": 50, "P": 40, "K": 35, "ph": 6.8, "temperature": 31, "humidity": 80, "rainfall": 1000},
            "andhra pradesh": {"N": 58, "P": 42, "K": 38, "ph": 6.5, "temperature": 30, "humidity": 78, "rainfall": 850},
            "telangana": {"N": 55, "P": 40, "K": 36, "ph": 6.7, "temperature": 29, "humidity": 76, "rainfall": 750},
            "rajasthan": {"N": 45, "P": 30, "K": 25, "ph": 7.8, "temperature": 35, "humidity": 40, "rainfall": 300},
            "gujarat": {"N": 50, "P": 35, "K": 28, "ph": 7.5, "temperature": 32, "humidity": 60, "rainfall": 500},
            "madhya pradesh": {"N": 65, "P": 40, "K": 35, "ph": 6.9, "temperature": 28, "humidity": 70, "rainfall": 900},
            "odisha": {"N": 60, "P": 38, "K": 33, "ph": 6.4, "temperature": 30, "humidity": 82, "rainfall": 1400},
            "kerala": {"N": 40, "P": 35, "K": 45, "ph": 5.5, "temperature": 28, "humidity": 90, "rainfall": 3000},
        }
    
    def _prepare_model(self):
        """Load and train the ML model for crop recommendation"""
        try:
            # Try to load existing model
            if os.path.exists("crop_model.pkl") and os.path.exists("crop_scaler.pkl"):
                self.model = joblib.load("crop_model.pkl")
                self.scaler = joblib.load("crop_scaler.pkl")
                print("✅ Loaded existing crop recommendation model")
                return
            
            # Load dataset
            if os.path.exists(self.dataset_path):
                df = pd.read_csv(self.dataset_path)
                print(f"📊 Loaded dataset with {len(df)} records")
                
                # Prepare features and target
                X = df[self.feature_columns]
                y = df['label']
                
                # Split the data
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Scale features
                self.scaler = StandardScaler()
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_test_scaled = self.scaler.transform(X_test)
                
                # Train model
                self.model = RandomForestClassifier(n_estimators=100, random_state=42)
                self.model.fit(X_train_scaled, y_train)
                
                # Evaluate model
                y_pred = self.model.predict(X_test_scaled)
                accuracy = accuracy_score(y_test, y_pred)
                print(f"✅ Model trained with accuracy: {accuracy:.2f}")
                
                # Save model
                joblib.dump(self.model, "crop_model.pkl")
                joblib.dump(self.scaler, "crop_scaler.pkl")
                
            else:
                print(f"⚠️ Dataset {self.dataset_path} not found. Creating dummy model.")
                self._create_dummy_model()
                
        except Exception as e:
            print(f"❌ Error preparing model: {e}")
            self._create_dummy_model()
    
    def _create_dummy_model(self):
        """Create a dummy model for testing purposes"""
        # Create dummy data
        np.random.seed(42)
        dummy_data = []
        crops = ['rice', 'wheat', 'sugarcane', 'cotton', 'maize', 'soybean', 'groundnut']
        
        for _ in range(1000):
            dummy_data.append([
                np.random.uniform(20, 100),  # N
                np.random.uniform(15, 80),   # P
                np.random.uniform(10, 60),   # K
                np.random.uniform(15, 40),   # temperature
                np.random.uniform(40, 95),   # humidity
                np.random.uniform(4, 9),     # ph
                np.random.uniform(100, 2000), # rainfall
                np.random.choice(crops)      # label
            ])
        
        df = pd.DataFrame(dummy_data, columns=self.feature_columns + ['label'])
        
        X = df[self.feature_columns]
        y = df['label']
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.model.fit(X_scaled, y)
        
        print("✅ Created dummy model for testing")
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, float]:
        """Fetch current weather data from OpenWeather API using coordinates"""
        if not self.weather_api_key:
            print("⚠️ No weather API key, using default values")
            return None
            
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.weather_api_key,
                'units': 'metric'  # Get temperature in Celsius
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract relevant weather data
                        weather_data = {
                            'temperature': data['main']['temp'],
                            'humidity': data['main']['humidity'],
                            'rainfall': 0  # Current weather doesn't include rainfall, we'll estimate
                        }
                        
                        # Try to get precipitation data if available
                        if 'rain' in data:
                            # Rain data is in mm for last 1h or 3h
                            rainfall_1h = data['rain'].get('1h', 0)
                            rainfall_3h = data['rain'].get('3h', 0)
                            # Estimate annual rainfall (very rough approximation)
                            if rainfall_1h > 0:
                                weather_data['rainfall'] = rainfall_1h * 24 * 365  # mm/year approximation
                            elif rainfall_3h > 0:
                                weather_data['rainfall'] = (rainfall_3h / 3) * 24 * 365
                        
                        print(f"🌤️ Current weather: {weather_data['temperature']}°C, {weather_data['humidity']}% humidity")
                        return weather_data
                    else:
                        print(f"⚠️ Weather API error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Error fetching weather data: {e}")
            return None
    
    async def get_historical_weather_estimate(self, latitude: float, longitude: float) -> Dict[str, float]:
        """Get weather averages/estimates for the location using a different approach"""
        try:
            # Use a simpler approach - get current weather and make reasonable estimates
            current_weather = await self.get_current_weather(latitude, longitude)
            if current_weather:
                # Use current temperature and humidity, estimate rainfall based on region
                rainfall_estimate = 800  # Default
                
                # Regional rainfall estimates based on coordinates (rough approximation)
                if 8 <= latitude <= 37 and 68 <= longitude <= 97:  # India bounds
                    if latitude < 15:  # Southern India
                        rainfall_estimate = 1200
                    elif latitude > 30:  # Northern India
                        rainfall_estimate = 600
                    else:  # Central India
                        rainfall_estimate = 900
                
                # If current weather has rainfall data, use it, otherwise use estimate
                if current_weather['rainfall'] == 0:
                    current_weather['rainfall'] = rainfall_estimate
                    
                return current_weather
            
        except Exception as e:
            print(f"❌ Error getting weather estimate: {e}")
        
        return None
    
    async def extract_soil_data_from_text(self, user_input: str) -> Dict[str, float]:
        """Use OpenAI to extract soil and environmental data from user's natural language input"""
        if not self.openai_client:
            # Fallback: try to extract basic location info
            return self._extract_basic_location_data(user_input.lower())
        
        try:
            prompt = f"""
            Extract soil and environmental data from the following user input about their farm location and conditions.
            
            User input: "{user_input}"
            
            Please extract or estimate the following values and return them as a JSON object:
            - N (Nitrogen content): 0-100
            - P (Phosphorus content): 0-100
            - K (Potassium content): 0-100
            - temperature (in Celsius): 15-40
            - humidity (percentage): 40-95
            - ph (soil pH): 4-9
            - rainfall (annual in mm): 100-3000
            
            If specific values are not mentioned, use your knowledge of Indian agriculture and regional patterns to estimate reasonable values for the mentioned location or soil type.
            
            Return only a valid JSON object with these exact keys:
            {{
                "N": value,
                "P": value,
                "K": value,
                "temperature": value,
                "humidity": value,
                "ph": value,
                "rainfall": value
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                soil_data = json.loads(result)
                
                # Validate the data
                required_keys = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
                if all(key in soil_data for key in required_keys):
                    return soil_data
                else:
                    print(f"⚠️ Missing keys in OpenAI response: {result}")
                    return self._extract_basic_location_data(user_input.lower())
                    
            except json.JSONDecodeError:
                print(f"⚠️ Invalid JSON from OpenAI: {result}")
                return self._extract_basic_location_data(user_input.lower())
                
        except Exception as e:
            print(f"❌ Error with OpenAI extraction: {e}")
            return self._extract_basic_location_data(user_input.lower())
    
    def _extract_basic_location_data(self, user_input: str) -> Dict[str, float]:
        """Fallback method to extract basic location data"""
        # Check for Indian states/regions in user input
        for state, data in self.regional_soil_data.items():
            if state in user_input.lower():
                print(f"📍 Detected location: {state.title()}")
                return data
        
        # Check for major cities that map to states
        city_state_mapping = {
            "mumbai": "maharashtra",
            "delhi": "haryana",  # Close enough climate-wise
            "bangalore": "karnataka",
            "bengaluru": "karnataka",
            "chennai": "tamil nadu",
            "hyderabad": "telangana",
            "pune": "maharashtra",
            "ahmedabad": "gujarat",
            "kolkata": "west bengal",
            "surat": "gujarat",
            "jaipur": "rajasthan",
            "lucknow": "uttar pradesh",
            "kanpur": "uttar pradesh",
            "nagpur": "maharashtra",
            "indore": "madhya pradesh",
            "thane": "maharashtra",
            "bhopal": "madhya pradesh",
            "visakhapatnam": "andhra pradesh",
            "pimpri": "maharashtra",
            "patna": "bihar",
            "vadodara": "gujarat",
            "ghaziabad": "uttar pradesh",
            "ludhiana": "punjab",
            "agra": "uttar pradesh",
            "nashik": "maharashtra",
            "faridabad": "haryana",
            "meerut": "uttar pradesh",
            "rajkot": "gujarat"
        }
        
        user_input_lower = user_input.lower()
        for city, state in city_state_mapping.items():
            if city in user_input_lower and state in self.regional_soil_data:
                print(f"📍 Detected city {city.title()} -> state {state.title()}")
                return self.regional_soil_data[state]
        
        # Default values for general Indian conditions
        print("📍 Using default Indian agricultural conditions")
        return {
            "N": 60,
            "P": 40,
            "K": 35,
            "temperature": 28,
            "humidity": 75,
            "ph": 6.5,
            "rainfall": 800
        }
    
    async def recommend_crops(self, user_input: str, location: Optional[str] = None, coordinates: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Recommend crops based on user input about their location and soil conditions
        
        Args:
            user_input: User's description of their location, soil, or farming conditions
            location: Optional specific location
            coordinates: Optional dict with 'latitude' and 'longitude' keys
            
        Returns:
            Dictionary with recommended crops and explanations
        """
        try:
            # Extract soil and environmental data
            soil_data = await self.extract_soil_data_from_text(user_input)
            
            # Try to get current weather data if coordinates are provided
            if coordinates and 'latitude' in coordinates and 'longitude' in coordinates:
                print(f"🌤️ Fetching current weather for coordinates: {coordinates['latitude']:.2f}, {coordinates['longitude']:.2f}")
                weather_data = await self.get_historical_weather_estimate(
                    coordinates['latitude'], 
                    coordinates['longitude']
                )
                
                if weather_data:
                    print(f"✅ Using current weather: {weather_data['temperature']}°C, {weather_data['humidity']}%, {weather_data['rainfall']}mm")
                    # Update soil_data with current weather
                    soil_data['temperature'] = weather_data['temperature']
                    soil_data['humidity'] = weather_data['humidity']
                    
                    # Only update rainfall if we got a reasonable value
                    if weather_data['rainfall'] > 0:
                        soil_data['rainfall'] = weather_data['rainfall']
                else:
                    print("⚠️ Could not fetch weather data, using estimated values")
            
            # Prepare features for prediction
            features = [
                soil_data['N'],
                soil_data['P'],
                soil_data['K'],
                soil_data['temperature'],
                soil_data['humidity'],
                soil_data['ph'],
                soil_data['rainfall']
            ]
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Get prediction
            predicted_crop = self.model.predict(features_scaled)[0]
            
            # Get prediction probabilities for top recommendations
            probabilities = self.model.predict_proba(features_scaled)[0]
            classes = self.model.classes_
            
            # Get top 3 recommendations
            top_indices = probabilities.argsort()[-3:][::-1]
            recommendations = []
            
            for i in top_indices:
                recommendations.append({
                    "crop": classes[i],
                    "confidence": float(probabilities[i]),
                    "percentage": round(probabilities[i] * 100, 1)
                })
            
            # Generate detailed explanation using OpenAI (if available)
            explanation = await self._generate_explanation(soil_data, recommendations, user_input)
            
            return {
                "primary_recommendation": predicted_crop,
                "top_recommendations": recommendations,
                "soil_analysis": soil_data,
                "explanation": explanation,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error in crop recommendation: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    async def _generate_explanation(self, soil_data: Dict, recommendations: List, user_input: str) -> str:
        """Generate detailed explanation for crop recommendations"""
        if not self.openai_client:
            # Fallback explanation
            primary_crop = recommendations[0]['crop']
            return f"Based on your soil conditions and location, {primary_crop} appears to be the most suitable crop. This recommendation considers factors like soil nutrients (N: {soil_data['N']}, P: {soil_data['P']}, K: {soil_data['K']}), pH level ({soil_data['ph']}), and climate conditions."
        
        try:
            crops_text = ", ".join([f"{rec['crop']} ({rec['percentage']}%)" for rec in recommendations])
            
            prompt = f"""
            You are an agricultural expert providing crop recommendations to Indian farmers.
            
            User's situation: "{user_input}"
            
            Soil Analysis:
            - Nitrogen (N): {soil_data['N']}
            - Phosphorus (P): {soil_data['P']}
            - Potassium (K): {soil_data['K']}
            - Temperature: {soil_data['temperature']}°C
            - Humidity: {soil_data['humidity']}%
            - Soil pH: {soil_data['ph']}
            - Rainfall: {soil_data['rainfall']}mm
            
            Recommended crops: {crops_text}
            
            Provide a detailed but concise explanation (2-3 paragraphs) in simple language that:
            1. Explains why these crops are suitable for the given conditions
            2. Mentions specific soil/climate factors that favor these crops
            3. Gives practical advice about farming these crops
            4. Considers the Indian agricultural context
            
            Keep the language farmer-friendly and avoid overly technical terms.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error generating explanation: {e}")
            primary_crop = recommendations[0]['crop']
            return f"Based on your soil conditions and location, {primary_crop} appears to be the most suitable crop for your farm."

# Create global instance
crop_recommender = CropRecommendationAgent()
