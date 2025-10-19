# # """
# # MCP File System Server Implementation
# # Allows Claude to read/write files and traverse directories through MCP
# # """

# # import os
# # import json
# # from pathlib import Path
# # from typing import Any, Optional
# # from mcp.server import Server
# # from mcp.types import Tool, TextContent, Resource
# # import mcp.types as types

# # # Initialize MCP Server
# # server = Server("filesystem-mcp")

# # # Define allowed base directories (security: restrict access)
# # ALLOWED_BASE_PATHS = [
# #     "C:\\Users\\alok4\\Desktop\\test_files",
# #     "C:\\Users\\alok4\\Documents",
# #     "C:\\Users\\alok4\\Desktop"
# # ]

# # def is_path_allowed(file_path: str) -> bool:
# #     """Check if path is within allowed directories"""
# #     resolved_path = Path(file_path).resolve()
# #     return any(resolved_path.is_relative_to(Path(base).resolve()) 
# #                for base in ALLOWED_BASE_PATHS)

# # # ============ TOOLS DEFINITIONS ============

# # @server.call_tool()
# # async def handle_tool_call(name: str, arguments: dict) -> Any:
# #     """Handle tool calls from Claude"""
    
# #     if name == "read_file":
# #         return read_file(arguments["path"])
# #     elif name == "write_file":
# #         return write_file(arguments["path"], arguments["content"])
# #     elif name == "list_directory":
# #         return list_directory(arguments["path"])
# #     elif name == "create_directory":
# #         return create_directory(arguments["path"])
# #     elif name == "delete_file":
# #         return delete_file(arguments["path"])
# #     elif name == "file_info":
# #         return get_file_info(arguments["path"])
# #     else:
# #         return {"error": f"Unknown tool: {name}"}

# # # ============ IMPLEMENTATION FUNCTIONS ============

# # def read_file(file_path: str) -> dict:
# #     """Read file contents"""
# #     try:
# #         if not is_path_allowed(file_path):
# #             return {"error": f"Access denied: {file_path}"}
        
# #         path = Path(file_path)
        
# #         if not path.exists():
# #             return {"error": f"File not found: {file_path}"}
        
# #         if path.is_dir():
# #             return {"error": f"Path is a directory, not a file: {file_path}"}
        
# #         # Read file
# #         with open(path, 'r', encoding='utf-8') as f:
# #             content = f.read()
        
# #         return {
# #             "success": True,
# #             "path": str(path),
# #             "size": path.stat().st_size,
# #             "content": content
# #         }
# #     except Exception as e:
# #         return {"error": str(e)}


# # def write_file(file_path: str, content: str) -> dict:
# #     """Write content to file"""
# #     try:
# #         if not is_path_allowed(file_path):
# #             return {"error": f"Access denied: {file_path}"}
        
# #         path = Path(file_path)
        
# #         # Create parent directories if needed
# #         path.parent.mkdir(parents=True, exist_ok=True)
        
# #         # Write file
# #         with open(path, 'w', encoding='utf-8') as f:
# #             f.write(content)
        
# #         return {
# #             "success": True,
# #             "path": str(path),
# #             "bytes_written": len(content),
# #             "message": f"File written successfully"
# #         }
# #     except Exception as e:
# #         return {"error": str(e)}


# # def list_directory(dir_path: str) -> dict:
# #     """List files and directories"""
# #     try:
# #         if not is_path_allowed(dir_path):
# #             return {"error": f"Access denied: {dir_path}"}
        
# #         path = Path(dir_path)
        
# #         if not path.exists():
# #             return {"error": f"Directory not found: {dir_path}"}
        
# #         if not path.is_dir():
# #             return {"error": f"Path is not a directory: {dir_path}"}
        
# #         items = []
# #         for item in sorted(path.iterdir()):
# #             stat = item.stat()
# #             items.append({
# #                 "name": item.name,
# #                 "type": "directory" if item.is_dir() else "file",
# #                 "size": stat.st_size if item.is_file() else None,
# #                 "path": str(item)
# #             })
        
