#!/usr/bin/env python3
"""
Web-only version of BhoomiSetu to test chat formatting without Telegram conflicts
"""

import uvicorn
from src.web.main import app

if __name__ == "__main__":
    print("🌾 Starting BhoomiSetu Web Interface (Chat Formatting Test)...")
    print("🔗 Web interface: http://localhost:8000")
    print("📝 Testing the new HTML formatting for chat responses")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
