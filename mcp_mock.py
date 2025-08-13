"""
Simple MCP Server for BhoomiSetu - No Dependencies on Complex Services
"""
import sys
import os
import json
import asyncio

class MockAgriAgent:
    """Mock agricultural agent for testing"""
    
    async def generate_response(self, message):
        """Generate a mock response"""
        if "punjab" in message.lower():
            return """Punjab is excellent for growing:
1. **Wheat** - Main rabi crop, sow in November-December
2. **Rice** - Main kharif crop, sow in June-July  
3. **Cotton** - Cash crop, good for southern Punjab
4. **Sugarcane** - Perennial crop, requires good irrigation
5. **Maize** - Can be grown in both seasons

Punjab's fertile alluvial soil and good irrigation make it ideal for these crops. Consider crop rotation and sustainable farming practices."""
        
        elif "crop" in message.lower():
            return """For crop selection, consider:
1. **Soil type** - Clay, sandy, loamy
2. **Climate** - Temperature and rainfall patterns
3. **Season** - Kharif (monsoon) or Rabi (winter)
4. **Water availability** - Irrigation facilities
5. **Market demand** - Current prices and demand

Popular crops by season:
- **Kharif**: Rice, Cotton, Sugarcane, Maize
- **Rabi**: Wheat, Gram, Mustard, Barley"""
        
        else:
            return f"""Thank you for your question: "{message}"

I'm BhoomiSetu, your AI agricultural advisor. I can help with:
- Crop recommendations based on location and soil
- Farming techniques and best practices  
- Pest and disease management
- Weather-based farming advice
- Market price information

Please ask me specific questions about farming, crops, or agricultural practices!"""

class MockCropAgent:
    """Mock crop recommendation agent"""
    
    async def get_crop_recommendation(self, state, city, soil_type, season):
        """Generate mock crop recommendation"""
        return f"""Crop Recommendation for {city}, {state}:

**Location**: {city}, {state}
**Soil Type**: {soil_type}
**Season**: {season}

**Recommended Crops**:
1. **Primary**: Rice (if kharif) or Wheat (if rabi)
2. **Secondary**: Based on local climate conditions
3. **Cash Crop**: Cotton or Sugarcane (if suitable)

**Farming Tips**:
- Prepare soil 2-3 weeks before sowing
- Use quality seeds from certified sources
- Apply organic fertilizers for better soil health
- Plan irrigation based on crop water requirements

**Note**: This is a basic recommendation. Consult local agricultural experts for detailed advice."""

class SimpleMCPServer:
    def __init__(self):
        # Use mock agents to avoid complex initialization
        self.agri_agent = MockAgriAgent()
        self.crop_agent = MockCropAgent()
    
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
