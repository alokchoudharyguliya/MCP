#!/usr/bin/env python3
"""
Test script to verify CORS and OpenAPI endpoint functionality
"""

import requests
import json

def test_openapi_endpoint(base_url="http://localhost:8000"):
    """Test the OpenAPI endpoint with CORS support"""
    try:
        print(f"🧪 Testing OpenAPI endpoint at {base_url}")
        
        # Test GET request to OpenAPI endpoint
        print("1. Testing GET /openapi.json...")
        response = requests.get(f"{base_url}/openapi.json")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ GET request successful")
            data = response.json()
            print(f"   📊 OpenAPI spec contains {len(data.get('paths', {}))} paths")
        else:
            print(f"   ❌ GET request failed: {response.text}")
            return False
        
        # Test OPTIONS request (CORS preflight)
        print("\n2. Testing OPTIONS /openapi.json...")
        response = requests.options(f"{base_url}/openapi.json")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ OPTIONS request successful")
            print(f"   📋 CORS headers: {dict(response.headers)}")
        else:
            print(f"   ❌ OPTIONS request failed: {response.text}")
            return False
        
        # Test root endpoint
        print("\n3. Testing GET /...")
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Root endpoint successful")
            data = response.json()
            print(f"   📋 Server info: {data.get('name', 'N/A')} v{data.get('version', 'N/A')}")
        else:
            print(f"   ❌ Root endpoint failed: {response.text}")
            return False
        
        print("\n🎉 All tests passed! OpenAPI endpoint is working correctly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {base_url}")
        print("   Make sure the server is running with: uvicorn mcp_server.main:app --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error testing OpenAPI: {e}")
        return False

if __name__ == "__main__":
    import sys
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = test_openapi_endpoint(base_url)
    sys.exit(0 if success else 1)
