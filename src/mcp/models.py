"""
Model Context Protocol (MCP) models for BhoomiSetu Agricultural AI
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class ModelType(str, Enum):
    """Available model types"""
    CHAT = "chat"
    CROP_RECOMMENDATION = "crop_recommendation"
    DISEASE_DETECTION = "disease_detection"
    PLANT_DISEASE = "plant_disease"
    WEATHER_ANALYSIS = "weather_analysis"
    MARKET_PRICE = "market_price"

class ModelStatus(str, Enum):
    """Model status"""
    AVAILABLE = "available"
    LOADING = "loading"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class HealthStatus(str, Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

# Request Models
class Coordinates(BaseModel):
    """Geographic coordinates"""
    latitude: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate", ge=-180, le=180)

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message", min_length=1)
    language: Optional[str] = Field("en", description="Response language (en, hi, te, etc.)")
    location: Optional[str] = Field(None, description="User location")
    coordinates: Optional[Coordinates] = Field(None, description="Geographic coordinates")
    conversation_history: Optional[List[Dict[str, Any]]] = Field([], description="Previous conversation")
    context: Optional[Dict[str, Any]] = Field({}, description="Additional context")

class PredictionRequest(BaseModel):
    """Generic prediction request"""
    model_id: str = Field(..., description="Model identifier")
    input_data: Dict[str, Any] = Field(..., description="Input data for prediction")
    parameters: Optional[Dict[str, Any]] = Field({}, description="Additional parameters")

class CropRecommendationRequest(BaseModel):
    """Crop recommendation request"""
    soil_type: Optional[str] = Field(None, description="Type of soil")
    climate_zone: Optional[str] = Field(None, description="Climate zone")
    season: Optional[str] = Field(None, description="Current season")
    farm_size: Optional[float] = Field(None, description="Farm size in acres")
    irrigation_type: Optional[str] = Field(None, description="Irrigation type")
    location: Optional[str] = Field(None, description="Location name")
    coordinates: Optional[Coordinates] = Field(None, description="Geographic coordinates")
    budget: Optional[float] = Field(None, description="Available budget")
    experience_level: Optional[str] = Field(None, description="Farmer experience level")

class DiseaseDetectionRequest(BaseModel):
    """Disease detection request"""
    crop_type: str = Field(..., description="Type of crop")
    symptoms: List[str] = Field(..., description="List of observed symptoms")
    location: Optional[str] = Field(None, description="Location")
    weather_conditions: Optional[Dict[str, Any]] = Field(None, description="Current weather")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")

# Response Models
class ModelInfo(BaseModel):
    """Model information"""
    id: str = Field(..., description="Model unique identifier")
    name: str = Field(..., description="Model display name")
    type: ModelType = Field(..., description="Model type")
    version: str = Field(..., description="Model version")
    description: str = Field(..., description="Model description")
    status: ModelStatus = Field(..., description="Current model status")
    capabilities: List[str] = Field(..., description="Model capabilities")
    input_schema: Dict[str, Any] = Field(..., description="Input schema")
    output_schema: Dict[str, Any] = Field(..., description="Output schema")
    created_at: datetime = Field(..., description="Model creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")

class ChatResponse(BaseModel):
    """Chat response model"""
    message: str = Field(..., description="AI response message")
    language: str = Field(..., description="Response language")
    query_type: Optional[str] = Field(None, description="Detected query type")
    confidence: Optional[float] = Field(None, description="Confidence score")
    sources: Optional[List[str]] = Field([], description="Information sources")
    suggestions: Optional[List[str]] = Field([], description="Follow-up suggestions")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

class PredictionResponse(BaseModel):
    """Generic prediction response"""
    model_id: str = Field(..., description="Model identifier")
    prediction: Any = Field(..., description="Prediction result")
    confidence: Optional[float] = Field(None, description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Prediction timestamp")

class CropRecommendationResponse(BaseModel):
    """Crop recommendation response"""
    recommended_crops: List[Dict[str, Any]] = Field(..., description="List of recommended crops")
    reasons: List[str] = Field(..., description="Reasons for recommendations")
    season_advice: Optional[str] = Field(None, description="Seasonal advice")
    estimated_yield: Optional[Dict[str, float]] = Field(None, description="Estimated yields")
    investment_required: Optional[Dict[str, float]] = Field(None, description="Investment estimates")
    risk_factors: Optional[List[str]] = Field([], description="Risk factors")
    success_tips: Optional[List[str]] = Field([], description="Success tips")

class DiseaseDetectionResponse(BaseModel):
    """Disease detection response"""
    detected_diseases: List[Dict[str, Any]] = Field(..., description="Detected diseases")
    confidence_scores: Dict[str, float] = Field(..., description="Confidence scores")
    treatment_recommendations: List[str] = Field(..., description="Treatment recommendations")
    prevention_tips: List[str] = Field(..., description="Prevention tips")
    severity_level: Optional[str] = Field(None, description="Disease severity")
    immediate_actions: Optional[List[str]] = Field([], description="Immediate actions needed")

class HealthResponse(BaseModel):
    """Health check response"""
    status: HealthStatus = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    version: str = Field(..., description="Server version")
    uptime: float = Field(..., description="Server uptime in seconds")
    models_status: Dict[str, ModelStatus] = Field(..., description="Status of each model")
    dependencies: Dict[str, bool] = Field(..., description="Dependencies status")
    performance_metrics: Optional[Dict[str, Any]] = Field({}, description="Performance metrics")

class ServerMetadata(BaseModel):
    """Server metadata response"""
    name: str = Field(..., description="Server name")
    version: str = Field(..., description="Server version")
    description: str = Field(..., description="Server description")
    supported_languages: List[str] = Field(..., description="Supported languages")
    available_models: List[str] = Field(..., description="Available model IDs")
    capabilities: List[str] = Field(..., description="Server capabilities")
    api_version: str = Field(..., description="API version")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    contact: Optional[Dict[str, str]] = Field({}, description="Contact information")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field({}, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")

# Model registry for tracking available models
MODEL_REGISTRY = {
    "bhoomi-chat": ModelInfo(
        id="bhoomi-chat",
        name="BhoomiSetu Agricultural Chat",
        type=ModelType.CHAT,
        version="1.0.0",
        description="Conversational AI for agricultural queries in multiple languages",
        status=ModelStatus.AVAILABLE,
        capabilities=["multilingual_chat", "agricultural_advice", "weather_integration", "policy_guidance"],
        input_schema=ChatRequest.model_json_schema(),
        output_schema=ChatResponse.model_json_schema(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"languages": ["en", "hi", "te", "ta", "kn", "ml"], "provider": "openai"}
    ),
    "claude-chat": ModelInfo(
        id="claude-chat",
        name="Claude Agricultural Assistant",
        type=ModelType.CHAT,
        version="1.0.0",
        description="Claude AI-powered agricultural advisor with advanced reasoning capabilities",
        status=ModelStatus.AVAILABLE,
        capabilities=["multilingual_chat", "agricultural_advice", "detailed_analysis", "contextual_reasoning"],
        input_schema=ChatRequest.model_json_schema(),
        output_schema=ChatResponse.model_json_schema(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"languages": ["en", "hi", "te", "ta", "kn", "ml"], "provider": "anthropic"}
    ),
    "crop-recommender": ModelInfo(
        id="crop-recommender",
        name="Crop Recommendation System",
        type=ModelType.CROP_RECOMMENDATION,
        version="1.0.0",
        description="ML-based crop recommendation based on soil, climate, and location",
        status=ModelStatus.AVAILABLE,
        capabilities=["crop_prediction", "yield_estimation", "risk_assessment"],
        input_schema=CropRecommendationRequest.model_json_schema(),
        output_schema=CropRecommendationResponse.model_json_schema(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"supported_crops": ["rice", "wheat", "maize", "cotton", "sugarcane"], "provider": "scikit-learn"}
    ),
    "claude-crop-advisor": ModelInfo(
        id="claude-crop-advisor",
        name="Claude Crop Advisor",
        type=ModelType.CROP_RECOMMENDATION,
        version="1.0.0",
        description="Claude AI-powered crop recommendation with detailed reasoning and context awareness",
        status=ModelStatus.AVAILABLE,
        capabilities=["intelligent_crop_selection", "context_aware_recommendations", "detailed_explanations"],
        input_schema=CropRecommendationRequest.model_json_schema(),
        output_schema=CropRecommendationResponse.model_json_schema(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"supported_crops": ["all_indian_crops"], "provider": "anthropic"}
    ),
    "disease-detector": ModelInfo(
        id="disease-detector",
        name="Crop Disease Detection",
        type=ModelType.DISEASE_DETECTION,
        version="1.0.0",
        description="AI-powered crop disease detection and treatment recommendations",
        status=ModelStatus.AVAILABLE,
        capabilities=["symptom_analysis", "treatment_recommendation", "prevention_guidance"],
        input_schema=DiseaseDetectionRequest.model_json_schema(),
        output_schema=DiseaseDetectionResponse.model_json_schema(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"supported_crops": ["tomato", "potato", "corn", "apple", "grape"], "provider": "rule_based"}
    ),
    "claude-disease-expert": ModelInfo(
        id="claude-disease-expert",
        name="Claude Disease Expert",
        type=ModelType.DISEASE_DETECTION,
        version="1.0.0",
        description="Claude AI expert system for plant disease diagnosis with comprehensive analysis",
        status=ModelStatus.AVAILABLE,
        capabilities=["advanced_diagnosis", "treatment_planning", "preventive_strategies", "expert_knowledge"],
        input_schema=DiseaseDetectionRequest.model_json_schema(),
        output_schema=DiseaseDetectionResponse.model_json_schema(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"supported_crops": ["all_crops"], "provider": "anthropic"}
    ),
    "plant-disease-cnn": ModelInfo(
        id="plant-disease-cnn",
        name="Plant Disease CNN Classifier",
        type=ModelType.PLANT_DISEASE,
        version="1.0.0",
        description="Deep learning model for plant disease classification from images",
        status=ModelStatus.AVAILABLE,
        capabilities=["image_classification", "disease_identification", "confidence_scoring"],
        input_schema={"image": "base64_string"},
        output_schema={"disease": "string", "confidence": "float"},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"input_format": "image", "classes": 38, "provider": "tensorflow"}
    )
}
