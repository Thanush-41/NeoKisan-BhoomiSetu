"""
Standalone MCP Server Runner for BhoomiSetu
Run this file to start the MCP server independently
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root)

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Configuration
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", 8001))
    reload = os.getenv("MCP_RELOAD", "true").lower() == "true"
    log_level = os.getenv("MCP_LOG_LEVEL", "info")
    
    print("🌾 Starting BhoomiSetu MCP Server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔄 Reload mode: {reload}")
    
    # Start server
    uvicorn.run(
        "src.mcp.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )
