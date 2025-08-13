#!/usr/bin/env python3
"""
Test the simple MCP server
"""
import json
import subprocess
import sys

def test_mcp_server():
    """Test the simple MCP server"""
    print("🧪 Testing Simple MCP Server...")
    
    # Test messages
    messages = [
        {
            "jsonrpc": "2.0", 
            "id": 1, 
            "method": "initialize", 
            "params": {}
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
                    "message": "What crops grow well in Punjab?"
                }
            }
        }
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Test {i}: {message['method']} ---")
        
        # Convert message to JSON string
        input_data = json.dumps(message) + "\n"
        
        try:
            # Run the server with the message
            process = subprocess.Popen(
                [sys.executable, "mcp_simple.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd="t:\\BhoomiSetu"
            )
            
            stdout, stderr = process.communicate(input=input_data, timeout=30)
            
            if stderr:
                print(f"STDERR: {stderr}")
            
            if stdout:
                # Try to parse the response
                try:
                    response = json.loads(stdout.strip())
                    print(f"✅ Response: {json.dumps(response, indent=2)}")
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response: {stdout}")
            else:
                print("❌ No response received")
                
        except subprocess.TimeoutExpired:
            print("❌ Test timed out")
            process.kill()
        except Exception as e:
            print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_mcp_server()
