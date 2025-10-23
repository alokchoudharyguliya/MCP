#!/usr/bin/env python3
"""
Test script to verify no authentication is required
"""

import requests
import json

def test_no_auth():
    """Test that all endpoints work without authentication"""
    
    base_url = "http://localhost:8000"
    
    print("=== Testing No Authentication Required ===")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health error: {e}")
    
    # Test tool listing
    print("\n2. Testing tool listing...")
    try:
        response = requests.get(f"{base_url}/.well-known/mcp/tools")
        print(f"Tools: {response.status_code}")
        if response.status_code == 200:
            tools = response.json()
            print(f"Found {len(tools.get('tools', []))} tools")
    except Exception as e:
        print(f"Tools error: {e}")
    
    # Test GPIO write
    print("\n3. Testing GPIO write...")
    try:
        data = {
            "target": "pi-lan",
            "pin": 17,
            "value": 1,
            "mode": "BCM"
        }
        response = requests.post(f"{base_url}/tools/gpio/write", json=data)
        print(f"GPIO Write: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"GPIO write error: {e}")
    
    # Test SSH exec
    print("\n4. Testing SSH exec...")
    try:
        data = {
            "target": "pi-lan",
            "command": "echo hello"
        }
        response = requests.post(f"{base_url}/tools/ssh_exec", json=data)
        print(f"SSH Exec: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"SSH exec error: {e}")
    
    print("\n=== Test Complete ===")
    print("If all tests show 200 status codes, authentication is disabled!")

if __name__ == "__main__":
    test_no_auth()