# #         return {
# #             "success": True,
# #             "path": str(path),
# #             "items": items,
# #             "count": len(items)
# #         }
# #     except Exception as e:
# #         return {"error": str(e)}


# # def create_directory(dir_path: str) -> dict:
# #     """Create directory"""
# #     try:
# #         if not is_path_allowed(dir_path):
# #             return {"error": f"Access denied: {dir_path}"}
        
# #         path = Path(dir_path)
        
# #         if path.exists():
# #             return {"error": f"Directory already exists: {dir_path}"}
        
# #         path.mkdir(parents=True, exist_ok=True)
        
# #         return {
# #             "success": True,
# #             "path": str(path),
# #             "message": "Directory created successfully"
# #         }
# #     except Exception as e:
# #         return {"error": str(e)}


# # def delete_file(file_path: str) -> dict:
# #     """Delete file"""
# #     try:
# #         if not is_path_allowed(file_path):
# #             return {"error": f"Access denied: {file_path}"}
        
# #         path = Path(file_path)
        
# #         if not path.exists():
# #             return {"error": f"File not found: {file_path}"}
        
# #         if path.is_dir():
# #             return {"error": f"Path is a directory. Use directory deletion for directories: {file_path}"}
        
# #         path.unlink()
        
# #         return {
# #             "success": True,
# #             "path": str(path),
# #             "message": "File deleted successfully"
# #         }
# #     except Exception as e:
# #         return {"error": str(e)}


# # def get_file_info(file_path: str) -> dict:
# #     """Get file metadata"""
# #     try:
# #         if not is_path_allowed(file_path):
# #             return {"error": f"Access denied: {file_path}"}
        
# #         path = Path(file_path)
        
# #         if not path.exists():
# #             return {"error": f"File not found: {file_path}"}
        
# #         stat = path.stat()
        
# #         return {
# #             "success": True,
# #             "path": str(path),
# #             "type": "directory" if path.is_dir() else "file",
# #             "size": stat.st_size,
# #             "created": stat.st_ctime,
# #             "modified": stat.st_mtime,
# #             "is_readable": os.access(path, os.R_OK),
# #             "is_writable": os.access(path, os.W_OK)
# #         }
# #     except Exception as e:
# #         return {"error": str(e)}


# # # ============ REGISTER TOOLS ============

# # # Tool definitions to expose to Claude
# # tools = [
# #     Tool(
# #         name="read_file",
# #         description="Read the contents of a file",
# #         inputSchema={
# #             "type": "object",
# #             "properties": {
# #                 "path": {
# #                     "type": "string",
# #                     "description": "Path to the file to read"
# #                 }
# #             },
# #             "required": ["path"]
# #         }
# #     ),
# #     Tool(
# #         name="write_file",
# #         description="Write content to a file (creates if doesn't exist)",
# #         inputSchema={
# #             "type": "object",
# #             "properties": {
# #                 "path": {
# #                     "type": "string",
# #                     "description": "Path to the file to write"
# #                 },
# #                 "content": {
# #                     "type": "string",
# #                     "description": "Content to write to file"
# #                 }
# #             },
# #             "required": ["path", "content"]
# #         }
# #     ),
# #     Tool(
# #         name="list_directory",
# #         description="List files and directories in a path",
# #         inputSchema={
# #             "type": "object",
# #             "properties": {
# #                 "path": {
# #                     "type": "string",
# #                     "description": "Directory path to list"
# #                 }
# #             },
# #             "required": ["path"]
# #         }
# #     ),
# #     Tool(
# #         name="create_directory",
# #         description="Create a new directory",
# #         inputSchema={
# #             "type": "object",
# #             "properties": {
# #                 "path": {
# #                     "type": "string",
# #                     "description": "Path for new directory"
# #                 }
# #             },
# #             "required": ["path"]
# #         }
# #     ),
# #     Tool(
# #         name="delete_file",
# #         description="Delete a file",
# #         inputSchema={
# #             "type": "object",
# #             "properties": {
# #                 "path": {
# #                     "type": "string",
# #                     "description": "Path to file to delete"
# #                 }
# #             },
# #             "required": ["path"]
# #         }
# #     ),
# #     Tool(
# #         name="file_info",
# #         description="Get file metadata (size, created date, etc)",
# #         inputSchema={
# #             "type": "object",
# #             "properties": {
# #                 "path": {
# #                     "type": "string",
# #                     "description": "Path to file"
# #                 }
# #             },
# #             "required": ["path"]
# #         }
# #     )
# # ]

