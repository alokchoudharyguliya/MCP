#!/usr/bin/env python3
"""
Run MCP server for Open WebUI integration
This script starts the MCP server and makes it accessible to Open WebUI
"""

import subprocess
import sys
import os
from pathlib import Path

def run_mcp_server():
    """Run the MCP server for Open WebUI integration"""
    
    print("🚀 Starting MCP Server for Open WebUI...")
    
    # Change to the project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    try:
        # Run the MCP server
        # You can choose between different server types:
        
        # Option 1: FastAPI server (for HTTP API access)
        print("Starting FastAPI MCP server...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "mcp_server.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        
        # Option 2: MCP stdio server (for direct MCP protocol)
        # subprocess.run([
        #     sys.executable, "-m", "mcp_server.mcp_complete_server"
        # ])
        
    except KeyboardInterrupt:
        print("\n🛑 MCP Server stopped")
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")

if __name__ == "__main__":
    run_mcp_server()
