"""
Simple MCP Server for BhoomiSetu - Claude Desktop Integration
"""
import sys
import os
import json
import asyncio
import logging

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Disable emojis for Windows compatibility
os.environ['NO_EMOJIS'] = '1'

class SimpleMCPServer:
    def __init__(self):
        self.services = None
        self._initialize()
    
    def _initialize(self):
        try:
            # Import services
            from src.agents.agri_agent import AgricultureAIAgent
            from src.agents.crop_recommender import CropRecommendationAgent
            
            # Initialize services
            self.agri_agent = AgricultureAIAgent()
            self.crop_agent = CropRecommendationAgent()
            self.services = True
            
        except Exception as e:
            logging.error(f"Failed to initialize services: {e}")
            sys.exit(1)
    
    async def handle_message(self, message):
        """Handle incoming MCP messages"""
        try:
            method = message.get("method")
            msg_id = message.get("id")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "bhoomisetu",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {
                                "name": "agricultural_chat",
                                "description": "Get agricultural advice and answers to farming questions",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string", "description": "Your farming question or query"}
                                    },
                                    "required": ["message"]
                                }
                            },
                            {
                                "name": "crop_recommendation",
                                "description": "Get crop recommendations based on soil and climate conditions",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "state": {"type": "string", "description": "Indian state name"},
                                        "city": {"type": "string", "description": "City name"},
                                        "soil_type": {"type": "string", "description": "Type of soil"},
                                        "season": {"type": "string", "description": "Current season"}
                                    },
                                    "required": ["state", "city", "soil_type", "season"]
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = message["params"]["name"]
                arguments = message["params"]["arguments"]
                
                if tool_name == "agricultural_chat":
                    user_message = arguments.get("message", "")
                    response = await self.agri_agent.generate_response(user_message)
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": response
                                }
                            ]
                        }
                    }
                
                elif tool_name == "crop_recommendation":
                    recommendation = await self.crop_agent.get_crop_recommendation(
                        state=arguments.get("state", ""),
                        city=arguments.get("city", ""),
                        soil_type=arguments.get("soil_type", ""),
                        season=arguments.get("season", "")
                    )
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": recommendation
                                }
                            ]
                        }
                    }
                
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

def main():
    """Main function"""
    server = SimpleMCPServer()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            line = line.strip()
            if not line:
                continue
            
            message = json.loads(line)
            response = asyncio.run(server.handle_message(message))
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            print(json.dumps(error_response), flush=True)
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

if __name__ == "__main__":
    main()
