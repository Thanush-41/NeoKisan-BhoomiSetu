"""
Persistent MCP Server for BhoomiSetu - Claude Desktop Integration
This version stays running and handles multiple messages
"""
import sys
import os
import json
import logging

# Set up debug logging
debug_file = os.path.join(os.path.dirname(__file__), 'mcp_debug.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(debug_file),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class MockAgriAgent:
    async def generate_response(self, message):
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
    async def get_crop_recommendation(self, state, city, soil_type, season):
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

class PersistentMCPServer:
    def __init__(self):
        self.agri_agent = MockAgriAgent()
        self.crop_agent = MockCropAgent()
        logger.info("BhoomiSetu MCP Server initialized")
    
    def handle_message(self, message):
        """Handle incoming MCP messages synchronously"""
        try:
            method = message.get("method")
            msg_id = message.get("id")
            
            logger.info(f"Handling method: {method} with id: {msg_id}")
            
            if method == "initialize":
                response = {
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
                logger.info("Initialize response prepared")
                return response
            
            elif method == "tools/list":
                response = {
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
                logger.info("Tools list response prepared")
                return response
            
            elif method == "tools/call":
                tool_name = message["params"]["name"]
                arguments = message["params"]["arguments"]
                
                logger.info(f"Calling tool: {tool_name} with args: {arguments}")
                
                if tool_name == "agricultural_chat":
                    user_message = arguments.get("message", "")
                    # Since we can't use async in this version, simulate the response
                    if "punjab" in user_message.lower():
                        response_text = """Punjab is excellent for growing:
1. **Wheat** - Main rabi crop, sow in November-December
2. **Rice** - Main kharif crop, sow in June-July  
3. **Cotton** - Cash crop, good for southern Punjab
4. **Sugarcane** - Perennial crop, requires good irrigation
5. **Maize** - Can be grown in both seasons

Punjab's fertile alluvial soil and good irrigation make it ideal for these crops. Consider crop rotation and sustainable farming practices."""
                    elif "crop" in user_message.lower():
                        response_text = """For crop selection, consider:
1. **Soil type** - Clay, sandy, loamy
2. **Climate** - Temperature and rainfall patterns
3. **Season** - Kharif (monsoon) or Rabi (winter)
4. **Water availability** - Irrigation facilities
5. **Market demand** - Current prices and demand

Popular crops by season:
- **Kharif**: Rice, Cotton, Sugarcane, Maize
- **Rabi**: Wheat, Gram, Mustard, Barley"""
                    else:
                        response_text = f"""Thank you for your question: "{user_message}"

I'm BhoomiSetu, your AI agricultural advisor. I can help with:
- Crop recommendations based on location and soil
- Farming techniques and best practices  
- Pest and disease management
- Weather-based farming advice
- Market price information

Please ask me specific questions about farming, crops, or agricultural practices!"""
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": response_text
                                }
                            ]
                        }
                    }
                    logger.info("Agricultural chat response prepared")
                    return response
                
                elif tool_name == "crop_recommendation":
                    state = arguments.get("state", "")
                    city = arguments.get("city", "")
                    soil_type = arguments.get("soil_type", "")
                    season = arguments.get("season", "")
                    
                    recommendation = f"""Crop Recommendation for {city}, {state}:

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
                    
                    response = {
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
                    logger.info("Crop recommendation response prepared")
                    return response
                
                else:
                    logger.warning(f"Unknown tool: {tool_name}")
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    }
            
            else:
                logger.warning(f"Unknown method: {method}")
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

def main():
    """Main function that keeps the server running"""
    server = PersistentMCPServer()
    logger.info("Starting persistent MCP server")
    
    try:
        while True:
            try:
                # Read line from stdin (blocking)
                line = sys.stdin.readline()
                
                # If no line, stdin was closed
                if not line:
                    logger.info("stdin closed, exiting")
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                logger.info(f"Received message: {line}")
                
                # Parse and handle the message
                message = json.loads(line)
                response = server.handle_message(message)
                
                # Send response to stdout
                output = json.dumps(response)
                print(output, flush=True)
                logger.info(f"Sent response: {output}")
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
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
                logger.error(f"Unexpected error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    
    logger.info("MCP server exited")

if __name__ == "__main__":
    main()
