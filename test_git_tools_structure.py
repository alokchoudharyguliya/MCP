#!/usr/bin/env python3
"""
Test script to verify git tools structure in MCP server
"""

import ast
import inspect

def test_git_tools_integration():
    """Test that git tools are properly integrated into the MCP server"""
    
    print("=== Testing Git Tools Integration ===")
    
    # Read the MCP server file
    with open('mcp_server/mcp_complete_server.py', 'r') as f:
        content = f.read()
    
    # Parse the file
    tree = ast.parse(content)
    
    # Check for git tool imports
    print("\n1. Checking imports...")
    git_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and 'git_tools' in node.module:
            for alias in node.names:
                git_imports.append(alias.name)
    
    print(f"Git tool imports found: {git_imports}")
    
    # Check for git tools in the tool list
    print("\n2. Checking tool definitions...")
    git_tools_in_list = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr == 'Tool':
            for keyword in node.keywords:
                if keyword.arg == 'name' and isinstance(keyword.value, ast.Constant):
                    tool_name = keyword.value.value
                    if 'git' in tool_name or tool_name == 'deploy_hook':
                        git_tools_in_list.append(tool_name)
    
    print(f"Git tools in tool list: {git_tools_in_list}")
    
    # Check for git tool handlers
    print("\n3. Checking tool handlers...")
    git_handlers = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('_handle_git'):
            git_handlers.append(node.name)
    
    print(f"Git tool handlers found: {git_handlers}")
    
    # Check for git tools in call_tool function
    print("\n4. Checking call_tool function...")
    git_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'call_tool':
            for child in ast.walk(node):
                if isinstance(child, ast.If) and hasattr(child.test, 'left') and hasattr(child.test.left, 'id'):
                    if child.test.left.id == 'name':
                        for comparison in child.test.comparators:
                            if isinstance(comparison, ast.Constant) and ('git' in comparison.value or comparison.value == 'deploy_hook'):
                                git_calls.append(comparison.value)
    
    print(f"Git tool calls in call_tool: {git_calls}")
    
    # Summary
    print("\n=== Summary ===")
    expected_git_tools = ['git_status', 'git_checkout', 'git_pull', 'deploy_hook']
    expected_handlers = ['_handle_git_status', '_handle_git_checkout', '_handle_git_pull', '_handle_deploy_hook']
    
    missing_tools = set(expected_git_tools) - set(git_tools_in_list)
    missing_handlers = set(expected_handlers) - set(git_handlers)
    missing_calls = set(expected_git_tools) - set(git_calls)
    
    if not missing_tools and not missing_handlers and not missing_calls:
        print("✅ All git tools are properly integrated!")
        print(f"   - Tools defined: {len(git_tools_in_list)}/{len(expected_git_tools)}")
        print(f"   - Handlers implemented: {len(git_handlers)}/{len(expected_handlers)}")
        print(f"   - Calls in call_tool: {len(git_calls)}/{len(expected_git_tools)}")
    else:
        print("❌ Some git tools are missing:")
        if missing_tools:
            print(f"   - Missing tools: {missing_tools}")
        if missing_handlers:
            print(f"   - Missing handlers: {missing_handlers}")
        if missing_calls:
            print(f"   - Missing calls: {missing_calls}")

if __name__ == "__main__":
    test_git_tools_integration()
