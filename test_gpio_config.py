#!/usr/bin/env python3
"""
Test GPIO configuration loading
"""

def test_gpio_config():
    """Test that GPIO configuration loads properly"""
    
    print("=== Testing GPIO Configuration ===")
    
    try:
        # Load policies (GPIO config only, security policies disabled)
        from mcp_server.config import load_policies
        policies = load_policies()
        
        print(f"Policies loaded: {type(policies)}")
        print(f"Has gpio attribute: {hasattr(policies, 'gpio')}")
        
        if hasattr(policies, 'gpio'):
            print(f"GPIO config: {policies.gpio}")
            print(f"GPIO targets: {getattr(policies.gpio, 'targets', 'No targets')}")
        
        # Test GPIO policy loading
        from mcp_server.tools.gpio_tools import _get_gpio_policy
        gpio_policy = _get_gpio_policy("pi-lan")
        print(f"GPIO policy for pi-lan: {gpio_policy}")
        
        print("✅ GPIO configuration test passed!")
        
    except Exception as e:
        print(f"❌ GPIO configuration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gpio_config()
