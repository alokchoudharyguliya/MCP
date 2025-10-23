#!/usr/bin/env python3
"""
Test script for git tools in the MCP server
"""

import asyncio
import json
from mcp_server.mcp_complete_server import server

async def test_git_tools():
    """Test the git tools in the MCP server"""
    
    print("=== Testing Git Tools in MCP Server ===")
    
    # Test listing tools
    print("\n1. Testing Tool Listing...")
    tools = await server.list_tools()
    git_tools = [tool for tool in tools if tool.name.startswith('git') or tool.name == 'deploy_hook']
    
    print(f"Found {len(git_tools)} git-related tools:")
    for tool in git_tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test git_status tool (this will fail if no targets configured, but we can see the error handling)
    print("\n2. Testing git_status...")
    try:
        result = await server.call_tool("git_status", {
            "target": "test-target",
            "project_dir": "/home/user/project"
        })
        print("Result:", result[0].text)
    except Exception as e:
        print(f"Expected error (no config): {e}")
    
    # Test git_checkout tool
    print("\n3. Testing git_checkout...")
    try:
        result = await server.call_tool("git_checkout", {
            "target": "test-target",
            "project_dir": "/home/user/project",
            "branch_or_tag": "main"
        })
        print("Result:", result[0].text)
    except Exception as e:
        print(f"Expected error (no config): {e}")
    
    # Test git_pull tool
    print("\n4. Testing git_pull...")
    try:
        result = await server.call_tool("git_pull", {
            "target": "test-target",
            "project_dir": "/home/user/project",
            "branch": "main"
        })
        print("Result:", result[0].text)
    except Exception as e:
        print(f"Expected error (no config): {e}")
    
    # Test deploy_hook tool
    print("\n5. Testing deploy_hook...")
    try:
        result = await server.call_tool("deploy_hook", {
            "target": "test-target",
            "project_dir": "/home/user/project",
            "hook_script": "/home/user/deploy.sh",
            "env": {"ENV": "production"}
        })
        print("Result:", result[0].text)
    except Exception as e:
        print(f"Expected error (no config): {e}")
    
    # Test unknown tool
    print("\n6. Testing unknown tool...")
    try:
        result = await server.call_tool("unknown_git_tool", {})
        print("Result:", result[0].text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_git_tools())
