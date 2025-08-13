# BhoomiSetu MCP Server

Model Context Protocol (MCP) server for BhoomiSetu Agricultural AI platform. This provides standardized API endpoints for agricultural AI models and services.

## Features

### 🚀 Core Endpoints

- **Health Check** (`/v1/health`) - Server and model status
- **Metadata** (`/v1/metadata`) - Server information and capabilities  
- **Models** (`/v1/models`) - List and get information about available models
- **Chat** (`/v1/chat`) - Conversational AI for agricultural queries
- **Prediction** (`/v1/models/{model_id}/predict`) - Generic model predictions

### 🌱 Agricultural Services

- **Crop Recommendations** - ML-based crop suggestions
- **Disease Detection** - Symptom-based disease identification
- **Plant Disease Classification** - Image-based disease detection
- **Weather Integration** - Weather-aware recommendations
- **Multilingual Support** - 10+ Indian languages

### 📊 Available Models

| Model ID | Type | Description |
|----------|------|-------------|
| `bhoomi-chat` | Chat | Conversational agricultural AI |
| `crop-recommender` | Prediction | Crop recommendation system |
| `disease-detector` | Detection | Disease detection from symptoms |
| `plant-disease-cnn` | Classification | CNN-based plant disease detection |

## Quick Start

### 1. Start the MCP Server

```bash
# Using the dedicated runner
python mcp_server.py

# Or with custom configuration
MCP_HOST=0.0.0.0 MCP_PORT=8001 python mcp_server.py
```

### 2. Use the Client

```python
import asyncio
from src.mcp.client import BhoomiSetuMCPClient

async def example():
    async with BhoomiSetuMCPClient("http://localhost:8001") as client:
        # Chat with agricultural AI
        response = await client.chat(
            message="What crops should I plant in Punjab?",
            language="en",
            location="Punjab, India"
        )
        print(response.message)
        
        # Get crop recommendations
        crops = await client.recommend_crops(
            soil_type="clay",
            season="kharif",
            location="Maharashtra"
        )
        print(crops.recommended_crops)

asyncio.run(example())
```

### 3. Quick Utilities

```python
from src.mcp.client import quick_chat, quick_crop_recommendation

# Simple chat
response = await quick_chat("How to increase wheat yield?")

# Quick crop advice
crops = await quick_crop_recommendation(
    "10 acres irrigated land in Tamil Nadu"
)
```

## API Documentation

### Chat Endpoint

**POST** `/v1/chat`

```json
{
  "message": "What crops should I plant?",
  "language": "en",
  "location": "Punjab, India",
  "coordinates": {
    "latitude": 30.7333,
    "longitude": 76.7794
  },
  "conversation_history": [],
  "context": {}
}
```

**Response:**
```json
{
  "message": "Based on your location in Punjab...",
  "language": "en",
  "query_type": "crop_recommendation",
  "confidence": 0.95,
  "sources": ["weather_data", "soil_analysis"],
  "suggestions": ["Consider soil testing", "Check irrigation"],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Crop Recommendation

**POST** `/v1/models/crop-recommender/recommend`

```json
{
  "soil_type": "clay",
  "climate_zone": "tropical", 
  "season": "kharif",
  "farm_size": 5.0,
  "location": "Maharashtra",
  "budget": 100000
}
```

**Response:**
```json
{
  "recommended_crops": [
    {
      "crop": "rice",
      "variety": "IR64",
      "confidence": 0.92,
      "expected_yield": "4.5 tons/acre"
    }
  ],
  "reasons": ["Suitable soil type", "Good rainfall"],
  "investment_required": {"seeds": 5000, "fertilizer": 15000}
}
```

### Disease Detection

**POST** `/v1/models/disease-detector/detect`

```json
{
  "crop_type": "tomato",
  "symptoms": ["yellow leaves", "brown spots"],
  "location": "Karnataka",
  "weather_conditions": {"humidity": 80, "temperature": 28}
}
```

### Plant Disease Classification

**POST** `/v1/models/plant-disease-cnn/classify`

Upload image file for CNN-based disease classification.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | Server host |
| `MCP_PORT` | `8001` | Server port |
| `MCP_RELOAD` | `true` | Enable auto-reload |
| `MCP_LOG_LEVEL` | `info` | Logging level |

### Required Dependencies

The MCP server requires the same dependencies as the main BhoomiSetu application:

- Agricultural AI agent
- Crop recommendation service
- Disease detection services
- Weather API integration
- Database connections

## Client Examples

### Basic Usage

```python
from src.mcp.client import BhoomiSetuMCPClient

