#!/usr/bin/env python3
"""
Simple verification that git tools are integrated into MCP server
"""

def verify_git_integration():
    """Verify git tools are properly integrated"""
    
    print("=== Verifying Git Tools Integration ===")
    
    # Read the MCP server file
    with open('mcp_server/mcp_complete_server.py', 'r') as f:
        content = f.read()
    
    # Check for key components
    checks = [
        ("Git tool imports", "from .tools.git_tools import"),
        ("Git status tool", 'name="git_status"'),
        ("Git checkout tool", 'name="git_checkout"'),
        ("Git pull tool", 'name="git_pull"'),
        ("Deploy hook tool", 'name="deploy_hook"'),
        ("Git status handler call", "elif name == \"git_status\":"),
        ("Git checkout handler call", "elif name == \"git_checkout\":"),
        ("Git pull handler call", "elif name == \"git_pull\":"),
        ("Deploy hook handler call", "elif name == \"deploy_hook\":"),
        ("Git status handler function", "async def _handle_git_status"),
        ("Git checkout handler function", "async def _handle_git_checkout"),
        ("Git pull handler function", "async def _handle_git_pull"),
        ("Deploy hook handler function", "async def _handle_deploy_hook"),
    ]
    
    results = []
    for check_name, search_term in checks:
        found = search_term in content
        results.append((check_name, found))
        status = "✅" if found else "❌"
        print(f"{status} {check_name}")
    
    # Summary
    passed = sum(1 for _, found in results if found)
    total = len(results)
    
    print(f"\n=== Summary ===")
    print(f"Passed: {passed}/{total} checks")
    
    if passed == total:
        print("🎉 All git tools are properly integrated into the MCP server!")
        print("\nAvailable git tools for Claude Desktop:")
        print("  - git_status: Get git repository status")
        print("  - git_checkout: Checkout a branch or tag")
        print("  - git_pull: Pull latest changes")
        print("  - deploy_hook: Execute deployment hook")
    else:
        print("⚠️  Some git tools may not be properly integrated.")
        missing = [name for name, found in results if not found]
        print(f"Missing: {missing}")

if __name__ == "__main__":
    verify_git_integration()