# # @server.list_tools()
# # async def list_tools() -> list[Tool]:
# #     """List available tools"""
# #     return tools


# # # ============ USAGE EXAMPLES ============

# # """
# # How Claude would use this:

# # 1. LIST DIRECTORY:
# #    User: "What files are in my documents folder?"
# #    Claude calls: list_directory("/home/user/documents")
   
# # 2. READ FILE:
# #    User: "Read my budget.txt file"
# #    Claude calls: read_file("/home/user/documents/budget.txt")
   
# # 3. WRITE FILE:
# #    User: "Create a meeting notes file with today's discussion"
# #    Claude calls: write_file("/home/user/documents/meeting_notes.txt", "...")
   
# # 4. CREATE DIRECTORY:
# #    User: "Create a new project folder called 'Q1-Planning'"
# #    Claude calls: create_directory("/home/user/projects/Q1-Planning")
   
# # 5. DELETE FILE:
# #    User: "Delete the old draft file"
# #    Claude calls: delete_file("/home/user/documents/old_draft.txt")
   
# # 6. FILE INFO:
# #    User: "When was my main report last modified?"
# #    Claude calls: file_info("/home/user/documents/report.pdf")
# # """


# # # ============ START SERVER ============

# # if __name__ == "__main__":
# #     # Start the MCP server
# #     # This would typically be started by the MCP host (Claude client)
# #     print("File System MCP Server initialized")
# #     print(f"Allowed paths: {ALLOWED_BASE_PATHS}")
# #     print(f"Available tools: {[t.name for t in tools]}")


# """
# MCP File System Server Implementation
# Simple version that stays running and doesn't crash
# """

# import os
# import sys
# import json
# import traceback
# from pathlib import Path
# from typing import Any

# # Define allowed base directories (security: restrict access)
# ALLOWED_BASE_PATHS = [
#     "C:\\Users\\alok4\\Desktop\\test_files",
#     "C:\\Users\\alok4\\Documents",
#     "C:\\Users\\alok4\\Desktop"
# ]

# def log_error(msg):
#     """Log errors to console"""
#     print(f"ERROR: {msg}", file=sys.stderr)
#     sys.stderr.flush()

# def log_info(msg):
#     """Log info to console"""
#     print(f"INFO: {msg}", file=sys.stderr)
#     sys.stderr.flush()

# def is_path_allowed(file_path: str) -> bool:
#     """Check if path is within allowed directories"""
#     try:
#         resolved_path = Path(file_path).resolve()
#         for base in ALLOWED_BASE_PATHS:
#             try:
#                 base_resolved = Path(base).resolve()
#                 resolved_path.relative_to(base_resolved)
#                 return True
#             except ValueError:
#                 continue
#         return False
#     except Exception as e:
#         log_error(f"Error checking path: {e}")
#         return False

# # ============ TOOL IMPLEMENTATIONS ============

# def read_file(file_path: str) -> dict:
#     """Read file contents"""
#     try:
#         if not is_path_allowed(file_path):
#             return {"error": f"Access denied: {file_path}"}
        
#         path = Path(file_path)
        
#         if not path.exists():
#             return {"error": f"File not found: {file_path}"}
        
#         if path.is_dir():
#             return {"error": f"Path is a directory, not a file: {file_path}"}
        
#         with open(path, 'r', encoding='utf-8') as f:
#             content = f.read()
        
