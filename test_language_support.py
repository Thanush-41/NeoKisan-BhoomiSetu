"""
Demo script to test the multi-language chat functionality
"""

import requests
import time

def test_language_chat():
    """Test chat in different languages"""
    
    # Test URLs
    base_url = "http://localhost:8000"
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(base_url, timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except:
            pass
        time.sleep(1)
        if i == max_retries - 1:
            print("❌ Server not ready, continuing anyway...")
    
    # Test different languages
    languages = ['en', 'hi', 'te', 'gu', 'pa']
    
    for lang in languages:
        print(f"\n🌐 Testing language: {lang}")
        
        # Test chat endpoint
        chat_data = {
            'message': 'Tell me about tomato farming',
            'location': 'Mumbai',
            'language': lang
        }
        
        try:
            response = requests.post(f"{base_url}/chat", data=chat_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response length: {len(result.get('response', ''))} characters")
                print(f"📝 Sample: {result.get('response', '')[:100]}...")
            else:
                print(f"❌ Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting BhoomiSetu Language Support Test")
    test_language_chat()
