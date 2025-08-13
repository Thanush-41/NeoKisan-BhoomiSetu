#!/usr/bin/env python3
"""
Comprehensive test for the mock MCP server
"""
import json
import subprocess
import sys

def test_mcp_mock_server():
    """Test the mock MCP server thoroughly"""
    print("Testing Mock MCP Server...")
    
    # Test messages
    tests = [
        {
            "name": "Initialize",
            "message": {
                "jsonrpc": "2.0", 
                "id": 1, 
                "method": "initialize", 
                "params": {}
            }
        },
        {
            "name": "List Tools",
            "message": {
                "jsonrpc": "2.0", 
                "id": 2, 
                "method": "tools/list", 
                "params": {}
            }
        },
        {
            "name": "Agricultural Chat - Punjab",
            "message": {
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
        },
        {
            "name": "Agricultural Chat - General",
            "message": {
                "jsonrpc": "2.0", 
                "id": 4, 
                "method": "tools/call", 
                "params": {
                    "name": "agricultural_chat",
                    "arguments": {
                        "message": "What is crop rotation?"
                    }
                }
            }
        },
        {
            "name": "Crop Recommendation",
            "message": {
                "jsonrpc": "2.0", 
                "id": 5, 
                "method": "tools/call", 
                "params": {
                    "name": "crop_recommendation",
                    "arguments": {
                        "state": "Punjab",
                        "city": "Ludhiana", 
                        "soil_type": "Alluvial",
                        "season": "Kharif"
                    }
                }
            }
        }
    ]
    
    all_passed = True
    
    for test in tests:
        print(f"\n--- {test['name']} ---")
        
        # Convert message to JSON string
        input_data = json.dumps(test['message']) + "\n"
        
        try:
            # Run the server with the message
            process = subprocess.Popen(
                [sys.executable, "mcp_mock.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd="t:\\BhoomiSetu"
            )
            
            stdout, stderr = process.communicate(input=input_data, timeout=10)
            
            if stderr and stderr.strip():
                print(f"WARNING - STDERR: {stderr}")
            
            if stdout:
                try:
                    response = json.loads(stdout.strip())
                    
                    # Check basic JSON-RPC structure
                    if response.get("jsonrpc") == "2.0" and "id" in response:
                        if "result" in response:
                            print(f"✅ PASSED")
                            print(f"   Response: {json.dumps(response, indent=2)[:200]}...")
                        elif "error" in response:
                            print(f"❌ ERROR in response: {response['error']}")
                            all_passed = False
                        else:
                            print(f"❌ Invalid response structure")
                            all_passed = False
                    else:
                        print(f"❌ Invalid JSON-RPC response")
                        all_passed = False
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response: {stdout}")
                    all_passed = False
            else:
                print("❌ No response received")
                all_passed = False
                
        except subprocess.TimeoutExpired:
            print("❌ Test timed out")
            process.kill()
            all_passed = False
        except Exception as e:
            print(f"❌ Test failed: {e}")
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 ALL TESTS PASSED! MCP Mock Server is working correctly.")
        print("\n📋 Next Steps:")
        print("1. Copy claude_desktop_config.json to your Claude Desktop config directory")
        print("2. Restart Claude Desktop")
        print("3. The 'bhoomisetu' tools should now be available in Claude Desktop")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print(f"{'='*50}")

if __name__ == "__main__":
    test_mcp_mock_server()
