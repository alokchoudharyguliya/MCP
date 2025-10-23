#!/usr/bin/env python3
"""
Test script for the FastAPI server with authentication
"""

import requests
import json

# Server configuration
BASE_URL = "http://localhost:8000"
API_KEY = "replace-with-a-long-random-api-key"  # From policies.yaml

def test_public_endpoints():
    """Test endpoints that don't require authentication"""
    print("=== Testing Public Endpoints ===")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health endpoint error: {e}")
    
    # Test docs endpoint
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Docs endpoint: {response.status_code}")
    except Exception as e:
        print(f"Docs endpoint error: {e}")

def test_authenticated_endpoints():
    """Test endpoints that require authentication"""
    print("\n=== Testing Authenticated Endpoints ===")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test tools listing
    try:
        response = requests.get(f"{BASE_URL}/.well-known/mcp/tools", headers=headers)
        print(f"Tools endpoint: {response.status_code}")
        if response.status_code == 200:
            tools = response.json()
            print(f"Available tools: {[tool['name'] for tool in tools['tools']]}")
    except Exception as e:
        print(f"Tools endpoint error: {e}")
    
    # Test SSH exec (this will fail if no targets configured, but we can test auth)
    try:
        payload = {
            "name": "ssh_exec",
            "arguments": {
                "target": "test-target",
                "command": "echo 'Hello World'"
            }
        }
        response = requests.post(f"{BASE_URL}/tools", json=payload, headers=headers)
        print(f"SSH exec endpoint: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"SSH exec endpoint error: {e}")

def test_unauthorized_access():
    """Test that unauthorized access is blocked"""
    print("\n=== Testing Unauthorized Access ===")
    
    # Test without auth header
    try:
        response = requests.get(f"{BASE_URL}/.well-known/mcp/tools")
        print(f"Unauthorized access: {response.status_code}")
        if response.status_code == 401:
            print("✓ Authentication correctly required")
        else:
            print("✗ Authentication not enforced")
    except Exception as e:
        print(f"Unauthorized test error: {e}")

if __name__ == "__main__":
    print("Testing FastAPI Server with Authentication")
    print("=" * 50)
    
    test_public_endpoints()
    test_authenticated_endpoints()
    test_unauthorized_access()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print(f"\nTo access the API documentation, visit: {BASE_URL}/docs")
    print(f"To use the API, include this header: Authorization: Bearer {API_KEY}")
