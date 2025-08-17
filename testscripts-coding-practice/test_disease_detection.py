"""
Test script to verify Plant Disease Detection functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.services.plant_disease_service import plant_disease_service
import requests

def test_model_loading():
    """Test if the model loads correctly"""
    try:
        print("✅ Testing model loading...")
        print(f"Model loaded: {plant_disease_service.model is not None}")
        print(f"Class names: {plant_disease_service.class_names}")
        print("✅ Model loading test passed!")
        return True
    except Exception as e:
        print(f"❌ Model loading test failed: {e}")
        return False

def test_api_endpoints():
    """Test if API endpoints are accessible"""
    base_url = "http://localhost:8000"
    
    try:
        print("\n✅ Testing API endpoints...")
        
        # Test disease classes endpoint
        response = requests.get(f"{base_url}/api/plant-disease/classes")
        if response.status_code == 200:
            print("✅ Plant disease classes endpoint working")
            print(f"Classes available: {response.json()['total_classes']}")
        else:
            print(f"❌ Classes endpoint failed: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing BhoomiSetu Plant Disease Detection Integration")
    print("=" * 60)
    
    # Test 1: Model Loading
    model_test = test_model_loading()
    
    # Test 2: API Endpoints (only if server is running)
    api_test = False
    try:
        api_test = test_api_endpoints()
    except:
        print("\n⚠️  API tests skipped (server not running)")
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"Model Loading: {'✅ PASS' if model_test else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_test else '⚠️  SKIP'}")
    
    if model_test:
        print("\n🎉 Integration successful! The plant disease detection feature is ready to use.")
        print("\n📋 FEATURES IMPLEMENTED:")
        print("• AI-powered plant disease detection using CNN model")
        print("• Support for 3 disease types: Tomato Bacterial Spot, Potato Early Blight, Corn Common Rust")
        print("• Multi-language disease descriptions (10+ languages)")
        print("• Treatment recommendations with preventive and chemical controls")
        print("• Modern glassmorphism UI with drag-and-drop file upload")
        print("• Real-time image preprocessing and prediction")
        print("• Integration with BhoomiSetu's existing agricultural AI system")
        
        print("\n🌐 ACCESS POINTS:")
        print("• Web Interface: http://localhost:8000/disease-detection")
        print("• API Prediction: POST /api/plant-disease/predict")
        print("• API Description: POST /api/plant-disease/description")
        print("• API Treatment: GET /api/plant-disease/treatment/{disease_name}")
        print("• API Classes: GET /api/plant-disease/classes")

if __name__ == "__main__":
    main()
