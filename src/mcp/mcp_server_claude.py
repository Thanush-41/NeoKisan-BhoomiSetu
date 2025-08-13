#!/usr/bin/env python3
"""
MCP Server for BhoomiSetu Agricultural AI - Claude Desktop Compatible
This server implements the Model Context Protocol for Claude Desktop integration
"""

import json
import sys
import asyncio
import logging
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

# Add project root to path
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server implementing the Model Context Protocol"""
    
    def __init__(self):
        self.agri_agent = None
        self.crop_recommender = None
        self.disease_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize BhoomiSetu services"""
        try:
            from src.agents.agri_agent import agri_agent
            from src.agents.crop_recommender import crop_recommender
            from src.services.crop_disease_service import crop_disease_service
            
            self.agri_agent = agri_agent
            self.crop_recommender = crop_recommender
            self.disease_service = crop_disease_service
            
            logger.info("✅ BhoomiSetu services initialized")
        except ImportError as e:
            logger.warning(f"⚠️ Could not import some services: {e}")
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP messages"""
        try:
            method = message.get("method")
            params = message.get("params", {})
            
            # Build base response
            response = {
                "jsonrpc": "2.0"
            }
            
            if method == "initialize":
                response["result"] = self._handle_initialize(params)
            elif method == "tools/list":
                response["result"] = self._handle_list_tools()
            elif method == "tools/call":
                response["result"] = await self._handle_call_tool(params)
            elif method == "resources/list":
                response["result"] = self._handle_list_resources()
            elif method == "resources/read":
                response["result"] = self._handle_read_resource(params)
            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "logging": {}
            },
            "serverInfo": {
                "name": "BhoomiSetu Agricultural AI",
                "version": "1.0.0"
            }
        }
    
    def _handle_list_tools(self) -> Dict[str, Any]:
        """Handle tools/list request"""
        tools = [
            {
                "name": "agricultural_chat",
                "description": "Chat with BhoomiSetu Agricultural AI for farming advice, crop recommendations, weather guidance, and market information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Your agricultural question or query"
                        },
                        "language": {
                            "type": "string",
                            "description": "Response language (en, hi, te, etc.)",
                            "default": "en"
                        },
                        "location": {
                            "type": "string",
                            "description": "Your location (city, state, country)"
                        },
                        "crop_type": {
                            "type": "string",
                            "description": "Specific crop you're asking about"
                        }
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "crop_recommendation",
                "description": "Get AI-powered crop recommendations based on soil, climate, location, and farming conditions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "soil_type": {
                            "type": "string",
                            "description": "Type of soil (clay, sandy, loamy, etc.)"
                        },
                        "season": {
                            "type": "string",
                            "description": "Current season (kharif, rabi, summer)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Farm location (city, state)"
                        },
                        "farm_size": {
                            "type": "number",
                            "description": "Farm size in acres"
                        },
                        "budget": {
                            "type": "number",
                            "description": "Available budget in INR"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "disease_detection",
                "description": "Detect crop diseases and get treatment recommendations based on symptoms",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "crop_type": {
                            "type": "string",
                            "description": "Type of crop (rice, wheat, tomato, etc.)"
                        },
                        "symptoms": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of observed symptoms"
                        },
                        "location": {
                            "type": "string",
                            "description": "Location where crop is grown"
                        }
                    },
                    "required": ["crop_type", "symptoms"]
                }
            },
            {
                "name": "weather_analysis",
                "description": "Get weather forecast and agricultural advice based on weather conditions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location for weather analysis"
                        },
                        "crop_type": {
                            "type": "string",
                            "description": "Crop to analyze weather impact for"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "market_prices",
                "description": "Get current market prices for agricultural commodities",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "commodity": {
                            "type": "string",
                            "description": "Agricultural commodity (onion, tomato, rice, etc.)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Market location or state"
                        }
                    },
                    "required": ["commodity"]
                }
            }
        ]
        
        return {"tools": tools}
    
    async def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "agricultural_chat":
                result = await self._agricultural_chat(arguments)
            elif tool_name == "crop_recommendation":
                result = await self._crop_recommendation(arguments)
            elif tool_name == "disease_detection":
                result = await self._disease_detection(arguments)
            elif tool_name == "weather_analysis":
                result = await self._weather_analysis(arguments)
            elif tool_name == "market_prices":
                result = await self._market_prices(arguments)
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unknown tool: {tool_name}"
                        }
                    ],
                    "isError": True
                }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing tool: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _agricultural_chat(self, args: Dict[str, Any]) -> str:
        """Handle agricultural chat"""
        if not self.agri_agent:
            return "❌ Agricultural AI agent not available"
        
        message = args.get("message", "")
        language = args.get("language", "en")
        location = args.get("location")
        crop_type = args.get("crop_type")
        
        context = {
            "location": location,
            "crop_type": crop_type,
            "conversation_history": []
        }
        
        try:
            response = await self.agri_agent.process_query(message, context, language)
            
            # Handle both string and dict responses
            if isinstance(response, str):
                result = f"🌾 **Agricultural AI Response:**\n\n{response}"
            elif isinstance(response, dict):
                result = f"🌾 **Agricultural AI Response:**\n\n{response.get('response', '')}"
                
                if response.get("suggestions"):
                    result += f"\n\n**Suggestions:**\n"
                    for suggestion in response["suggestions"][:3]:
                        result += f"• {suggestion}\n"
            else:
                result = f"🌾 **Agricultural AI Response:**\n\n{str(response)}"
            
            return result
            
        except Exception as e:
            return f"❌ Error processing query: {str(e)}"
    
    async def _crop_recommendation(self, args: Dict[str, Any]) -> str:
        """Handle crop recommendation"""
        if not self.crop_recommender:
            return "❌ Crop recommendation service not available"
        
        try:
            recommendations = await self.crop_recommender.get_recommendations(args)
            
            result = "🌱 **Crop Recommendations:**\n\n"
            
            crops = recommendations.get("crops", [])
            for i, crop in enumerate(crops[:5], 1):
                if isinstance(crop, dict):
                    crop_name = crop.get("name", crop.get("crop", str(crop)))
                    result += f"{i}. **{crop_name}**\n"
                else:
                    result += f"{i}. {crop}\n"
            
            reasons = recommendations.get("reasons", [])
            if reasons:
                result += "\n**Reasons:**\n"
                for reason in reasons[:3]:
                    result += f"• {reason}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error getting crop recommendations: {str(e)}"
    
    async def _disease_detection(self, args: Dict[str, Any]) -> str:
        """Handle disease detection"""
        if not self.disease_service:
            return "❌ Disease detection service not available"
        
        try:
            detection = await self.disease_service.detect_diseases(args)
            
            result = "🦠 **Disease Detection Results:**\n\n"
            
            diseases = detection.get("diseases", [])
            if diseases:
                result += "**Detected Diseases:**\n"
                for disease in diseases[:3]:
                    if isinstance(disease, dict):
                        name = disease.get("name", str(disease))
                        result += f"• {name}\n"
                    else:
                        result += f"• {disease}\n"
            
            treatments = detection.get("treatments", [])
            if treatments:
                result += "\n**Treatment Recommendations:**\n"
                for treatment in treatments[:3]:
                    result += f"• {treatment}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error detecting diseases: {str(e)}"
    
    async def _weather_analysis(self, args: Dict[str, Any]) -> str:
        """Handle weather analysis"""
        if not self.agri_agent:
            return "❌ Weather analysis service not available"
        
        location = args.get("location")
        crop_type = args.get("crop_type", "")
        
        query = f"Weather forecast and farming advice for {location}"
        if crop_type:
            query += f" for {crop_type} cultivation"
        
        context = {"location": location, "crop_type": crop_type}
        
        try:
            response = await self.agri_agent.process_query(query, context, "en")
            return f"🌤️ **Weather Analysis:**\n\n{response.get('response', '')}"
        except Exception as e:
            return f"❌ Error getting weather analysis: {str(e)}"
    
    async def _market_prices(self, args: Dict[str, Any]) -> str:
        """Handle market prices"""
        if not self.agri_agent:
            return "❌ Market price service not available"
        
        commodity = args.get("commodity")
        location = args.get("location", "India")
        
        query = f"Current market prices for {commodity} in {location}"
        context = {"location": location, "commodity": commodity}
        
        try:
            response = await self.agri_agent.process_query(query, context, "en")
            return f"💰 **Market Prices for {commodity}:**\n\n{response.get('response', '')}"
        except Exception as e:
            return f"❌ Error getting market prices: {str(e)}"
    
    def _handle_list_resources(self) -> Dict[str, Any]:
        """Handle resources/list request"""
        resources = [
            {
                "uri": "bhoomisetu://agricultural-knowledge",
                "name": "Agricultural Knowledge Base",
                "description": "Comprehensive agricultural knowledge base",
                "mimeType": "text/plain"
            }
        ]
        
        return {"resources": resources}
    
    def _handle_read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")
        
        if uri == "bhoomisetu://agricultural-knowledge":
            content = "Agricultural knowledge base containing comprehensive information about crops, farming practices, and agricultural techniques for Indian farmers."
        else:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Unknown resource URI: {uri}"
                }
            }
        
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": content
                }
            ]
        }

async def read_stdin():
    """Read a line from stdin asynchronously with timeout"""
    loop = asyncio.get_event_loop()
    try:
        # Use a timeout to prevent hanging
        return await asyncio.wait_for(
            loop.run_in_executor(None, sys.stdin.readline),
            timeout=0.1
        )
    except asyncio.TimeoutError:
        return ""

async def main():
    """Main function for MCP server"""
    server = MCPServer()
    
    # Don't log to stderr when used with Claude Desktop
    if not os.environ.get('MCP_DEBUG'):
        logging.disable(logging.CRITICAL)
    
    logger.info("🌾 BhoomiSetu MCP Server started")
    logger.info("📡 Listening on stdin/stdout for MCP messages")
    
    try:
        while True:
            try:
                # Read JSON-RPC message from stdin
                line = await read_stdin()
                if not line:
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.01)
                    continue
                
                line = line.strip()
                if not line:
                    continue
                
                message = json.loads(line)
                response = await server.handle_message(message)
                
                # Add id to response if present in request
                if "id" in message:
                    response["id"] = message["id"]
                
                # Send response to stdout
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                if "id" in locals() and "message" in locals() and "id" in message:
                    error_response["id"] = message["id"]
                
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        logger.info("🔄 Server shutting down")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        # Send error response
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
        sys.stdout.write(json.dumps(error_response) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