#         return {
#             "success": True,
#             "path": str(path),
#             "size": path.stat().st_size,
#             "content": content
#         }
#     except Exception as e:
#         return {"error": f"Failed to read file: {str(e)}"}

# def write_file(file_path: str, content: str) -> dict:
#     """Write content to file"""
#     try:
#         if not is_path_allowed(file_path):
#             return {"error": f"Access denied: {file_path}"}
        
#         path = Path(file_path)
#         path.parent.mkdir(parents=True, exist_ok=True)
        
#         with open(path, 'w', encoding='utf-8') as f:
#             f.write(content)
        
#         return {
#             "success": True,
#             "path": str(path),
#             "bytes_written": len(content),
#             "message": f"File written successfully"
#         }
#     except Exception as e:
#         return {"error": f"Failed to write file: {str(e)}"}

# def list_directory(dir_path: str) -> dict:
#     """List files and directories"""
#     try:
#         if not is_path_allowed(dir_path):
#             return {"error": f"Access denied: {dir_path}"}
        
#         path = Path(dir_path)
        
#         if not path.exists():
#             return {"error": f"Directory not found: {dir_path}"}
        
#         if not path.is_dir():
#             return {"error": f"Path is not a directory: {dir_path}"}
        
#         items = []
#         for item in sorted(path.iterdir()):
#             try:
#                 stat = item.stat()
#                 items.append({
#                     "name": item.name,
#                     "type": "directory" if item.is_dir() else "file",
#                     "size": stat.st_size if item.is_file() else None,
#                     "path": str(item)
#                 })
#             except Exception:
#                 continue
        
#         return {
#             "success": True,
#             "path": str(path),
#             "items": items,
#             "count": len(items)
#         }
#     except Exception as e:
#         return {"error": f"Failed to list directory: {str(e)}"}

# def create_directory(dir_path: str) -> dict:
#     """Create directory"""
#     try:
#         if not is_path_allowed(dir_path):
#             return {"error": f"Access denied: {dir_path}"}
        
#         path = Path(dir_path)
        
#         if path.exists():
#             return {"error": f"Directory already exists: {dir_path}"}
        
#         path.mkdir(parents=True, exist_ok=True)
        
#         return {
#             "success": True,
#             "path": str(path),
#             "message": "Directory created successfully"
#         }
#     except Exception as e:
#         return {"error": f"Failed to create directory: {str(e)}"}

# def delete_file(file_path: str) -> dict:
#     """Delete file"""
#     try:
#         if not is_path_allowed(file_path):
#             return {"error": f"Access denied: {file_path}"}
        
#         path = Path(file_path)
        
#         if not path.exists():
#             return {"error": f"File not found: {file_path}"}
        
#         if path.is_dir():
#             return {"error": f"Path is a directory. Use directory deletion for directories: {file_path}"}
        
#         path.unlink()
        
#         return {
#             "success": True,
#             "path": str(path),
#             "message": "File deleted successfully"
#         }
#     except Exception as e:
#         return {"error": f"Failed to delete file: {str(e)}"}

# def get_file_info(file_path: str) -> dict:
#     """Get file metadata"""
#     try:
#         if not is_path_allowed(file_path):
#             return {"error": f"Access denied: {file_path}"}
        
#         path = Path(file_path)
        
#         if not path.exists():
#             return {"error": f"File not found: {file_path}"}
        
#         stat = path.stat()
        
#         return {
#             "success": True,
#             "path": str(path),
#             "type": "directory" if path.is_dir() else "file",
#             "size": stat.st_size,
#             "created": stat.st_ctime,
#             "modified": stat.st_mtime,
#             "is_readable": os.access(path, os.R_OK),
#             "is_writable": os.access(path, os.W_OK)
#         }
#     except Exception as e:
#         return {"error": f"Failed to get file info: {str(e)}"}

# # ============ TOOL REGISTRY ============

