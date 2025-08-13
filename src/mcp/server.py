"""
Model Context Protocol (MCP) Server for BhoomiSetu Agricultural AI
Provides standardized API endpoints for agricultural AI models and services
"""

import os
import sys
import json
import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.mcp.models import (
    ModelInfo, ModelType, ModelStatus, HealthStatus,
    ChatRequest, ChatResponse, PredictionRequest, PredictionResponse,
    CropRecommendationRequest, CropRecommendationResponse,
    DiseaseDetectionRequest, DiseaseDetectionResponse,
    HealthResponse, ServerMetadata, ErrorResponse,
    MODEL_REGISTRY
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server state
SERVER_START_TIME = time.time()
SERVER_VERSION = "1.0.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting BhoomiSetu MCP Server...")
    
    # Initialize services
    try:
        await initialize_services()
        logger.info("✅ Services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
    
    yield
    
    # Cleanup
    logger.info("🔽 Shutting down BhoomiSetu MCP Server...")

# Create FastAPI app
app = FastAPI(
    title="BhoomiSetu MCP Server",
    description="Model Context Protocol server for BhoomiSetu Agricultural AI",
    version=SERVER_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services (will be initialized in lifespan)
agri_agent = None
crop_recommender = None
disease_service = None
plant_disease_service = None
claude_service = None

async def initialize_services():
    """Initialize all AI services"""
    global agri_agent, crop_recommender, disease_service, plant_disease_service, claude_service
    
    try:
        # Import and initialize services
        from src.agents.agri_agent import agri_agent as agent
        from src.agents.crop_recommender import crop_recommender as crop_rec
        from src.services.crop_disease_service import crop_disease_service
        from src.services.plant_disease_service import plant_disease_service as plant_svc
        
        # Initialize Claude service
        try:
            from src.services.claude_service import claude_service as claude_svc
            claude_service = claude_svc
            logger.info("✅ Claude service initialized")
        except ImportError as e:
            logger.warning(f"⚠️ Claude service not available: {e}")
            claude_service = None
        
        agri_agent = agent
        crop_recommender = crop_rec
        disease_service = crop_disease_service
        plant_disease_service = plant_svc
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise

def get_uptime() -> float:
    """Get server uptime in seconds"""
    return time.time() - SERVER_START_TIME

def check_service_health() -> Dict[str, bool]:
    """Check health of all dependencies"""
    health = {
        "agri_agent": agri_agent is not None,
        "crop_recommender": crop_recommender is not None,
        "disease_service": disease_service is not None,
        "plant_disease_service": plant_disease_service is not None,
        "claude_service": claude_service is not None and claude_service.is_available(),
        "openai_api": os.getenv('OPENAI_API_KEY') is not None,
        "groq_api": os.getenv('GROQ_API_KEY') is not None,
        "anthropic_api": os.getenv('ANTHROPIC_API_KEY') is not None,
        "weather_api": os.getenv('OPENWEATHER_API_KEY') is not None,
        "data_gov_api": os.getenv('DATA_GOV_API_KEY') is not None
    }
    return health

def determine_health_status(dependencies: Dict[str, bool]) -> HealthStatus:
    """Determine overall health status"""
    critical_services = ["agri_agent", "crop_recommender"]
    
    # Check if critical services are healthy
    critical_healthy = all(dependencies.get(service, False) for service in critical_services)
    
    if critical_healthy:
        # If most services are healthy, status is healthy
        total_services = len(dependencies)
        healthy_count = sum(1 for status in dependencies.values() if status)
        health_ratio = healthy_count / total_services
        
        if health_ratio >= 0.8:
            return HealthStatus.HEALTHY
        elif health_ratio >= 0.6:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNHEALTHY
    else:
        return HealthStatus.UNHEALTHY

# MCP v1 Endpoints

@app.get("/v1/health", response_model=HealthResponse)
async def get_health():
    """Get server health status"""
    try:
        dependencies = check_service_health()
        status = determine_health_status(dependencies)
        
        # Get model statuses
        models_status = {}
        for model_id in MODEL_REGISTRY.keys():
            if model_id == "bhoomi-chat" and dependencies["agri_agent"]:
                models_status[model_id] = ModelStatus.AVAILABLE
            elif model_id == "crop-recommender" and dependencies["crop_recommender"]:
                models_status[model_id] = ModelStatus.AVAILABLE
            elif model_id in ["disease-detector", "plant-disease-cnn"] and dependencies["disease_service"]:
                models_status[model_id] = ModelStatus.AVAILABLE
            else:
                models_status[model_id] = ModelStatus.ERROR
        
        return HealthResponse(
            status=status,
            version=SERVER_VERSION,
            uptime=get_uptime(),
            models_status=models_status,
            dependencies=dependencies,
            performance_metrics={
                "uptime_hours": round(get_uptime() / 3600, 2),
                "active_models": len([s for s in models_status.values() if s == ModelStatus.AVAILABLE])
            }
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/metadata", response_model=ServerMetadata)
async def get_metadata():
    """Get server metadata"""
    return ServerMetadata(
        name="BhoomiSetu MCP Server",
        version=SERVER_VERSION,
        description="Model Context Protocol server for BhoomiSetu Agricultural AI platform",
        supported_languages=["en", "hi", "te", "ta", "kn", "ml", "mr", "gu", "bn", "as"],
        available_models=list(MODEL_REGISTRY.keys()),
        capabilities=[
            "agricultural_chat",
            "crop_recommendation", 
            "disease_detection",
            "plant_disease_classification",
            "weather_integration",
            "multilingual_support",
            "market_price_analysis"
        ],
        api_version="1.0.0",
        documentation_url="/docs",
        contact={
            "name": "BhoomiSetu Team",
            "email": "support@bhoomisetu.ai",
            "url": "https://bhoomisetu.ai"
        }
    )

@app.get("/v1/models", response_model=List[ModelInfo])
async def list_models():
    """Get list of available models"""
    return list(MODEL_REGISTRY.values())

@app.get("/v1/models/{model_id}", response_model=ModelInfo)
async def get_model_info(model_id: str):
    """Get information about a specific model"""
    if model_id not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    
    return MODEL_REGISTRY[model_id]

@app.post("/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat with the agricultural AI agent"""
    try:
        # Check if Claude should be used (based on preference or availability)
        use_claude = request.context.get("use_claude", False) or not agri_agent
        
        if use_claude and claude_service and claude_service.is_available():
            # Use Claude for chat
            response = await claude_service.agricultural_query(
                query=request.message,
                context={
                    "location": request.location,
                    "coordinates": request.coordinates.model_dump() if request.coordinates else None,
                    **request.context
                },
                language=request.language
            )
            
            return ChatResponse(
                message=response.get("response", ""),
                language=response.get("language", request.language),
                query_type=response.get("query_type"),
                confidence=response.get("confidence"),
                sources=response.get("sources", []),
                suggestions=response.get("suggestions", []),
                metadata={
                    **response.get("metadata", {}),
                    "ai_provider": "claude"
                }
            )
        
        elif agri_agent:
            # Use existing agent
            user_context = {
                "location": request.location,
                "coordinates": request.coordinates.model_dump() if request.coordinates else None,
                "conversation_history": request.conversation_history or [],
                **request.context
            }
            
            response = await agri_agent.process_query(
                query=request.message,
                context=user_context,
                language=request.language
            )
            
            return ChatResponse(
                message=response.get("response", ""),
                language=response.get("language", request.language),
                query_type=response.get("query_type"),
                confidence=response.get("confidence"),
                sources=response.get("sources", []),
                suggestions=response.get("suggestions", []),
                metadata={
                    **response.get("metadata", {}),
                    "ai_provider": "openai"
                }
            )
        else:
            raise HTTPException(status_code=503, detail="No chat service available")
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/models/{model_id}/predict", response_model=PredictionResponse)
async def model_predict(model_id: str, request: PredictionRequest):
    """Make a prediction using a specific model"""
    try:
        if model_id not in MODEL_REGISTRY:
            raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
        
        model_info = MODEL_REGISTRY[model_id]
        
        # Route to appropriate service based on model type
        if model_info.type == ModelType.CHAT:
            return await _handle_chat_prediction(request)
        elif model_info.type == ModelType.CROP_RECOMMENDATION:
            return await _handle_crop_prediction(request)
        elif model_info.type == ModelType.DISEASE_DETECTION:
            return await _handle_disease_prediction(request)
        elif model_info.type == ModelType.PLANT_DISEASE:
            return await _handle_plant_disease_prediction(request)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported model type: {model_info.type}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error for model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/models/crop-recommender/recommend", response_model=CropRecommendationResponse)
async def recommend_crops(request: CropRecommendationRequest):
    """Get crop recommendations"""
    try:
        if not crop_recommender:
            raise HTTPException(status_code=503, detail="Crop recommendation service unavailable")
        
        # Prepare input for crop recommender
        farm_context = {
            "soil_type": request.soil_type,
            "climate_zone": request.climate_zone,
            "season": request.season,
            "farm_size": request.farm_size,
            "irrigation_type": request.irrigation_type,
            "location": request.location,
            "coordinates": request.coordinates.model_dump() if request.coordinates else None,
            "budget": request.budget,
            "experience_level": request.experience_level
        }
        
        # Get recommendations
        result = await crop_recommender.get_recommendations(farm_context)
        
        return CropRecommendationResponse(
            recommended_crops=result.get("crops", []),
            reasons=result.get("reasons", []),
            season_advice=result.get("season_advice"),
            estimated_yield=result.get("estimated_yield"),
            investment_required=result.get("investment_required"),
            risk_factors=result.get("risk_factors", []),
            success_tips=result.get("success_tips", [])
        )
        
    except Exception as e:
        logger.error(f"Crop recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/models/disease-detector/detect", response_model=DiseaseDetectionResponse)
async def detect_disease(request: DiseaseDetectionRequest):
    """Detect crop diseases based on symptoms"""
    try:
        if not disease_service:
            raise HTTPException(status_code=503, detail="Disease detection service unavailable")
        
        # Prepare input for disease detection
        detection_input = {
            "crop_type": request.crop_type,
            "symptoms": request.symptoms,
            "location": request.location,
            "weather_conditions": request.weather_conditions,
            "image_data": request.image_data
        }
        
        # Get disease detection results
        result = await disease_service.detect_diseases(detection_input)
        
        return DiseaseDetectionResponse(
            detected_diseases=result.get("diseases", []),
            confidence_scores=result.get("confidence_scores", {}),
            treatment_recommendations=result.get("treatments", []),
            prevention_tips=result.get("prevention", []),
            severity_level=result.get("severity"),
            immediate_actions=result.get("immediate_actions", [])
        )
        
    except Exception as e:
        logger.error(f"Disease detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/models/plant-disease-cnn/classify")
async def classify_plant_disease(file: UploadFile = File(...)):
    """Classify plant disease from uploaded image"""
    try:
        if not plant_disease_service:
            raise HTTPException(status_code=503, detail="Plant disease classification service unavailable")
        
        # Read and process image
        image_data = await file.read()
        
        # Get classification result
        result = await plant_disease_service.predict_disease(image_data)
        
        return PredictionResponse(
            model_id="plant-disease-cnn",
            prediction={
                "disease": result.get("predicted_class"),
                "confidence": result.get("confidence"),
                "all_predictions": result.get("all_predictions", [])
            },
            confidence=result.get("confidence"),
            metadata={
                "image_size": len(image_data),
                "filename": file.filename,
                "content_type": file.content_type
            }
        )
        
    except Exception as e:
        logger.error(f"Plant disease classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/claude/chat", response_model=ChatResponse)
async def claude_chat_endpoint(request: ChatRequest):
    """Chat specifically with Claude AI"""
    try:
        if not claude_service or not claude_service.is_available():
            raise HTTPException(status_code=503, detail="Claude AI service unavailable")
        
        response = await claude_service.agricultural_query(
            query=request.message,
            context={
                "location": request.location,
                "coordinates": request.coordinates.model_dump() if request.coordinates else None,
                **request.context
            },
            language=request.language
        )
        
        return ChatResponse(
            message=response.get("response", ""),
            language=response.get("language", request.language),
            query_type=response.get("query_type"),
            confidence=response.get("confidence"),
            sources=response.get("sources", []),
            suggestions=response.get("suggestions", []),
            metadata={
                **response.get("metadata", {}),
                "ai_provider": "claude"
            }
        )
        
    except Exception as e:
        logger.error(f"Claude chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/claude/crop-recommendation")
async def claude_crop_recommendation(request: CropRecommendationRequest):
    """Get crop recommendations using Claude AI"""
    try:
        if not claude_service or not claude_service.is_available():
            raise HTTPException(status_code=503, detail="Claude AI service unavailable")
        
        farm_context = {
            "soil_type": request.soil_type,
            "climate_zone": request.climate_zone,
            "season": request.season,
            "farm_size": request.farm_size,
            "irrigation_type": request.irrigation_type,
            "location": request.location,
            "coordinates": request.coordinates.model_dump() if request.coordinates else None,
            "budget": request.budget,
            "experience_level": request.experience_level
        }
        
        result = await claude_service.crop_recommendation(farm_context)
        
        return {
            "recommendations": result.get("recommendations"),
            "farm_context": result.get("farm_context"),
            "metadata": {
                **result.get("metadata", {}),
                "ai_provider": "claude"
            }
        }
        
    except Exception as e:
        logger.error(f"Claude crop recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/claude/disease-diagnosis")
async def claude_disease_diagnosis(request: DiseaseDetectionRequest):
    """Diagnose diseases using Claude AI"""
    try:
        if not claude_service or not claude_service.is_available():
            raise HTTPException(status_code=503, detail="Claude AI service unavailable")
        
        context = {
            "location": request.location,
            "weather_conditions": request.weather_conditions
        }
        
        result = await claude_service.disease_diagnosis(
            symptoms=request.symptoms,
            crop_type=request.crop_type,
            context=context
        )
        
        return {
            "diagnosis": result.get("diagnosis"),
            "crop_type": result.get("crop_type"),
            "symptoms": result.get("symptoms"),
            "metadata": {
                **result.get("metadata", {}),
                "ai_provider": "claude"
            }
        }
        
    except Exception as e:
        logger.error(f"Claude disease diagnosis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for model prediction routing
async def _handle_chat_prediction(request: PredictionRequest) -> PredictionResponse:
    """Handle chat model predictions"""
    if not agri_agent:
        raise HTTPException(status_code=503, detail="Chat service unavailable")
    
    message = request.input_data.get("message", "")
    context = request.input_data.get("context", {})
    language = request.parameters.get("language", "en")
    
    response = await agri_agent.process_query(message, context, language)
    
    return PredictionResponse(
        model_id="bhoomi-chat",
        prediction=response,
        confidence=response.get("confidence"),
        metadata={"language": language}
    )

async def _handle_crop_prediction(request: PredictionRequest) -> PredictionResponse:
    """Handle crop recommendation predictions"""
    if not crop_recommender:
        raise HTTPException(status_code=503, detail="Crop recommendation service unavailable")
    
    result = await crop_recommender.get_recommendations(request.input_data)
    
    return PredictionResponse(
        model_id="crop-recommender",
        prediction=result,
        metadata={"farm_context": request.input_data}
    )

async def _handle_disease_prediction(request: PredictionRequest) -> PredictionResponse:
    """Handle disease detection predictions"""
    if not disease_service:
        raise HTTPException(status_code=503, detail="Disease detection service unavailable")
    
    result = await disease_service.detect_diseases(request.input_data)
    
    return PredictionResponse(
        model_id="disease-detector",
        prediction=result,
        metadata={"input_symptoms": request.input_data.get("symptoms", [])}
    )

async def _handle_plant_disease_prediction(request: PredictionRequest) -> PredictionResponse:
    """Handle plant disease CNN predictions"""
    if not plant_disease_service:
        raise HTTPException(status_code=503, detail="Plant disease classification service unavailable")
    
    image_data = request.input_data.get("image_data")
    if not image_data:
        raise HTTPException(status_code=400, detail="Image data required")
    
    # Decode base64 image if needed
    import base64
    if isinstance(image_data, str):
        image_data = base64.b64decode(image_data)
    
    result = await plant_disease_service.predict_disease(image_data)
    
    return PredictionResponse(
        model_id="plant-disease-cnn",
        prediction=result,
        confidence=result.get("confidence"),
        metadata={"image_processed": True}
    )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPException",
            message=exc.detail,
            details={"status_code": exc.status_code}
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details={"exception_type": type(exc).__name__}
        ).model_dump()
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "BhoomiSetu MCP Server",
        "version": SERVER_VERSION,
        "description": "Model Context Protocol server for BhoomiSetu Agricultural AI",
        "endpoints": {
            "health": "/v1/health",
            "metadata": "/v1/metadata", 
            "models": "/v1/models",
            "chat": "/v1/chat",
            "predict": "/v1/models/{model_id}/predict",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.mcp.server:app",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", 8001)),
        reload=os.getenv("MCP_RELOAD", "true").lower() == "true"
    )
