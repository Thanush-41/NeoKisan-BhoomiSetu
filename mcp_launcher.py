#!/usr/bin/env python3
"""
MCP Server Launcher for BhoomiSetu
This launcher ensures proper environment setup for Claude Desktop
"""
import sys
import os
import asyncio
import json
import logging

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set up minimal logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(project_root, 'mcp_debug.log'))]
)

logger = logging.getLogger(__name__)

async def main():
    """Launch the MCP server"""
    try:
        logger.info("🚀 Starting BhoomiSetu MCP Launcher...")
        
        # Import and run the MCP server
        from src.mcp.mcp_server_claude import MCPServer
        
        server = MCPServer()
        logger.info("✅ MCP Server initialized")
        
        # Handle stdin/stdout communication
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    logger.info("📡 No input received, continuing...")
                    await asyncio.sleep(0.1)
                    continue
                
                line = line.strip()
                if not line:
                    continue
                
                logger.info(f"📥 Received message: {line[:100]}...")
                
                message = json.loads(line)
                response = await server.handle_message(message)
                
                # Send response to stdout
                print(json.dumps(response), flush=True)
                logger.info(f"📤 Sent response: {str(response)[:100]}...")
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                logger.error(f"❌ JSON parse error: {e}")
                
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0", 
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                logger.error(f"❌ Internal error: {e}")
                
    except KeyboardInterrupt:
        logger.info("🛑 MCP Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("🌾 BhoomiSetu MCP Launcher starting...")
    asyncio.run(main())
