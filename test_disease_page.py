#!/usr/bin/env python3
"""
Test script to verify disease detection page functionality
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import Request
import uvicorn

app = FastAPI(title="BhoomiSetu Disease Detection Test")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/disease-detection", response_class=HTMLResponse)
async def disease_detection_page(request: Request):
    """Disease detection page with Streamlit integration"""
    return templates.TemplateResponse("disease_detection.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Redirect to disease detection page"""
    return templates.TemplateResponse("disease_detection.html", {"request": request})

if __name__ == "__main__":
    print("🌱 Starting BhoomiSetu Disease Detection Test Server...")
    print("📱 Access the page at: http://localhost:8001")
    print("🔗 Click 'Use Advanced Detection Tool' to test Streamlit integration")
    print("📖 Review the comprehensive documentation section")
    print("\n" + "="*60)
    
    uvicorn.run(
        "test_disease_page:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