async with BhoomiSetuMCPClient() as client:
    # Check server health
    health = await client.get_health()
    
    # List models
    models = await client.list_models()
    
    # Chat
    response = await client.chat("How to grow organic vegetables?")
```

### Advanced Usage

```python
# Crop recommendations with coordinates
from src.mcp.models import Coordinates

crops = await client.recommend_crops(
    soil_type="loamy",
    coordinates=Coordinates(latitude=28.6139, longitude=77.2090),
    farm_size=2.5,
    budget=50000
)

# Disease detection with image
with open("plant_image.jpg", "rb") as f:
    result = await client.classify_plant_disease(f.read())
```

### Error Handling

```python
from src.mcp.client import MCPClientError

try:
    async with BhoomiSetuMCPClient() as client:
        response = await client.chat("Hello")
except MCPClientError as e:
    print(f"MCP Error: {e}")
except Exception as e:
    print(f"General Error: {e}")
```

## Health Monitoring

### Health Check Response

```json
{
  "status": "healthy",
  "version": "1.0.0", 
  "uptime": 3600.5,
  "models_status": {
    "bhoomi-chat": "available",
    "crop-recommender": "available"
  },
  "dependencies": {
    "agri_agent": true,
    "openai_api": true,
    "weather_api": true
  }
}
```

### Model Status Values

- `available` - Model is ready
- `loading` - Model is initializing
- `error` - Model has errors
- `maintenance` - Model is under maintenance

## Integration

### With Main BhoomiSetu App

The MCP server can run alongside the main application:

```python
# In main.py, add MCP server startup
import threading
from src.mcp.server import app as mcp_app

def start_mcp_server():
    uvicorn.run(mcp_app, host="0.0.0.0", port=8001)

# Start MCP in separate thread
mcp_thread = threading.Thread(target=start_mcp_server)
mcp_thread.daemon = True
mcp_thread.start()
```

### With External Applications

External applications can use the MCP client or make direct HTTP requests:

```bash
# Health check
curl http://localhost:8001/v1/health

# Chat request
curl -X POST http://localhost:8001/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What crops for Punjab?", "language": "en"}'
```

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check if port 8001 is available
   - Verify environment variables
   - Ensure all dependencies are installed

2. **Models show as unavailable**
   - Check if main services are running
   - Verify API keys in environment
   - Check logs for initialization errors

3. **Client connection errors**
   - Verify server URL and port
   - Check network connectivity
   - Ensure server is running and healthy

### Logs

Server logs provide detailed information about:
- Service initialization
- Request processing
- Error details
- Performance metrics

Example log output:
```
INFO: 🚀 Starting BhoomiSetu MCP Server...
INFO: ✅ Services initialized successfully
INFO: Server started at http://0.0.0.0:8001
INFO: POST /v1/chat - 200 OK (1.23s)
```

## Development

### Adding New Models

1. Define model in `MODEL_REGISTRY` in `models.py`
2. Add prediction handler in `server.py`
3. Update client methods in `client.py`
4. Add tests and documentation

### Custom Endpoints

```python
@app.post("/v1/custom/endpoint")
async def custom_endpoint(request: CustomRequest):
    # Implementation
    return CustomResponse(...)
```

## Support

For issues and questions:
- Check the [main documentation](../README.md)
- Review server logs
- Test with example scripts
- Check health endpoint status
