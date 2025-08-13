"""
MCP Client for BhoomiSetu Agricultural AI
Provides easy-to-use client interface for interacting with the MCP server
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import base64
from io import BytesIO

from .models import (
    ModelInfo, ChatRequest, ChatResponse, PredictionRequest, PredictionResponse,
    CropRecommendationRequest, CropRecommendationResponse,
    DiseaseDetectionRequest, DiseaseDetectionResponse,
    HealthResponse, ServerMetadata, Coordinates
)

class MCPClientError(Exception):
    """Custom exception for MCP client errors"""
    pass

class BhoomiSetuMCPClient:
    """Client for interacting with BhoomiSetu MCP server"""
    
    def __init__(self, base_url: str = "http://localhost:8001", timeout: int = 30):
        """
        Initialize MCP client
        
        Args:
            base_url: Base URL of the MCP server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to MCP server"""
        if not self.session:
            raise MCPClientError("Client session not initialized. Use async context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise MCPClientError(f"HTTP {response.status}: {error_text}")
        except aiohttp.ClientError as e:
            raise MCPClientError(f"Request failed: {str(e)}")
    
    async def get_health(self) -> HealthResponse:
        """Get server health status"""
        data = await self._make_request("GET", "/v1/health")
        return HealthResponse(**data)
    
    async def get_metadata(self) -> ServerMetadata:
        """Get server metadata"""
        data = await self._make_request("GET", "/v1/metadata")
        return ServerMetadata(**data)
    
    async def list_models(self) -> List[ModelInfo]:
        """Get list of available models"""
        data = await self._make_request("GET", "/v1/models")
        return [ModelInfo(**model) for model in data]
    
    async def get_model_info(self, model_id: str) -> ModelInfo:
        """Get information about a specific model"""
        data = await self._make_request("GET", f"/v1/models/{model_id}")
        return ModelInfo(**data)
    
    async def chat(
        self, 
        message: str,
        language: str = "en",
        location: Optional[str] = None,
        coordinates: Optional[Coordinates] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        use_claude: bool = False
    ) -> ChatResponse:
        """
        Chat with the agricultural AI agent
        
        Args:
            message: User message
            language: Response language
            location: User location
            coordinates: Geographic coordinates
            conversation_history: Previous conversation
            context: Additional context
            use_claude: Whether to specifically use Claude AI
            
        Returns:
            ChatResponse with AI response
        """
        context = context or {}
        if use_claude:
            context["use_claude"] = True
            
        request = ChatRequest(
            message=message,
            language=language,
            location=location,
            coordinates=coordinates,
            conversation_history=conversation_history or [],
            context=context
        )
        
        data = await self._make_request(
            "POST", 
            "/v1/chat",
            json=request.model_dump()
        )
        return ChatResponse(**data)
    
    async def predict(
        self, 
        model_id: str, 
        input_data: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> PredictionResponse:
        """
        Make a prediction using a specific model
        
        Args:
            model_id: Model identifier
            input_data: Input data for prediction
            parameters: Additional parameters
            
        Returns:
            PredictionResponse with prediction result
        """
        request = PredictionRequest(
            model_id=model_id,
            input_data=input_data,
            parameters=parameters or {}
        )
        
        data = await self._make_request(
            "POST",
            f"/v1/models/{model_id}/predict",
            json=request.model_dump()
        )
        return PredictionResponse(**data)
    
    async def recommend_crops(
        self,
        soil_type: Optional[str] = None,
        climate_zone: Optional[str] = None,
        season: Optional[str] = None,
        farm_size: Optional[float] = None,
        irrigation_type: Optional[str] = None,
        location: Optional[str] = None,
        coordinates: Optional[Coordinates] = None,
        budget: Optional[float] = None,
        experience_level: Optional[str] = None
    ) -> CropRecommendationResponse:
        """
        Get crop recommendations
        
        Args:
            soil_type: Type of soil
            climate_zone: Climate zone
            season: Current season
            farm_size: Farm size in acres
            irrigation_type: Irrigation type
            location: Location name
            coordinates: Geographic coordinates
            budget: Available budget
            experience_level: Farmer experience level
            
        Returns:
            CropRecommendationResponse with recommendations
        """
        request = CropRecommendationRequest(
            soil_type=soil_type,
            climate_zone=climate_zone,
            season=season,
            farm_size=farm_size,
            irrigation_type=irrigation_type,
            location=location,
            coordinates=coordinates,
            budget=budget,
            experience_level=experience_level
        )
        
        data = await self._make_request(
            "POST",
            "/v1/models/crop-recommender/recommend",
            json=request.model_dump()
        )
        return CropRecommendationResponse(**data)
    
    async def detect_disease(
        self,
        crop_type: str,
        symptoms: List[str],
        location: Optional[str] = None,
        weather_conditions: Optional[Dict[str, Any]] = None,
        image_data: Optional[str] = None
    ) -> DiseaseDetectionResponse:
        """
        Detect crop diseases based on symptoms
        
        Args:
            crop_type: Type of crop
            symptoms: List of observed symptoms
            location: Location
            weather_conditions: Current weather
            image_data: Base64 encoded image data
            
        Returns:
            DiseaseDetectionResponse with detection results
        """
        request = DiseaseDetectionRequest(
            crop_type=crop_type,
            symptoms=symptoms,
            location=location,
            weather_conditions=weather_conditions,
            image_data=image_data
        )
        
        data = await self._make_request(
            "POST",
            "/v1/models/disease-detector/detect",
            json=request.model_dump()
        )
        return DiseaseDetectionResponse(**data)
    
    async def classify_plant_disease(
        self, 
        image_data: Union[bytes, str, BytesIO],
        filename: str = "image.jpg"
    ) -> PredictionResponse:
        """
        Classify plant disease from image
        
        Args:
            image_data: Image data (bytes, base64 string, or BytesIO)
            filename: Image filename
            
        Returns:
            PredictionResponse with classification result
        """
        # Prepare image data
        if isinstance(image_data, str):
            # Assume base64 encoded
            image_bytes = base64.b64decode(image_data)
        elif isinstance(image_data, BytesIO):
            image_bytes = image_data.getvalue()
        else:
            image_bytes = image_data
        
        # Prepare multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field(
            'file',
            image_bytes,
            filename=filename,
            content_type='image/jpeg'
        )
        
        data = await self._make_request(
            "POST",
            "/v1/models/plant-disease-cnn/classify",
            data=form_data
        )
        return PredictionResponse(**data)
    
    # Convenience methods for common tasks
    
    async def ask_question(
        self, 
        question: str, 
        language: str = "en",
        location: Optional[str] = None
    ) -> str:
        """
        Ask a simple question and get text response
        
        Args:
            question: Question to ask
            language: Response language
            location: User location
            
        Returns:
            Text response from AI
        """
        response = await self.chat(
            message=question,
            language=language,
            location=location
        )
        return response.message
    
    async def get_crop_advice(
        self,
        farm_description: str,
        location: Optional[str] = None,
        season: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get crop recommendations based on farm description
        
        Args:
            farm_description: Description of farm conditions
            location: Farm location
            season: Current season
            
        Returns:
            List of recommended crops
        """
        recommendations = await self.recommend_crops(
            location=location,
            season=season
        )
        return recommendations.recommended_crops
    
    async def diagnose_plant(
        self,
        crop_type: str,
        symptoms: List[str],
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Diagnose plant diseases based on symptoms
        
        Args:
            crop_type: Type of crop
            symptoms: Observed symptoms
            location: Location
            
        Returns:
            Diagnosis results with treatments
        """
        detection = await self.detect_disease(
            crop_type=crop_type,
            symptoms=symptoms,
            location=location
        )
        
        return {
            "diseases": detection.detected_diseases,
            "treatments": detection.treatment_recommendations,
            "prevention": detection.prevention_tips
        }
    
    async def analyze_plant_image(self, image_data: Union[bytes, str]) -> Dict[str, Any]:
        """
        Analyze plant image for disease detection
        
        Args:
            image_data: Image data
            
        Returns:
            Analysis results
        """
        result = await self.classify_plant_disease(image_data)
        return result.prediction
    
    async def is_server_healthy(self) -> bool:
        """
        Check if server is healthy
        
        Returns:
            True if server is healthy
        """
        try:
            health = await self.get_health()
            return health.status == "healthy"
        except:
            return False


# Utility functions for easy client usage

async def quick_chat(message: str, server_url: str = "http://localhost:8001") -> str:
    """
    Quick chat without managing client lifecycle
    
    Args:
        message: Message to send
        server_url: MCP server URL
        
    Returns:
        AI response text
    """
    async with BhoomiSetuMCPClient(server_url) as client:
        return await client.ask_question(message)

async def quick_crop_recommendation(
    farm_description: str, 
    location: str = None,
    server_url: str = "http://localhost:8001"
) -> List[Dict[str, Any]]:
    """
    Quick crop recommendation without managing client lifecycle
    
    Args:
        farm_description: Farm description
        location: Farm location
        server_url: MCP server URL
        
    Returns:
        List of crop recommendations
    """
    async with BhoomiSetuMCPClient(server_url) as client:
        return await client.get_crop_advice(farm_description, location)

async def quick_disease_diagnosis(
    crop_type: str,
    symptoms: List[str],
    server_url: str = "http://localhost:8001"
) -> Dict[str, Any]:
    """
    Quick disease diagnosis without managing client lifecycle
    
    Args:
        crop_type: Type of crop
        symptoms: List of symptoms
        server_url: MCP server URL
        
    Returns:
        Diagnosis results
    """
    async with BhoomiSetuMCPClient(server_url) as client:
        return await client.diagnose_plant(crop_type, symptoms)
