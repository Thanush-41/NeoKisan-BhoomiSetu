"""
Test script for BhoomiSetu MCP Server
Tests the MCP protocol implementation
"""

import json
import subprocess
import sys
import os

def test_mcp_server():
    """Test the MCP server by sending JSON-RPC messages"""
    
    # Path to the MCP server
    server_path = os.path.join(os.path.dirname(__file__), "src", "mcp", "mcp_server_claude.py")
    
    print("🧪 Testing BhoomiSetu MCP Server...")
    
    # Test messages
    test_messages = [
        # Initialize
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
        # List tools
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        },
        # Call agricultural chat tool
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
    
    try:
        # Start the MCP server process
        process = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        print("✅ MCP Server started")
        
        # Send test messages
        for i, message in enumerate(test_messages, 1):
            print(f"\n📤 Sending test message {i}: {message['method']}")
            
            # Send message
            process.stdin.write(json.dumps(message) + "\n")
            process.stdin.flush()
            
            # Read response (with timeout)
            try:
                response_line = process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    print(f"📥 Response: {json.dumps(response, indent=2)[:200]}...")
                else:
                    print("❌ No response received")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
            except Exception as e:
                print(f"❌ Error reading response: {e}")
        
        # Clean shutdown
        process.stdin.close()
        process.terminate()
        process.wait(timeout=5)
        
        print("\n✅ MCP Server test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    test_mcp_server()
