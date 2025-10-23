#!/usr/bin/env python3
"""
Open WebUI Integration Script for MCP Tools
This script helps you integrate your MCP tools with Open WebUI
"""

import requests
import json

class MCPOpenWebUIIntegration:
    def __init__(self, mcp_base_url="http://localhost:8000"):
        self.mcp_base_url = mcp_base_url
        
    def test_connection(self):
        """Test connection to MCP server"""
        try:
            response = requests.get(f"{self.mcp_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_tools(self):
        """Get list of available MCP tools"""
        try:
            response = requests.get(f"{self.mcp_base_url}/.well-known/mcp/tools", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def call_gpio_write(self, pin, value, target="pi-lan", mode="BCM"):
        """Call GPIO write function"""
        data = {
            "target": target,
            "pin": pin,
            "value": value,
            "mode": mode
        }
        try:
            response = requests.post(f"{self.mcp_base_url}/tools/gpio/write", 
                                   json=data, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def call_gpio_read(self, pin, target="pi-lan", mode="BCM"):
        """Call GPIO read function"""
        data = {
            "target": target,
            "pin": pin,
            "mode": mode
        }
        try:
            response = requests.post(f"{self.mcp_base_url}/tools/gpio/read", 
                                   json=data, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def call_ssh_exec(self, command, target="pi-lan", cwd=None):
        """Call SSH exec function"""
        data = {
            "target": target,
            "command": command
        }
        if cwd:
            data["cwd"] = cwd
            
        try:
            response = requests.post(f"{self.mcp_base_url}/tools/ssh_exec", 
                                   json=data, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def main():
    """Test the integration"""
    print("🔗 Testing MCP + Open WebUI Integration")
    print("=" * 50)
    
    integration = MCPOpenWebUIIntegration()
    
    # Test connection
    if integration.test_connection():
        print("✅ MCP Server connection successful")
    else:
        print("❌ MCP Server connection failed")
        return
    
    # Get available tools
    tools = integration.get_available_tools()
    if tools:
        print(f"✅ Found {len(tools.get('tools', []))} available tools")
    else:
        print("❌ Could not retrieve tools list")
        return
    
    # Test GPIO functions
    print("\n🧪 Testing GPIO Functions:")
    
    # Test GPIO write
    print("Testing GPIO write (pin 17, value 1)...")
    result = integration.call_gpio_write(17, 1)
    print(f"Result: {result}")
    
    # Test GPIO read
    print("Testing GPIO read (pin 17)...")
    result = integration.call_gpio_read(17)
    print(f"Result: {result}")
    
    # Test SSH exec
    print("Testing SSH exec (ls command)...")
    result = integration.call_ssh_exec("ls -la")
    print(f"Result: {result}")
    
    print("\n🎉 Integration test completed!")
    print("\n📋 Next steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Go to Settings → Connections")
    print("3. Add MCP server connection")
    print("4. Use the function calling features!")

if __name__ == "__main__":
    main()