# TOOLS = {
#     "read_file": read_file,
#     "write_file": write_file,
#     "list_directory": list_directory,
#     "create_directory": create_directory,
#     "delete_file": delete_file,
#     "file_info": get_file_info
# }

# TOOL_DEFINITIONS = [
#     {
#         "name": "read_file",
#         "description": "Read the contents of a file",
#         "inputSchema": {
#             "type": "object",
#             "properties": {
#                 "path": {"type": "string", "description": "Path to the file to read"}
#             },
#             "required": ["path"]
#         }
#     },
#     {
#         "name": "write_file",
#         "description": "Write content to a file (creates if doesn't exist)",
#         "inputSchema": {
#             "type": "object",
#             "properties": {
#                 "path": {"type": "string", "description": "Path to the file to write"},
#                 "content": {"type": "string", "description": "Content to write to file"}
#             },
#             "required": ["path", "content"]
#         }
#     },
#     {
#         "name": "list_directory",
#         "description": "List files and directories in a path",
#         "inputSchema": {
#             "type": "object",
#             "properties": {
#                 "path": {"type": "string", "description": "Directory path to list"}
#             },
#             "required": ["path"]
#         }
#     },
#     {
#         "name": "create_directory",
#         "description": "Create a new directory",
#         "inputSchema": {
#             "type": "object",
#             "properties": {
#                 "path": {"type": "string", "description": "Path for new directory"}
#             },
#             "required": ["path"]
#         }
#     },
#     {
#         "name": "delete_file",
#         "description": "Delete a file",
#         "inputSchema": {
#             "type": "object",
#             "properties": {
#                 "path": {"type": "string", "description": "Path to file to delete"}
#             },
#             "required": ["path"]
#         }
#     },
#     {
#         "name": "file_info",
#         "description": "Get file metadata (size, created date, etc)",
#         "inputSchema": {
#             "type": "object",
#             "properties": {
#                 "path": {"type": "string", "description": "Path to file"}
#             },
#             "required": ["path"]
#         }
#     }
# ]

# # ============ MCP PROTOCOL HANDLER ============

# def process_request(request: dict) -> dict:
#     """Process MCP JSON-RPC request"""
#     try:
#         jsonrpc = request.get("jsonrpc", "2.0")
#         method = request.get("method")
#         params = request.get("params", {})
#         req_id = request.get("id")
        
#         if method == "initialize":
#             return {
#                 "jsonrpc": jsonrpc,
#                 "id": req_id,
#                 "result": {
#                     "protocolVersion": "2024-11-05",
#                     "capabilities": {},
#                     "serverInfo": {
#                         "name": "filesystem-mcp",
#                         "version": "1.0.0"
#                     }
#                 }
#             }
        
#         elif method == "tools/list":
#             return {
#                 "jsonrpc": jsonrpc,
#                 "id": req_id,
#                 "result": {"tools": TOOL_DEFINITIONS}
#             }
        
#         elif method == "tools/call":
#             tool_name = params.get("name")
#             tool_args = params.get("arguments", {})
            
#             if tool_name not in TOOLS:
#                 return {
#                     "jsonrpc": jsonrpc,
#                     "id": req_id,
#                     "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
#                 }
            
#             result = TOOLS[tool_name](**tool_args)
            
#             return {
#                 "jsonrpc": jsonrpc,
#                 "id": req_id,
#                 "result": result
#             }
        
#         else:
#             return {
#                 "jsonrpc": jsonrpc,
#                 "id": req_id,
#                 "error": {"code": -32601, "message": f"Unknown method: {method}"}
#             }
    
#     except Exception as e:
#         log_error(f"Error processing request: {e}\n{traceback.format_exc()}")
#         return {
#             "jsonrpc": "2.0",
#             "id": request.get("id"),
#             "error": {"code": -32603, "message": str(e)}
#         }

# # ============ MAIN LOOP ============

# def main():
#     """Main server loop - read from stdin, process, write to stdout"""
#     log_info("File System MCP Server started")
#     log_info(f"Allowed paths: {ALLOWED_BASE_PATHS}")
#     log_info(f"Available tools: {list(TOOLS.keys())}")
    
