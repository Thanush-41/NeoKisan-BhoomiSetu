"""
MCP Server compatible with Claude Desktop
This server provides the Model Context Protocol interface for Claude Desktop integration
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# MCP Protocol imports
from src.mcp.claude_bridge import mcp_bridge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server for Claude Desktop integration"""
    
    def __init__(self):
        self.bridge = mcp_bridge
        self.capabilities = {
            "tools": True,
            "resources": True,
            "prompts": False,
            "logging": True
        }
    
    async def initialize(self):
        """Initialize the MCP server"""
        logger.info("🌾 Initializing BhoomiSetu MCP Server for Claude Desktop...")
        
        # Initialize the bridge services (synchronously since _initialize_services is not async)
        try:
            self.bridge._initialize_services()
            logger.info("✅ BhoomiSetu services initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize services: {e}")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests from Claude Desktop"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize":
                return await self._handle_initialize(params)
            elif method == "tools/list":
                return await self._handle_list_tools()
            elif method == "tools/call":
                return await self._handle_call_tool(params)
            elif method == "resources/list":
                return await self._handle_list_resources()
            elif method == "resources/read":
                return await self._handle_read_resource(params)
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": "BhoomiSetu Agricultural AI",
                "version": "1.0.0",
                "description": "AI-powered agricultural advisor for Indian farmers"
            }
        }
    
    async def _handle_list_tools(self) -> Dict[str, Any]:
        """Handle tools/list request"""
        tools = self.bridge.get_tools()
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools
            ]
        }
    
    async def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return {
                "error": {
                    "code": -32602,
                    "message": "Missing tool name"
                }
            }
        
        try:
            result = await self.bridge.handle_tool_call(tool_name, arguments)
            
            # Format result for Claude Desktop
            if "error" in result:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: {result['error']}"
                        }
                    ],
                    "isError": True
                }
            else:
                # Format successful result
                content_text = self._format_tool_result(tool_name, result)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": content_text
                        }
                    ]
                }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tool execution failed: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _handle_list_resources(self) -> Dict[str, Any]:
        """Handle resources/list request"""
        resources = self.bridge.get_resources()
        return {
            "resources": [
                {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description,
                    "mimeType": resource.mimeType
                }
                for resource in resources
            ]
        }
    
    async def _handle_read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")
        
        if not uri:
            return {
                "error": {
                    "code": -32602,
                    "message": "Missing resource URI"
                }
            }
        
        # Handle resource reading based on URI
        if uri == "bhoomisetu://agricultural-knowledge":
            content = "Agricultural knowledge base containing comprehensive information about crops, farming practices, and agricultural techniques for Indian farmers."
        elif uri == "bhoomisetu://crop-database":
            content = "Crop database with information about various crop varieties, their growing conditions, seasons, and yield expectations."
        elif uri == "bhoomisetu://disease-database":
            content = "Plant disease database with symptoms, identification, and treatment recommendations for common agricultural diseases."
        elif uri == "bhoomisetu://market-data":
            content = "Real-time market data including commodity prices, market trends, and trading information from Indian agricultural markets."
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
    
    def _format_tool_result(self, tool_name: str, result: Dict[str, Any]) -> str:
        """Format tool result for display in Claude Desktop"""
        if tool_name == "agricultural_chat":
            response = result.get("response", "")
            query_type = result.get("query_type", "")
            suggestions = result.get("suggestions", [])
            
            formatted = f"🌾 **Agricultural AI Response:**\n\n{response}"
            
            if query_type:
                formatted += f"\n\n**Query Type:** {query_type}"
            
            if suggestions:
                formatted += f"\n\n**Suggestions:**\n"
                for suggestion in suggestions[:3]:  # Limit to 3 suggestions
                    formatted += f"• {suggestion}\n"
            
            return formatted
        
        elif tool_name == "crop_recommendation":
            crops = result.get("recommended_crops", [])
            reasons = result.get("reasons", [])
            
            formatted = "🌱 **Crop Recommendations:**\n\n"
            
            for i, crop in enumerate(crops[:5], 1):  # Limit to 5 crops
                if isinstance(crop, dict):
                    crop_name = crop.get("name", crop.get("crop", str(crop)))
                    confidence = crop.get("confidence", "")
                    formatted += f"{i}. **{crop_name}**"
                    if confidence:
                        formatted += f" (Confidence: {confidence})"
                    formatted += "\n"
                else:
                    formatted += f"{i}. {crop}\n"
            
            if reasons:
                formatted += "\n**Reasons:**\n"
                for reason in reasons[:3]:
                    formatted += f"• {reason}\n"
            
            return formatted
        
        elif tool_name == "disease_detection":
            diseases = result.get("detected_diseases", [])
            treatments = result.get("treatment_recommendations", [])
            
            formatted = "🦠 **Disease Detection Results:**\n\n"
            
            if diseases:
                formatted += "**Detected Diseases:**\n"
                for disease in diseases[:3]:
                    if isinstance(disease, dict):
                        name = disease.get("name", str(disease))
                        confidence = disease.get("confidence", "")
                        formatted += f"• {name}"
                        if confidence:
                            formatted += f" ({confidence}% confidence)"
                        formatted += "\n"
                    else:
                        formatted += f"• {disease}\n"
            
            if treatments:
                formatted += "\n**Treatment Recommendations:**\n"
                for treatment in treatments[:3]:
                    formatted += f"• {treatment}\n"
            
            return formatted
        
        elif tool_name == "weather_analysis":
            forecast = result.get("weather_forecast", "")
            advice = result.get("farming_advice", "")
            
            formatted = "🌤️ **Weather Analysis:**\n\n"
            if forecast:
                formatted += f"**Forecast:** {forecast}\n\n"
            if advice:
                formatted += f"**Farming Advice:** {advice}"
            
            return formatted
        
        elif tool_name == "market_prices":
            commodity = result.get("commodity", "")
            price_info = result.get("price_info", "")
            
            formatted = f"💰 **Market Prices for {commodity}:**\n\n{price_info}"
            return formatted
        
        elif tool_name == "government_schemes":
            schemes = result.get("schemes", "")
            
            formatted = f"🏛️ **Government Schemes:**\n\n{schemes}"
            return formatted
        
        else:
            # Generic formatting for unknown tools
            return json.dumps(result, indent=2)

# Create MCP server instance
mcp_server = MCPServer()

async def main():
    """Main function for Claude Desktop MCP server"""
    await mcp_server.initialize()
    
    # In a real MCP server, this would handle stdin/stdout communication
    # For now, this serves as a test function
    logger.info("🚀 BhoomiSetu MCP Server ready for Claude Desktop integration")
    
    # Test tool listing
    tools_response = await mcp_server._handle_list_tools()
    logger.info(f"Available tools: {len(tools_response['tools'])}")
    
    # Test a sample tool call
    test_request = {
        "name": "agricultural_chat",
        "arguments": {
            "message": "What crops should I plant in Punjab during winter?",
            "location": "Punjab, India",
            "language": "en"
        }
    }
    
    result = await mcp_server._handle_call_tool(test_request)
    logger.info("✅ Test tool call completed")

if __name__ == "__main__":
    asyncio.run(main())
