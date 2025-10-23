#!/usr/bin/env python3
"""
Test script for the complete MCP server
"""

import asyncio
import json
from mcp_server.mcp_complete_server import server

async def test_server():
    """Test the MCP server functionality"""
    
    # Test listing tools
    print("=== Testing Tool Listing ===")
    tools = await server.list_tools()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    print("\n=== Testing Tool Calls ===")
    
    # Test SSH exec (this will fail if no targets are configured, but we can see the error handling)
    print("\n1. Testing ssh_exec...")
    try:
        result = await server.call_tool("ssh_exec", {
            "target": "test-target",
            "command": "echo 'Hello World'"
        })
        print("Result:", result[0].text)
    except Exception as e:
        print(f"Expected error (no config): {e}")
    
    # Test scp_put (this will also fail without proper config)
    print("\n2. Testing scp_put...")
    try:
        test_content = "Hello, World!"
        content_b64 = test_content.encode('utf-8').hex()  # Using hex instead of base64 for simplicity
        result = await server.call_tool("scp_put", {
            "target": "test-target",
            "remote_path": "/tmp/test.txt",
            "content_b64": content_b64
        })
        print("Result:", result[0].text)
    except Exception as e:
        print(f"Expected error (no config): {e}")
    
    # Test unknown tool
    print("\n3. Testing unknown tool...")
    try:
        result = await server.call_tool("unknown_tool", {})
        print("Result:", result[0].text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_server())
