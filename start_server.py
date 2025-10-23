#!/usr/bin/env python3
"""
Start the MCP server with OpenAPI support
"""

import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting MCP Pi Tool Server with OpenAPI support...")
    print("📋 Available endpoints:")
    print("   - http://localhost:8000/ (root)")
    print("   - http://localhost:8000/openapi.json (OpenAPI spec)")
    print("   - http://localhost:8000/docs (Swagger UI)")
    print("   - http://localhost:8000/redoc (ReDoc)")
    print("   - http://localhost:8000/health (health check)")
    print("   - http://localhost:8000/.well-known/mcp/tools (MCP tools)")
    print("\n🔧 OpenAPI tools can now connect to:")
    print("   URL: http://localhost:8000/openapi.json")
    print("   Type: OpenAPI")
    print()
    
    try:
        uvicorn.run(
            "mcp_server.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
