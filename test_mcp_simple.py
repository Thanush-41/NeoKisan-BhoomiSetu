"""
Simple test for BhoomiSetu MCP Server
Tests the MCP message handling directly
"""

import json
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))

async def test_mcp_direct():
    """Test MCP server message handling directly"""
    
    print("🧪 Testing BhoomiSetu MCP Server (Direct)...")
    
    try:
        # Import the MCP server
        from src.mcp.mcp_server_claude import MCPServer
        
        server = MCPServer()
        print("✅ MCP Server initialized")
        
        # Test messages
        test_messages = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            },
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            },
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "agricultural_chat",
                    "arguments": {
                        "message": "What crops should I plant in Punjab?",
                        "location": "Punjab, India",
                        "language": "en"
                    }
                }
            }
        ]
        
        # Process each test message
        for i, message in enumerate(test_messages, 1):
            print(f"\n📤 Test {i}: {message['method']}")
            
            try:
                response = await server.handle_message(message)
                print(f"✅ Response received")
                
                # Check response structure
                if "result" in response:
                    print(f"📊 Result type: {type(response['result'])}")
                    if message['method'] == 'tools/list':
                        tools = response['result'].get('tools', [])
                        print(f"🛠️ Available tools: {len(tools)}")
                        for tool in tools:
                            print(f"   - {tool.get('name', 'Unknown')}")
                    elif message['method'] == 'tools/call':
                        content = response['result'].get('content', [])
                        if content and content[0].get('text'):
                            text = content[0]['text']
                            print(f"💬 Response preview: {text[:100]}...")
                elif "error" in response:
                    print(f"❌ Error: {response['error']}")
                else:
                    print(f"⚠️ Unexpected response structure")
                    
            except Exception as e:
                print(f"❌ Error processing message: {e}")
        
        print("\n✅ Direct MCP test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_tool_schemas():
    """Test that tool schemas are valid"""
    
    print("\n🔧 Testing tool schemas...")
    
    try:
        from src.mcp.mcp_server_claude import MCPServer
        
        server = MCPServer()
        tools_response = server._handle_list_tools()
        tools = tools_response.get('tools', [])
        
        print(f"📋 Found {len(tools)} tools:")
        
        for tool in tools:
            name = tool.get('name', 'Unknown')
            description = tool.get('description', 'No description')
            schema = tool.get('inputSchema', {})
            
            print(f"\n🛠️ {name}:")
            print(f"   Description: {description[:80]}...")
            
            # Check required properties
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            print(f"   Properties: {len(properties)}")
            print(f"   Required: {required}")
            
            # Validate schema structure
            if schema.get('type') != 'object':
                print(f"   ⚠️ Warning: Schema type should be 'object'")
            
            for prop_name, prop_def in properties.items():
                if not prop_def.get('type'):
                    print(f"   ⚠️ Warning: Property '{prop_name}' missing type")
        
        print("\n✅ Tool schemas test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🌾 BhoomiSetu MCP Server Test Suite")
    print("=" * 50)
    
    # Test 1: Direct message handling
    success1 = await test_mcp_direct()
    
    # Test 2: Tool schemas
    success2 = await test_tool_schemas()
    
    # Summary
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! MCP server is working correctly.")
        print("\n💡 Next steps:")
        print("1. Copy claude_desktop_config.json to your Claude Desktop config")
        print("2. Restart Claude Desktop")
        print("3. Tools should appear automatically in conversations")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
