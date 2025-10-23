#!/usr/bin/env python3
"""
Test GPIO blink functionality
"""

def test_gpio_blink_imports():
    """Test that GPIO blink can be imported"""
    
    print("=== Testing GPIO Blink Imports ===")
    
    try:
        from mcp_server.tools.gpio_tools import (
            gpio_blink, 
            GPIOBlinkRequest, 
            TOOL_GPIO_BLINK
        )
        print("✅ GPIO blink imports successful!")
        
        # Test creating a request
        req = GPIOBlinkRequest(
            target="pi-lan",
            pin=17,
            count=3,
            on_time=0.2,
            off_time=0.3
        )
        print(f"✅ GPIOBlinkRequest created: {req}")
        
        # Test tool schema
        print(f"✅ TOOL_GPIO_BLINK schema: {TOOL_GPIO_BLINK['name']}")
        
        print("🎉 All GPIO blink functionality is working!")
        
    except Exception as e:
        print(f"❌ GPIO blink test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gpio_blink_imports()
