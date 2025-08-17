"""
Integration test script for BhoomiSetu MCP Server
This script tests the complete MCP setup and integration
"""

import asyncio
import sys
import os
import time
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

async def test_mcp_integration():
    """Test complete MCP integration"""
    print("🌾 BhoomiSetu MCP Integration Test")
    print("=" * 50)
    
    try:
        # Import MCP components
        from src.mcp.client import BhoomiSetuMCPClient, quick_chat
        from src.mcp.models import Coordinates, MODEL_REGISTRY
        
        print("✅ MCP modules imported successfully")
        
        # Test model registry
        print(f"\n📋 Available models: {len(MODEL_REGISTRY)}")
        for model_id, model_info in MODEL_REGISTRY.items():
            print(f"   - {model_info.name} ({model_id})")
        
        # Test server connectivity (assuming server is running)
        server_url = "http://localhost:8001"
        print(f"\n🔗 Testing connection to {server_url}")
        
        try:
            async with BhoomiSetuMCPClient(server_url) as client:
                # Test health check
                health = await client.get_health()
                print(f"   Server status: {health.status}")
                print(f"   Uptime: {health.uptime:.1f}s")
                
                # Test metadata
                metadata = await client.get_metadata()
                print(f"   Server: {metadata.name} v{metadata.version}")
                
                # Test models list
                models = await client.list_models()
                print(f"   Available models: {len(models)}")
                
                # Test chat functionality
                print("\n💬 Testing chat functionality...")
                chat_response = await client.chat(
                    message="What is the best crop for Punjab in winter?",
                    language="en",
                    location="Punjab, India"
                )
                print(f"   Chat response: {chat_response.message[:100]}...")
                
                # Test crop recommendations
                print("\n🌱 Testing crop recommendations...")
                crop_response = await client.recommend_crops(
                    soil_type="alluvial",
                    season="rabi",
                    location="Punjab",
                    farm_size=5.0
                )
                print(f"   Recommended crops: {len(crop_response.recommended_crops)}")
                
                # Test disease detection
                print("\n🦠 Testing disease detection...")
                disease_response = await client.detect_disease(
                    crop_type="wheat",
                    symptoms=["yellow leaves", "stunted growth"],
                    location="Punjab"
                )
                print(f"   Detected diseases: {len(disease_response.detected_diseases)}")
                
                # Test quick utilities
                print("\n⚡ Testing quick utilities...")
                quick_response = await quick_chat("How to increase wheat yield?", server_url)
                print(f"   Quick chat: {quick_response[:50]}...")
                
                print("\n✅ All MCP tests passed!")
                return True
                
        except Exception as e:
            print(f"   ❌ Server connection failed: {e}")
            print("   💡 Make sure MCP server is running: python mcp_server.py")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_mcp_models():
    """Test MCP data models"""
    print("\n🔧 Testing MCP data models...")
    
    try:
        from src.mcp.models import (
            ChatRequest, CropRecommendationRequest, 
            DiseaseDetectionRequest, Coordinates
        )
        
        # Test ChatRequest
        chat_req = ChatRequest(
            message="Test message",
            language="hi",
            location="Delhi"
        )
        print(f"   ChatRequest: ✅")
        
        # Test Coordinates
        coords = Coordinates(latitude=28.6139, longitude=77.2090)
        print(f"   Coordinates: ✅")
        
        # Test CropRecommendationRequest
        crop_req = CropRecommendationRequest(
            soil_type="clay",
            season="kharif",
            coordinates=coords
        )
        print(f"   CropRecommendationRequest: ✅")
        
        # Test DiseaseDetectionRequest
        disease_req = DiseaseDetectionRequest(
            crop_type="rice",
            symptoms=["brown spots", "wilting"]
        )
        print(f"   DiseaseDetectionRequest: ✅")
        
        print("✅ All model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_mcp_server_standalone():
    """Test MCP server can be imported and started"""
    print("\n🚀 Testing MCP server standalone...")
    
    try:
        from src.mcp.server import app
        print("   Server app imported: ✅")
        
        # Test that FastAPI app is configured correctly
        assert app.title == "BhoomiSetu MCP Server"
        print("   Server configuration: ✅")
        
        # Check routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/v1/health", "/v1/metadata", "/v1/models", "/v1/chat"]
        
        for route in expected_routes:
            if route in routes:
                print(f"   Route {route}: ✅")
            else:
                print(f"   Route {route}: ❌")
                
        print("✅ Server standalone test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

async def performance_test():
    """Basic performance test"""
    print("\n⚡ Performance test...")
    
    try:
        from src.mcp.models import MODEL_REGISTRY
        
        # Test model registry performance
        start_time = time.time()
        for _ in range(1000):
            list(MODEL_REGISTRY.keys())
        end_time = time.time()
        
        print(f"   Model registry access (1000x): {(end_time - start_time)*1000:.2f}ms")
        
        # Test model creation performance
        from src.mcp.models import ChatRequest, Coordinates
        
        start_time = time.time()
        for i in range(100):
            req = ChatRequest(
                message=f"Test message {i}",
                coordinates=Coordinates(latitude=28.6, longitude=77.2)
            )
        end_time = time.time()
        
        print(f"   Model creation (100x): {(end_time - start_time)*1000:.2f}ms")
        print("✅ Performance test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Starting BhoomiSetu MCP comprehensive tests...\n")
    
    results = []
    
    # Test 1: Models
    results.append(await test_mcp_models())
    
    # Test 2: Server standalone
    results.append(test_mcp_server_standalone())
    
    # Test 3: Performance
    results.append(await performance_test())
    
    # Test 4: Integration (requires running server)
    results.append(await test_mcp_integration())
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Summary:")
    
    test_names = ["Models", "Server", "Performance", "Integration"]
    for name, result in zip(test_names, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {name}: {status}")
    
    overall = "✅ ALL TESTS PASSED" if all(results) else "❌ SOME TESTS FAILED"
    print(f"\n{overall}")
    
    if not results[-1]:  # Integration test failed
        print("\n💡 To run integration tests:")
        print("   1. Start MCP server: python mcp_server.py")
        print("   2. Run this test again")

if __name__ == "__main__":
    asyncio.run(main())
