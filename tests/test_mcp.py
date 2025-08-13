"""
Test suite for BhoomiSetu MCP Server
"""

import pytest
import asyncio
import json
from typing import Dict, Any
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.mcp.server import app
from src.mcp.client import BhoomiSetuMCPClient
from src.mcp.models import (
    ChatRequest, CropRecommendationRequest, DiseaseDetectionRequest,
    Coordinates, ModelStatus, HealthStatus
)

# Test client
client = TestClient(app)

class TestMCPServer:
    """Test MCP server endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "BhoomiSetu MCP Server"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime" in data
        assert "models_status" in data
    
    def test_metadata_endpoint(self):
        """Test metadata endpoint"""
        response = client.get("/v1/metadata")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "BhoomiSetu MCP Server"
        assert "supported_languages" in data
        assert "available_models" in data
        assert "capabilities" in data
    
    def test_models_list_endpoint(self):
        """Test models list endpoint"""
        response = client.get("/v1/models")
        assert response.status_code == 200
        models = response.json()
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Check first model structure
        model = models[0]
        assert "id" in model
        assert "name" in model
        assert "type" in model
        assert "status" in model
    
    def test_model_info_endpoint(self):
        """Test individual model info endpoint"""
        # Test valid model
        response = client.get("/v1/models/bhoomi-chat")
        assert response.status_code == 200
        model = response.json()
        assert model["id"] == "bhoomi-chat"
        assert model["type"] == "chat"
        
        # Test invalid model
        response = client.get("/v1/models/nonexistent")
        assert response.status_code == 404
    
    @patch('src.mcp.server.agri_agent')
    def test_chat_endpoint(self, mock_agent):
        """Test chat endpoint"""
        # Mock agent response
        mock_agent.process_query.return_value = {
            "response": "Test response",
            "language": "en",
            "query_type": "general",
            "confidence": 0.9
        }
        
        chat_request = {
            "message": "Hello, how to grow rice?",
            "language": "en",
            "location": "Punjab"
        }
        
        response = client.post("/v1/chat", json=chat_request)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "language" in data
        assert "timestamp" in data
    
    def test_chat_endpoint_validation(self):
        """Test chat endpoint input validation"""
        # Empty message
        response = client.post("/v1/chat", json={"message": ""})
        assert response.status_code == 422
        
        # Missing message
        response = client.post("/v1/chat", json={"language": "en"})
        assert response.status_code == 422
    
    @patch('src.mcp.server.crop_recommender')
    def test_crop_recommendation_endpoint(self, mock_recommender):
        """Test crop recommendation endpoint"""
        # Mock recommender response
        mock_recommender.get_recommendations.return_value = {
            "crops": [{"name": "rice", "confidence": 0.9}],
            "reasons": ["Suitable climate"],
            "season_advice": "Good time to plant"
        }
        
        request_data = {
            "soil_type": "clay",
            "season": "kharif",
            "location": "Punjab"
        }
        
        response = client.post("/v1/models/crop-recommender/recommend", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "recommended_crops" in data
        assert "reasons" in data
    
    @patch('src.mcp.server.disease_service')
    def test_disease_detection_endpoint(self, mock_service):
        """Test disease detection endpoint"""
        # Mock service response
        mock_service.detect_diseases.return_value = {
            "diseases": [{"name": "leaf_blight", "confidence": 0.8}],
            "treatments": ["Apply fungicide"],
            "prevention": ["Proper drainage"]
        }
        
        request_data = {
            "crop_type": "tomato",
            "symptoms": ["yellow leaves", "brown spots"]
        }
        
        response = client.post("/v1/models/disease-detector/detect", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "detected_diseases" in data
        assert "treatment_recommendations" in data

class TestMCPClient:
    """Test MCP client functionality"""
    
    @pytest.fixture
    def mock_server_response(self):
        """Mock server responses"""
        return {
            "health": {
                "status": "healthy",
                "version": "1.0.0",
                "uptime": 100.0,
                "models_status": {"bhoomi-chat": "available"}
            },
            "metadata": {
                "name": "BhoomiSetu MCP Server",
                "version": "1.0.0",
                "supported_languages": ["en", "hi"],
                "available_models": ["bhoomi-chat"]
            },
            "chat": {
                "message": "Test response",
                "language": "en",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    
    @pytest.mark.asyncio
    async def test_client_health_check(self, mock_server_response):
        """Test client health check"""
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = Mock(return_value=mock_server_response["health"])
            mock_request.return_value.__aenter__.return_value = mock_response
            
            async with BhoomiSetuMCPClient("http://localhost:8001") as client:
                health = await client.get_health()
                assert health.status == "healthy"
                assert health.version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_client_chat(self, mock_server_response):
        """Test client chat functionality"""
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = Mock(return_value=mock_server_response["chat"])
            mock_request.return_value.__aenter__.return_value = mock_response
            
            async with BhoomiSetuMCPClient("http://localhost:8001") as client:
                response = await client.chat("Test message")
                assert response.message == "Test response"
                assert response.language == "en"
    
    @pytest.mark.asyncio
    async def test_client_error_handling(self):
        """Test client error handling"""
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = Mock()
            mock_response.status = 500
            mock_response.text = Mock(return_value="Internal Server Error")
            mock_request.return_value.__aenter__.return_value = mock_response
            
            async with BhoomiSetuMCPClient("http://localhost:8001") as client:
                with pytest.raises(Exception):
                    await client.get_health()

class TestMCPModels:
    """Test MCP data models"""
    
    def test_chat_request_validation(self):
        """Test ChatRequest validation"""
        # Valid request
        request = ChatRequest(message="Hello")
        assert request.message == "Hello"
        assert request.language == "en"  # default
        
        # Invalid request (empty message)
        with pytest.raises(ValueError):
            ChatRequest(message="")
    
    def test_coordinates_validation(self):
        """Test Coordinates validation"""
        # Valid coordinates
        coords = Coordinates(latitude=28.6139, longitude=77.2090)
        assert coords.latitude == 28.6139
        assert coords.longitude == 77.2090
        
        # Invalid coordinates
        with pytest.raises(ValueError):
            Coordinates(latitude=100, longitude=77.2090)  # Invalid latitude
        
        with pytest.raises(ValueError):
            Coordinates(latitude=28.6139, longitude=200)  # Invalid longitude
    
    def test_crop_recommendation_request(self):
        """Test CropRecommendationRequest"""
        request = CropRecommendationRequest(
            soil_type="clay",
            season="kharif",
            farm_size=5.0
        )
        assert request.soil_type == "clay"
        assert request.season == "kharif"
        assert request.farm_size == 5.0
    
    def test_disease_detection_request(self):
        """Test DiseaseDetectionRequest"""
        request = DiseaseDetectionRequest(
            crop_type="tomato",
            symptoms=["yellow leaves", "spots"]
        )
        assert request.crop_type == "tomato"
        assert len(request.symptoms) == 2

class TestMCPIntegration:
    """Integration tests for MCP components"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_chat_flow(self):
        """Test complete chat flow"""
        # This would require actual server running
        # For now, we'll test with mocked responses
        pass
    
    @pytest.mark.asyncio
    async def test_model_registry_consistency(self):
        """Test that model registry is consistent"""
        from src.mcp.models import MODEL_REGISTRY
        
        # Check that all models have required fields
        for model_id, model_info in MODEL_REGISTRY.items():
            assert model_info.id == model_id
            assert model_info.name
            assert model_info.type
            assert model_info.version
            assert model_info.status
    
    def test_api_versioning(self):
        """Test API versioning consistency"""
        # All endpoints should be under /v1/
        response = client.get("/v1/health")
        assert response.status_code == 200
        
        response = client.get("/v1/metadata")
        assert response.status_code == 200
        
        response = client.get("/v1/models")
        assert response.status_code == 200

class TestMCPPerformance:
    """Performance tests for MCP server"""
    
    def test_health_check_performance(self):
        """Test health check response time"""
        import time
        
        start_time = time.time()
        response = client.get("/v1/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import threading
        
        def make_request():
            return client.get("/v1/health")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in results)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
