"""
Example usage of BhoomiSetu MCP Client
Demonstrates how to interact with the MCP server
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.mcp.client import BhoomiSetuMCPClient, quick_chat, quick_crop_recommendation
from src.mcp.models import Coordinates

async def main():
    """Main example function"""
    print("🌾 BhoomiSetu MCP Client Examples")
    print("=" * 50)
    
    # Server URL (adjust as needed)
    server_url = "http://localhost:8001"
    
    try:
        # Method 1: Using context manager (recommended)
        async with BhoomiSetuMCPClient(server_url) as client:
            
            # Check server health
            print("\n1. Checking server health...")
            try:
                health = await client.get_health()
                print(f"   Status: {health.status}")
                print(f"   Uptime: {health.uptime:.2f} seconds")
                print(f"   Available models: {len(health.models_status)}")
            except Exception as e:
                print(f"   ❌ Server not available: {e}")
                return
            
            # Get server metadata
            print("\n2. Getting server metadata...")
            metadata = await client.get_metadata()
            print(f"   Name: {metadata.name}")
            print(f"   Version: {metadata.version}")
            print(f"   Supported languages: {', '.join(metadata.supported_languages[:5])}...")
            
            # List available models
            print("\n3. Listing available models...")
            models = await client.list_models()
            for model in models:
                print(f"   📋 {model.name} ({model.id}) - {model.status}")
            
            # Chat example
            print("\n4. Chat example...")
            response = await client.chat(
                message="What crops should I plant in Punjab during Rabi season?",
                language="en",
                location="Punjab, India"
            )
            print(f"   🤖 AI: {response.message[:200]}...")
            
            # Crop recommendation example
            print("\n5. Crop recommendation example...")
            crop_response = await client.recommend_crops(
                soil_type="clay",
                climate_zone="tropical",
                season="kharif",
                farm_size=5.0,
                location="Maharashtra, India",
                coordinates=Coordinates(latitude=19.7515, longitude=75.7139)
            )
            print(f"   🌱 Recommended crops: {len(crop_response.recommended_crops)}")
            if crop_response.recommended_crops:
                print(f"   Top recommendation: {crop_response.recommended_crops[0]}")
            
            # Disease detection example
            print("\n6. Disease detection example...")
            disease_response = await client.detect_disease(
                crop_type="tomato",
                symptoms=["yellow leaves", "brown spots", "wilting"],
                location="Karnataka, India"
            )
            print(f"   🦠 Detected diseases: {len(disease_response.detected_diseases)}")
            if disease_response.treatment_recommendations:
                print(f"   💊 First treatment: {disease_response.treatment_recommendations[0]}")
            
            # Model-specific prediction
            print("\n7. Direct model prediction...")
            prediction = await client.predict(
                model_id="bhoomi-chat",
                input_data={
                    "message": "How to increase wheat yield?",
                    "context": {"location": "Haryana"}
                },
                parameters={"language": "en"}
            )
            print(f"   🎯 Prediction type: {type(prediction.prediction)}")
        
        # Method 2: Using utility functions (for simple tasks)
        print("\n8. Using utility functions...")
        
        simple_response = await quick_chat(
            "What is the best time to plant rice?",
            server_url
        )
        print(f"   ⚡ Quick chat: {simple_response[:100]}...")
        
        quick_crops = await quick_crop_recommendation(
            "I have 10 acres of land with good irrigation in Tamil Nadu",
            "Tamil Nadu, India",
            server_url
        )
        print(f"   ⚡ Quick crops: {len(quick_crops)} recommendations")
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the MCP server is running on the specified URL")

async def health_check_example():
    """Simple health check example"""
    server_url = "http://localhost:8001"
    
    async with BhoomiSetuMCPClient(server_url) as client:
        is_healthy = await client.is_server_healthy()
        print(f"Server healthy: {is_healthy}")

async def multilingual_chat_example():
    """Example of multilingual chat"""
    server_url = "http://localhost:8001"
    
    languages = ["en", "hi", "te"]
    questions = [
        "How to prepare soil for wheat cultivation?",
        "गेहूं की खेती के लिए मिट्टी कैसे तैयार करें?",
        "గోధుమ సాగుకు మట్టిని ఎలా సిద్ధం చేయాలి?"
    ]
    
    async with BhoomiSetuMCPClient(server_url) as client:
        for lang, question in zip(languages, questions):
            response = await client.chat(
                message=question,
                language=lang,
                location="India"
            )
            print(f"{lang.upper()}: {response.message[:150]}...")

if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Full examples (main)")
    print("2. Health check only")
    print("3. Multilingual chat")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        asyncio.run(health_check_example())
    elif choice == "3":
        asyncio.run(multilingual_chat_example())
    else:
        print("Invalid choice")
        asyncio.run(main())
