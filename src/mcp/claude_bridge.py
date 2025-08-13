"""
Claude Desktop MCP Bridge for BhoomiSetu
Provides MCP-compatible interface for Claude Desktop integration
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

@dataclass
class Tool:
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

@dataclass
class Resource:
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mimeType: str

class BhoomiSetuMCPBridge:
    """MCP Bridge for BhoomiSetu Agricultural AI"""
    
    def __init__(self):
        self.name = "BhoomiSetu Agricultural AI"
        self.version = "1.0.0"
        
        # Initialize services
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
            
        except ImportError as e:
            print(f"Warning: Could not import some services: {e}")
    
    def get_tools(self) -> List[Tool]:
        """Get available MCP tools"""
        return [
            Tool(
                name="agricultural_chat",
                description="Chat with BhoomiSetu Agricultural AI for farming advice, crop recommendations, weather guidance, and market information in multiple Indian languages",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Your agricultural question or query"
                        },
                        "language": {
                            "type": "string",
                            "description": "Response language (en, hi, te, ta, etc.)",
                            "default": "en"
                        },
                        "location": {
                            "type": "string",
                            "description": "Your location (city, state, country)"
                        },
                        "crop_type": {
                            "type": "string",
                            "description": "Specific crop you're asking about (optional)"
                        }
                    },
                    "required": ["message"]
                }
            ),
            Tool(
                name="crop_recommendation",
                description="Get AI-powered crop recommendations based on soil, climate, location, and farming conditions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "soil_type": {
                            "type": "string",
                            "description": "Type of soil (clay, sandy, loamy, etc.)"
                        },
                        "climate_zone": {
                            "type": "string",
                            "description": "Climate zone (tropical, subtropical, temperate, etc.)"
                        },
                        "season": {
                            "type": "string",
                            "description": "Current season (kharif, rabi, summer, monsoon)"
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
                        },
                        "irrigation_type": {
                            "type": "string",
                            "description": "Irrigation method (drip, sprinkler, flood, rainfed)"
                        }
                    },
                    "required": ["location"]
                }
            ),
            Tool(
                name="disease_detection",
                description="Detect crop diseases and get treatment recommendations based on symptoms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "crop_type": {
                            "type": "string",
                            "description": "Type of crop (rice, wheat, tomato, etc.)"
                        },
                        "symptoms": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of observed symptoms (yellow leaves, brown spots, wilting, etc.)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Location where crop is grown"
                        },
                        "weather_conditions": {
                            "type": "string",
                            "description": "Current weather conditions (hot, humid, dry, rainy, etc.)"
                        }
                    },
                    "required": ["crop_type", "symptoms"]
                }
            ),
            Tool(
                name="weather_analysis",
                description="Get weather forecast and agricultural advice based on weather conditions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location for weather analysis"
                        },
                        "crop_type": {
                            "type": "string",
                            "description": "Crop to analyze weather impact for (optional)"
                        },
                        "farming_activity": {
                            "type": "string",
                            "description": "Specific farming activity (sowing, harvesting, irrigation, etc.)"
                        }
                    },
                    "required": ["location"]
                }
            ),
            Tool(
                name="market_prices",
                description="Get current market prices for agricultural commodities across Indian markets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "commodity": {
                            "type": "string",
                            "description": "Agricultural commodity (onion, tomato, rice, wheat, etc.)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Market location or state (optional)"
                        }
                    },
                    "required": ["commodity"]
                }
            ),
            Tool(
                name="government_schemes",
                description="Get information about Indian government agricultural schemes and subsidies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scheme_type": {
                            "type": "string",
                            "description": "Type of scheme (loan, insurance, subsidy, pm-kisan, etc.)"
                        },
                        "state": {
                            "type": "string",
                            "description": "Indian state for state-specific schemes"
                        },
                        "farmer_category": {
                            "type": "string",
                            "description": "Farmer category (small, marginal, large, etc.)"
                        }
                    }
                }
            )
        ]
    
    def get_resources(self) -> List[Resource]:
        """Get available MCP resources"""
        return [
            Resource(
                uri="bhoomisetu://agricultural-knowledge",
                name="Agricultural Knowledge Base",
                description="Comprehensive agricultural knowledge base covering crops, diseases, weather, and farming practices",
                mimeType="application/json"
            ),
            Resource(
                uri="bhoomisetu://crop-database",
                name="Crop Database",
                description="Database of crop varieties, growing conditions, and yield information",
                mimeType="application/json"
            ),
            Resource(
                uri="bhoomisetu://disease-database",
                name="Disease Database", 
                description="Plant disease identification and treatment database",
                mimeType="application/json"
            ),
            Resource(
                uri="bhoomisetu://market-data",
                name="Market Data",
                description="Real-time agricultural commodity prices and market trends",
                mimeType="application/json"
            )
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls"""
        try:
            if tool_name == "agricultural_chat":
                return await self._handle_agricultural_chat(arguments)
            elif tool_name == "crop_recommendation":
                return await self._handle_crop_recommendation(arguments)
            elif tool_name == "disease_detection":
                return await self._handle_disease_detection(arguments)
            elif tool_name == "weather_analysis":
                return await self._handle_weather_analysis(arguments)
            elif tool_name == "market_prices":
                return await self._handle_market_prices(arguments)
            elif tool_name == "government_schemes":
                return await self._handle_government_schemes(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def _handle_agricultural_chat(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agricultural chat requests"""
        if not self.agri_agent:
            return {"error": "Agricultural AI agent not available"}
        
        message = args.get("message", "")
        language = args.get("language", "en")
        location = args.get("location")
        crop_type = args.get("crop_type")
        
        context = {
            "location": location,
            "crop_type": crop_type,
            "conversation_history": []
        }
        
        response = await self.agri_agent.process_query(message, context, language)
        
        return {
            "response": response.get("response", ""),
            "language": response.get("language", language),
            "query_type": response.get("query_type", "general"),
            "confidence": response.get("confidence"),
            "sources": response.get("sources", []),
            "suggestions": response.get("suggestions", [])
        }
    
    async def _handle_crop_recommendation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle crop recommendation requests"""
        if not self.crop_recommender:
            return {"error": "Crop recommendation service not available"}
        
        try:
            recommendations = await self.crop_recommender.get_recommendations(args)
            return {
                "recommended_crops": recommendations.get("crops", []),
                "reasons": recommendations.get("reasons", []),
                "season_advice": recommendations.get("season_advice"),
                "estimated_yield": recommendations.get("estimated_yield"),
                "investment_required": recommendations.get("investment_required"),
                "success_tips": recommendations.get("success_tips", [])
            }
        except Exception as e:
            return {"error": f"Crop recommendation failed: {str(e)}"}
    
    async def _handle_disease_detection(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle disease detection requests"""
        if not self.disease_service:
            return {"error": "Disease detection service not available"}
        
        try:
            detection = await self.disease_service.detect_diseases(args)
            return {
                "detected_diseases": detection.get("diseases", []),
                "confidence_scores": detection.get("confidence_scores", {}),
                "treatment_recommendations": detection.get("treatments", []),
                "prevention_tips": detection.get("prevention", []),
                "severity_level": detection.get("severity"),
                "immediate_actions": detection.get("immediate_actions", [])
            }
        except Exception as e:
            return {"error": f"Disease detection failed: {str(e)}"}
    
    async def _handle_weather_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle weather analysis requests"""
        if not self.agri_agent:
            return {"error": "Weather analysis service not available"}
        
        location = args.get("location")
        crop_type = args.get("crop_type", "")
        activity = args.get("farming_activity", "")
        
        query = f"Weather forecast and farming advice for {location}"
        if crop_type:
            query += f" for {crop_type} cultivation"
        if activity:
            query += f" for {activity}"
        
        context = {"location": location, "crop_type": crop_type}
        response = await self.agri_agent.process_query(query, context, "en")
        
        return {
            "weather_forecast": response.get("response", ""),
            "farming_advice": response.get("farming_advice", ""),
            "recommendations": response.get("suggestions", [])
        }
    
    async def _handle_market_prices(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle market price requests"""
        if not self.agri_agent:
            return {"error": "Market price service not available"}
        
        commodity = args.get("commodity")
        location = args.get("location", "India")
        
        query = f"Current market prices for {commodity} in {location}"
        context = {"location": location, "commodity": commodity}
        
        response = await self.agri_agent.process_query(query, context, "en")
        
        return {
            "commodity": commodity,
            "location": location,
            "price_info": response.get("response", ""),
            "market_trends": response.get("suggestions", [])
        }
    
    async def _handle_government_schemes(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle government schemes requests"""
        if not self.agri_agent:
            return {"error": "Government schemes service not available"}
        
        scheme_type = args.get("scheme_type", "agricultural schemes")
        state = args.get("state", "India")
        farmer_category = args.get("farmer_category", "")
        
        query = f"Government {scheme_type} for farmers in {state}"
        if farmer_category:
            query += f" for {farmer_category} farmers"
        
        context = {"location": state, "farmer_category": farmer_category}
        response = await self.agri_agent.process_query(query, context, "en")
        
        return {
            "schemes": response.get("response", ""),
            "eligibility": response.get("eligibility", ""),
            "application_process": response.get("suggestions", [])
        }

# Initialize the MCP bridge
mcp_bridge = BhoomiSetuMCPBridge()

def get_tools():
    """Get available tools for Claude Desktop"""
    return [tool.__dict__ for tool in mcp_bridge.get_tools()]

def get_resources():
    """Get available resources for Claude Desktop"""
    return [resource.__dict__ for resource in mcp_bridge.get_resources()]

async def call_tool(name: str, arguments: dict):
    """Call a tool and return the result"""
    return await mcp_bridge.handle_tool_call(name, arguments)

if __name__ == "__main__":
    # Test the MCP bridge
    print("🌾 BhoomiSetu MCP Bridge for Claude Desktop")
    print("Available tools:")
    for tool in mcp_bridge.get_tools():
        print(f"  - {tool.name}: {tool.description}")
    
    print("\nAvailable resources:")
    for resource in mcp_bridge.get_resources():
        print(f"  - {resource.name}: {resource.description}")
