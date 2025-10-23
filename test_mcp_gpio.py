#!/usr/bin/env python3
"""
Test MCP GPIO tools integration
"""

import asyncio
import json
from mcp_server.mcp_complete_server import server

async def test_mcp_gpio_tools():
    """Test all GPIO tools in MCP server"""
    
    print("=== Testing MCP GPIO Tools ===")
    
    try:
        # Test listing tools
        print("\n1. Testing tool listing...")
        tools = await server.list_tools()
        gpio_tools = [t for t in tools if t.name.startswith('gpio')]
        print(f"Found {len(gpio_tools)} GPIO tools:")
        for tool in gpio_tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test GPIO write
        print("\n2. Testing GPIO write...")
        write_args = {
            "target": "pi-lan",
            "pin": 17,
            "value": 1,
            "mode": "BCM"
        }
        try:
            result = await server.call_tool("gpio_write", write_args)
            print(f"GPIO Write Result: {result[0].text if result else 'No result'}")
        except Exception as e:
            print(f"GPIO Write Error: {e}")
        
        # Test GPIO read
        print("\n3. Testing GPIO read...")
        read_args = {
            "target": "pi-lan",
            "pin": 17,
            "mode": "BCM"
        }
        try:
            result = await server.call_tool("gpio_read", read_args)
            print(f"GPIO Read Result: {result[0].text if result else 'No result'}")
        except Exception as e:
            print(f"GPIO Read Error: {e}")
        
        # Test GPIO PWM
        print("\n4. Testing GPIO PWM...")
        pwm_args = {
            "target": "pi-lan",
            "pin": 18,
            "duty": 50.0,
            "freq": 1000.0,
            "duration": 1.0,
            "mode": "BCM"
        }
        try:
            result = await server.call_tool("gpio_pwm", pwm_args)
            print(f"GPIO PWM Result: {result[0].text if result else 'No result'}")
        except Exception as e:
            print(f"GPIO PWM Error: {e}")
        
        # Test GPIO blink
        print("\n5. Testing GPIO blink...")
        blink_args = {
            "target": "pi-lan",
            "pin": 17,
            "count": 3,
            "on_time": 0.2,
            "off_time": 0.3,
            "mode": "BCM"
        }
        try:
            result = await server.call_tool("gpio_blink", blink_args)
            print(f"GPIO Blink Result: {result[0].text if result else 'No result'}")
        except Exception as e:
            print(f"GPIO Blink Error: {e}")
        
        # Test GPIO macro
        print("\n6. Testing GPIO macro...")
        macro_args = {
            "target": "pi-lan",
            "steps": [
                {
                    "op": "write",
                    "data": {"pin": 17, "value": 1, "mode": "BCM"}
                },
                {
                    "op": "blink",
                    "data": {"pin": 18, "count": 2, "on_time": 0.1, "off_time": 0.1, "mode": "BCM"}
                },
                {
                    "op": "write",
                    "data": {"pin": 17, "value": 0, "mode": "BCM"}
                }
            ],
            "mode": "BCM"
        }
        try:
            result = await server.call_tool("macro_run", macro_args)
            print(f"GPIO Macro Result: {result[0].text if result else 'No result'}")
        except Exception as e:
            print(f"GPIO Macro Error: {e}")
        
        print("\n✅ MCP GPIO tools test completed!")
        
    except Exception as e:
        print(f"❌ MCP GPIO test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_gpio_tools())
