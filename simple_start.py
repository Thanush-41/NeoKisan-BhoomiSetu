"""
Simplified startup script for testing BhoomiSetu without OpenAI
"""

import os
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="BhoomiSetu - Agricultural AI Advisor",
    description="AI-powered agricultural advisor for Indian farmers",
    version="1.0.0"
)

# Try to mount static files and templates
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
except Exception as e:
    print(f"Warning: Could not mount static files or templates: {e}")
    templates = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return HTMLResponse("""
        <html>
            <head><title>BhoomiSetu - Agricultural AI Advisor</title></head>
            <body style="font-family: Arial; margin: 50px; background: #f8f9fa;">
                <div style="max-width: 800px; margin: 0 auto; text-align: center;">
                    <h1 style="color: #2E8B57;">🌾 BhoomiSetu</h1>
                    <h2>AI-Powered Agricultural Advisor</h2>
                    <p style="font-size: 18px; color: #666;">Welcome to BhoomiSetu! Your AI agricultural advisor is running successfully.</p>
                    
                    <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0;">
                        <h3 style="color: #2E8B57;">🚀 System Status</h3>
                        <p>✅ Web server is running</p>
                        <p>✅ FastAPI is working</p>
                        <p>✅ Dependencies are installed</p>
                        <p>⚠️ Add OpenAI API key for full functionality</p>
                    </div>
                    
                    <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0;">
                        <h3 style="color: #2E8B57;">🔗 Quick Links</h3>
                        <a href="/api/health" style="display: inline-block; margin: 10px; padding: 10px 20px; background: #2E8B57; color: white; text-decoration: none; border-radius: 5px;">Health Check</a>
                        <a href="https://t.me/neokisan_bot" target="_blank" style="display: inline-block; margin: 10px; padding: 10px 20px; background: #0088cc; color: white; text-decoration: none; border-radius: 5px;">Telegram Bot</a>
                    </div>
                    
                    <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0;">
                        <h3 style="color: #2E8B57;">📋 Next Steps</h3>
                        <ol style="text-align: left; display: inline-block;">
                            <li>Add your OpenAI API key to the .env file</li>
                            <li>Restart the application</li>
                            <li>Test the AI features</li>
                            <li>Start chatting with the Telegram bot</li>
                        </ol>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h4 style="color: #856404;">🔑 To enable AI features:</h4>
                        <p style="color: #856404;">Edit the .env file and replace 'your_openai_api_key_here' with your actual OpenAI API key.</p>
                    </div>
                </div>
            </body>
        </html>
        """)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "BhoomiSetu Agricultural AI Advisor", 
        "version": "1.0.0",
        "features": {
            "web_interface": True,
            "telegram_bot": True,
            "weather_api": bool(os.getenv('OPENWEATHER_API_KEY')),
            "commodity_api": bool(os.getenv('DATA_GOV_API_KEY')),
            "openai_configured": bool(os.getenv('OPENAI_API_KEY')) and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here'
        }
    }

@app.get("/api/test")
async def test_apis():
    """Test API endpoints"""
    import requests
    
    results = {}
    
    # Test weather API
    try:
        weather_key = os.getenv('OPENWEATHER_API_KEY')
        if weather_key:
            url = f"http://api.openweathermap.org/data/2.5/weather?q=Mumbai&appid={weather_key}&units=metric"
            response = requests.get(url, timeout=5)
            results['weather'] = {'status': 'ok' if response.status_code == 200 else 'error', 'code': response.status_code}
        else:
            results['weather'] = {'status': 'no_key'}
    except Exception as e:
        results['weather'] = {'status': 'error', 'message': str(e)}
    
    # Test commodity API  
    try:
        data_key = os.getenv('DATA_GOV_API_KEY')
        if data_key:
            url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={data_key}&format=json&limit=1"
            response = requests.get(url, timeout=5)
            results['commodity'] = {'status': 'ok' if response.status_code == 200 else 'error', 'code': response.status_code}
        else:
            results['commodity'] = {'status': 'no_key'}
    except Exception as e:
        results['commodity'] = {'status': 'error', 'message': str(e)}
    
    return results

if __name__ == "__main__":
    print("🌾 Starting BhoomiSetu Agricultural AI Advisor...")
    print(f"🔗 Web interface: http://localhost:{os.getenv('PORT', 8000)}")
    print(f"🤖 Telegram bot: https://t.me/neokisan_bot")
    print("✨ Press Ctrl+C to stop")
    
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000))
    )