#     try:
#         while True:
#             try:
#                 # Read line from stdin
#                 line = sys.stdin.readline()
                
#                 if not line:
#                     log_info("EOF reached, exiting")
#                     break
                
#                 line = line.strip()
#                 if not line:
#                     continue
                
#                 # Parse JSON request
#                 request = json.loads(line)
                
#                 # Process request
#                 response = process_request(request)
                
#                 # Send JSON response
#                 print(json.dumps(response))
#                 sys.stdout.flush()
            
#             except json.JSONDecodeError as e:
#                 log_error(f"Invalid JSON: {e}")
#                 error_response = {
#                     "jsonrpc": "2.0",
#                     "error": {"code": -32700, "message": "Parse error"}
#                 }
#                 print(json.dumps(error_response))
#                 sys.stdout.flush()
            
#             except Exception as e:
#                 log_error(f"Unexpected error: {e}\n{traceback.format_exc()}")
    
#     except KeyboardInterrupt:
#         log_info("Server interrupted by user")
#     except Exception as e:
#         log_error(f"Fatal error: {e}\n{traceback.format_exc()}")
#     finally:
#         log_info("Server shutting down")

# if __name__ == "__main__":
#     main()

"""
File System MCP Server Implementation using FastMCP
Allows Claude to read/write files and traverse directories
"""

import os
from pathlib import Path
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("filesystem-mcp")

# Define allowed base directories (security: restrict access)
ALLOWED_BASE_PATHS = [
    "C:\\Users\\alok4\\Desktop\\test_files",
    "C:\\Users\\alok4/Desktop",
    "C:\\Users\\alok4\\OneDrive\\Documents",  # Add this if using OneDrive
]

def is_path_allowed(file_path: str) -> bool:
    """Check if path is within allowed directories"""
    try:
        resolved_path = Path(file_path).resolve()
        for base in ALLOWED_BASE_PATHS:
            try:
                base_resolved = Path(base).resolve()
                resolved_path.relative_to(base_resolved)
                return True
            except ValueError:
                continue
        return False
    except Exception as e:
        return False

# ============ TOOL IMPLEMENTATIONS ============

@mcp.tool()
def read_file(path: str) -> dict:
    """Read the contents of a file
    
    Args:
        path: Path to the file to read
    """
    try:
        if not is_path_allowed(path):
            return {"error": f"Access denied: {path}"}
        
        file_path = Path(path)
        
        if not file_path.exists():
            return {"error": f"File not found: {path}"}
        
        if file_path.is_dir():
            return {"error": f"Path is a directory, not a file: {path}"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "path": str(file_path),
            "size": file_path.stat().st_size,
            "content": content
        }
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}


@mcp.tool()
def write_file(path: str, content: str) -> dict:
    """Write content to a file (creates if doesn't exist)
    
    Args:
        path: Path to the file to write
        content: Content to write to file
    """
    try:
        if not is_path_allowed(path):
            return {"error": f"Access denied: {path}"}
        
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "path": str(file_path),
            "bytes_written": len(content),
            "message": "File written successfully"
        }
    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}


@mcp.tool()
def list_directory(path: str) -> dict:
    """List files and directories in a path
    
    Args:
        path: Directory path to list
    """
    try:
        if not is_path_allowed(path):
            return {"error": f"Access denied: {path}"}
        
        dir_path = Path(path)
        
        if not dir_path.exists():
            return {"error": f"Directory not found: {path}"}
        
        if not dir_path.is_dir():
            return {"error": f"Path is not a directory: {path}"}
        
        items = []
        for item in sorted(dir_path.iterdir()):
            try:
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "path": str(item)
                })
            except Exception:
                continue
        
        return {
            "success": True,
            "path": str(dir_path),
            "items": items,
            "count": len(items)
        }
    except Exception as e:
        return {"error": f"Failed to list directory: {str(e)}"}


