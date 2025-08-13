"""
MCP package initialization
"""

from .server import app
from .client import BhoomiSetuMCPClient, quick_chat, quick_crop_recommendation, quick_disease_diagnosis
from .models import (
    ModelInfo, ModelType, ModelStatus, HealthStatus,
    ChatRequest, ChatResponse, PredictionRequest, PredictionResponse,
    CropRecommendationRequest, CropRecommendationResponse,
    DiseaseDetectionRequest, DiseaseDetectionResponse,
    HealthResponse, ServerMetadata, Coordinates
)

__version__ = "1.0.0"
__all__ = [
    "app",
    "BhoomiSetuMCPClient",
    "quick_chat",
    "quick_crop_recommendation", 
    "quick_disease_diagnosis",
    "ModelInfo",
    "ModelType",
    "ModelStatus",
    "HealthStatus",
    "ChatRequest",
    "ChatResponse",
    "PredictionRequest",
    "PredictionResponse",
    "CropRecommendationRequest",
    "CropRecommendationResponse",
    "DiseaseDetectionRequest",
    "DiseaseDetectionResponse",
    "HealthResponse",
    "ServerMetadata",
    "Coordinates"
]
