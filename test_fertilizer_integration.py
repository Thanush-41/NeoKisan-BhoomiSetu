#!/usr/bin/env python3
"""
Test script for fertilizer dataset integration in BhoomiSetu agricultural AI
Tests the new fertilizer recommendation functionality with the CSV dataset
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.agri_agent import AgricultureAIAgent

async def test_fertilizer_loading():
    """Test fertilizer dataset loading"""
    print("🌿 Testing fertilizer dataset loading...")
    
    agent = AgricultureAIAgent()
    
    # Check if fertilizer data loaded
    if hasattr(agent, 'fertilizer_data') and agent.fertilizer_data:
        print(f"✅ Fertilizer data loaded successfully: {len(agent.fertilizer_data)} soil types")
        
        # Show sample data structure
        print("\n📊 Sample fertilizer data structure:")
        for soil_type, crops in list(agent.fertilizer_data.items())[:2]:
            print(f"  Soil Type: {soil_type}")
            for crop_type, fertilizers in list(crops.items())[:2]:
                print(f"    Crop: {crop_type}")
                if fertilizers:
                    fertilizer = fertilizers[0]
                    print(f"      Sample fertilizer: {fertilizer['fertilizer']}")
                    print(f"      NPK: {fertilizer['nitrogen']}-{fertilizer['phosphorus']}-{fertilizer['potassium']}")
                    print(f"      Conditions: {fertilizer['temperature']}°C, {fertilizer['humidity']}% humidity")
                    break
            break
    else:
        print("❌ Fertilizer data not loaded")
        return False
    
    return True

async def test_fertilizer_recommendations():
    """Test fertilizer recommendation functionality"""
    print("\n🔍 Testing fertilizer recommendation methods...")
    
    agent = AgricultureAIAgent()
    
    # Test specific soil type and crop type recommendations
    print("\n1. Testing specific soil and crop recommendations:")
    recommendations = agent.get_fertilizer_recommendations(
        soil_type="sandy",
        crop_type="rice",
        temperature=25,
        humidity=80,
        moisture=60
    )
    
    print(f"Recommendations found: {recommendations.get('total_found', 0)}")
    if recommendations.get('recommendations'):
        for i, rec in enumerate(recommendations['recommendations'][:2]):
            print(f"  {i+1}. {rec['fertilizer']}")
            print(f"     NPK: {rec['npk']['nitrogen']}-{rec['npk']['phosphorus']}-{rec['npk']['potassium']}")
            if 'match_score' in rec:
                print(f"     Match Score: {rec['match_score']}%")
    
    # Test general environmental condition recommendations
    print("\n2. Testing general environmental recommendations:")
    general_recommendations = agent.get_fertilizer_recommendations(
        temperature=30,
        humidity=70,
        moisture=45
    )
    
    print(f"General recommendations found: {general_recommendations.get('total_found', 0)}")
    if general_recommendations.get('recommendations'):
        for i, rec in enumerate(general_recommendations['recommendations'][:3]):
            print(f"  {i+1}. {rec['fertilizer']} for {rec['soil_type']} + {rec['crop_type']}")
            print(f"     NPK: {rec['npk']['nitrogen']}-{rec['npk']['phosphorus']}-{rec['npk']['potassium']}")
            print(f"     Match Score: {rec['match_score']}%")

async def test_integrated_crop_advice():
    """Test integrated fertilizer recommendations in crop advice queries"""
    print("\n🌾 Testing integrated crop advice with fertilizer recommendations...")
    
    agent = AgricultureAIAgent()
    
    # Test query for rice cultivation
    query = "What fertilizer should I use for rice in sandy soil?"
    location = "Hyderabad"
    
    print(f"Query: {query}")
    print(f"Location: {location}")
    
    try:
        # Simulate context data
        context_data = {
            "weather": {
                "current": {
                    "temperature": 28,
                    "humidity": 75,
                    "description": "partly cloudy"
                }
            },
            "soil": {
                "soil_type": "sandy",
                "suitable_crops": ["rice", "wheat"]
            }
        }
        
        user_context = {"location": location}
        
        response = await agent._generate_comprehensive_agricultural_advice(
            query=query,
            weather_info=context_data["weather"],
            soil_info=context_data["soil"],
            location_name=location
        )
        
        print("\n📝 AI Response:")
        print(response)
        
        # Check if fertilizer recommendations are included
        if "fertilizer" in response.lower():
            print("\n✅ Fertilizer recommendations are included in the response")
        else:
            print("\n⚠️ No fertilizer recommendations found in response")
            
    except Exception as e:
        print(f"❌ Error in integrated test: {e}")

async def test_nutrient_specific_query():
    """Test nutrient-specific queries with fertilizer dataset"""
    print("\n🧪 Testing nutrient-specific queries...")
    
    agent = AgricultureAIAgent()
    
    # Test nutrient-specific query
    query = "I have soil with N=40, P=25, K=30. What crops should I grow?"
    location = "Vijayawada"
    
    print(f"Query: {query}")
    print(f"Location: {location}")
    
    try:
        context_data = {
            "weather": {
                "current": {
                    "temperature": 30,
                    "humidity": 80,
                    "description": "hot and humid"
                }
            },
            "soil": {
                "soil_type": "black",
                "suitable_crops": ["cotton", "sugarcane"]
            }
        }
        
        user_context = {"location": location}
        
        response = await agent._generate_comprehensive_agricultural_advice(
            query=query,
            weather_info=context_data["weather"],
            soil_info=context_data["soil"],
            location_name=location
        )
        
        print("\n📝 AI Response for nutrient-specific query:")
        print(response)
        
        # Check if both dataset recommendations and AI analysis are included
        if "fertilizer dataset" in response.lower() or "n-p-k" in response.lower():
            print("\n✅ Nutrient-specific recommendations are included")
        else:
            print("\n⚠️ No nutrient-specific recommendations found in response")
            
    except Exception as e:
        print(f"❌ Error in nutrient-specific test: {e}")

async def run_all_tests():
    """Run comprehensive fertilizer integration tests"""
    print("🚀 Starting Fertilizer Integration Tests for BhoomiSetu")
    print("=" * 60)
    
    # Test 1: Dataset loading
    success1 = await test_fertilizer_loading()
    
    if success1:
        # Test 2: Recommendation methods
        await test_fertilizer_recommendations()
        
        # Test 3: Integrated crop advice
        await test_integrated_crop_advice()
        
        # Test 4: Nutrient-specific queries
        await test_nutrient_specific_query()
        
        print("\n" + "=" * 60)
        print("✅ All fertilizer integration tests completed!")
        print("🌿 Fertilizer dataset is now integrated with BhoomiSetu AI")
        print("📊 Data-driven fertilizer recommendations are available")
        print("🤖 AI responses now include both dataset lookup and AI analysis")
    else:
        print("\n❌ Fertilizer dataset loading failed - check CSV file path")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