@mcp.tool()
def create_directory(path: str) -> dict:
    """Create a new directory
    
    Args:
        path: Path for new directory
    """
    try:
        if not is_path_allowed(path):
            return {"error": f"Access denied: {path}"}
        
        dir_path = Path(path)
        
        if dir_path.exists():
            return {"error": f"Directory already exists: {path}"}
        
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "path": str(dir_path),
            "message": "Directory created successfully"
        }
    except Exception as e:
        return {"error": f"Failed to create directory: {str(e)}"}


@mcp.tool()
def delete_file(path: str) -> dict:
    """Delete a file
    
    Args:
        path: Path to file to delete
    """
    try:
        if not is_path_allowed(path):
            return {"error": f"Access denied: {path}"}
        
        file_path = Path(path)
        
        if not file_path.exists():
            return {"error": f"File not found: {path}"}
        
        if file_path.is_dir():
            return {"error": f"Path is a directory. Cannot delete directory: {path}"}
        
        file_path.unlink()
        
        return {
            "success": True,
            "path": str(file_path),
            "message": "File deleted successfully"
        }
    except Exception as e:
        return {"error": f"Failed to delete file: {str(e)}"}


@mcp.tool()
def file_info(path: str) -> dict:
    """Get file metadata (size, created date, modified date, etc)
    
    Args:
        path: Path to file
    """
    try:
        if not is_path_allowed(path):
            return {"error": f"Access denied: {path}"}
        
        file_path = Path(path)
        
        if not file_path.exists():
            return {"error": f"File not found: {path}"}
        
        stat = file_path.stat()
        
        return {
            "success": True,
            "path": str(file_path),
            "type": "directory" if file_path.is_dir() else "file",
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "is_readable": os.access(file_path, os.R_OK),
            "is_writable": os.access(file_path, os.W_OK)
        }
    except Exception as e:
        return {"error": f"Failed to get file info: {str(e)}"}


# ============ RESOURCES (Optional) ============

@mcp.resource("file://{path}")
def read_file_resource(path: str) -> str:
    """Read a file as a resource
    
    Args:
        path: Path to file
    """
    try:
        if not is_path_allowed(path):
            raise ValueError(f"Access denied: {path}")
        
        file_path = Path(path)
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


# ============ USAGE EXAMPLES ============

"""
HOW TO USE THIS WITH CLAUDE:

1. Install dependencies:
   pip install fastmcp

2. Run the server:
   python filesystem_server.py

3. Configure Claude to use this MCP server in your settings

4. Now you can ask Claude:

   User: "What files are in my Documents folder?"
   → Claude calls: list_directory("C:\\Users\\alok4\\Documents")
   
   User: "Read my notes.txt file"
   → Claude calls: read_file("C:\\Users\\alok4\\Documents\\notes.txt")
   
   User: "Create a file called todo.txt with my tasks"
   → Claude calls: write_file("C:\\Users\\alok4\\Desktop\\todo.txt", "...")
   
   User: "Create a new folder for my project"
   → Claude calls: create_directory("C:\\Users\\alok4\\Desktop\\test_files\\my_project")
   
   User: "Delete the old backup file"
   → Claude calls: delete_file("C:\\Users\\alok4\\Desktop\\old_backup.txt")
   
   User: "When was my report last modified?"
   → Claude calls: file_info("C:\\Users\\alok4\\Documents\\report.pdf")

SECURITY:
- Only files in ALLOWED_BASE_PATHS can be accessed
- All paths are validated before operations
- Prevents directory traversal attacks
- All errors are caught and returned safely
"""

if __name__ == "__main__":
    print("File System MCP Server (FastMCP)")
    print(f"Allowed paths: {ALLOWED_BASE_PATHS}")
    print("Available tools:")
    print("  - read_file")
    print("  - write_file")
    print("  - list_directory")
    print("  - create_directory")
    print("  - delete_file")
    print("  - file_info")
    print("\nStarting server...")
    
    mcp.run()