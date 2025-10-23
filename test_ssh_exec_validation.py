#!/usr/bin/env python3
"""
Test script to demonstrate ssh_exec validation and proper usage
"""

import requests
import json

def test_ssh_exec_validation(base_url="http://localhost:8000"):
    """Test ssh_exec tool with various request scenarios"""
    
    print("🧪 Testing ssh_exec validation...")
    
    # Test cases
    test_cases = [
        {
            "name": "Empty request (should fail)",
            "data": {},
            "expected_status": 400
        },
        {
            "name": "Missing target (should fail)", 
            "data": {"command": "ls -la"},
            "expected_status": 400
        },
        {
            "name": "Missing command (should fail)",
            "data": {"target": "pi-lan"},
            "expected_status": 400
        },
        {
            "name": "Valid request (should work)",
            "data": {"target": "pi-lan", "command": "echo 'Hello World'"},
            "expected_status": 200
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Data: {test_case['data']}")
        
        try:
            response = requests.post(
                f"{base_url}/tools",
                json={
                    "name": "ssh_exec",
                    "arguments": test_case["data"]
                },
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == test_case["expected_status"]:
                print("   ✅ Expected result")
            else:
                print(f"   ❌ Expected {test_case['expected_status']}, got {response.status_code}")
            
            # Show response details
            try:
                response_data = response.json()
                if "detail" in response_data:
                    print(f"   Message: {response_data['detail']}")
                elif "error" in response_data:
                    print(f"   Error: {response_data['error']}")
            except:
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Could not connect to server")
            print("   Make sure server is running: python start_server.py")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n📋 Proper ssh_exec usage examples:")
    examples = [
        {
            "description": "Basic command execution",
            "request": {
                "name": "ssh_exec",
                "arguments": {
                    "target": "pi-lan",
                    "command": "ls -la /home/pi"
                }
            }
        },
        {
            "description": "Command with working directory",
            "request": {
                "name": "ssh_exec", 
                "arguments": {
                    "target": "pi-lan",
                    "command": "pwd",
                    "cwd": "/home/pi/project"
                }
            }
        },
        {
            "description": "Command with environment variables",
            "request": {
                "name": "ssh_exec",
                "arguments": {
                    "target": "pi-lan",
                    "command": "echo $MY_VAR",
                    "env": {"MY_VAR": "Hello from MCP"}
                }
            }
        }
    ]
    
    for example in examples:
        print(f"\n   {example['description']}:")
        print(f"   {json.dumps(example['request'], indent=6)}")
    
    return True

if __name__ == "__main__":
    import sys
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_ssh_exec_validation(base_url)
