#!/usr/bin/env python3
"""
Test the Open WebUI + MCP setup
"""

import requests
import json

def test_openwebui():
    """Test if Open WebUI is accessible"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Open WebUI is running at http://localhost:3000")
            return True
        else:
            print(f"❌ Open WebUI returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Open WebUI not accessible: {e}")
        return False

def test_mcp_server():
    """Test if MCP server is accessible"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP Server is running at http://localhost:8000")
            return True
        else:
            print(f"❌ MCP Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP Server not accessible: {e}")
        return False

def test_mcp_tools():
    """Test if MCP tools are available"""
    try:
        response = requests.get("http://localhost:8000/.well-known/mcp/tools", timeout=5)
        if response.status_code == 200:
            tools = response.json()
            print(f"✅ MCP Server has {len(tools.get('tools', []))} tools available")
            return True
        else:
            print(f"❌ MCP Tools returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP Tools not accessible: {e}")
        return False

def main():
    print("🧪 Testing Open WebUI + MCP Setup")
    print("=" * 40)
    
    openwebui_ok = test_openwebui()
    mcp_server_ok = test_mcp_server()
    mcp_tools_ok = test_mcp_tools()
    
    print("\n" + "=" * 40)
    if openwebui_ok and mcp_server_ok and mcp_tools_ok:
        print("🎉 All services are running correctly!")
        print("\n📋 Next steps:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Create your first account (admin account)")
        print("3. Configure MCP server connection in Open WebUI")
        print("4. Start using unlimited local AI with GPIO control!")
    else:
        print("❌ Some services are not working properly")
        if not openwebui_ok:
            print("   - Check Open WebUI container: docker logs open-webui")
        if not mcp_server_ok:
            print("   - Check MCP server: python run_mcp_with_openwebui.py")

if __name__ == "__main__":
    main()
