#!/usr/bin/env python3
"""
Test script to verify OpenAPI endpoint functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_server'))

from mcp_server.main import app
import json

def test_openapi():
    """Test the OpenAPI specification generation"""
    try:
        # Generate OpenAPI spec
        spec = app.openapi()
        
        print("✅ OpenAPI spec generated successfully")
        print(f"📋 Title: {spec.get('info', {}).get('title', 'N/A')}")
        print(f"🔢 Version: {spec.get('info', {}).get('version', 'N/A')}")
        print(f"🛣️  Paths count: {len(spec.get('paths', {}))}")
        
        # Check for key endpoints
        paths = spec.get('paths', {})
        key_endpoints = ['/openapi.json', '/', '/health', '/.well-known/mcp/tools']
        
        print("\n🔍 Checking key endpoints:")
        for endpoint in key_endpoints:
            if endpoint in paths:
                print(f"  ✅ {endpoint}")
            else:
                print(f"  ❌ {endpoint}")
        
        # Check for tool endpoints
        tool_endpoints = [path for path in paths.keys() if path.startswith('/tools/')]
        print(f"\n🔧 Tool endpoints found: {len(tool_endpoints)}")
        for endpoint in tool_endpoints[:5]:  # Show first 5
            print(f"  - {endpoint}")
        if len(tool_endpoints) > 5:
            print(f"  ... and {len(tool_endpoints) - 5} more")
        
        # Test the actual endpoint
        print("\n🧪 Testing /openapi.json endpoint:")
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/openapi.json")
        
        if response.status_code == 200:
            print("  ✅ /openapi.json returns 200 OK")
            data = response.json()
            print(f"  📊 Response contains {len(data.get('paths', {}))} paths")
        else:
            print(f"  ❌ /openapi.json returned {response.status_code}")
            
        print("\n🎉 OpenAPI integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenAPI: {e}")
        return False

if __name__ == "__main__":
    success = test_openapi()
    sys.exit(0 if success else 1)
