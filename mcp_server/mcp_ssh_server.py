"""
MCP SSH Server - Execute commands on remote hosts via SSH
Compatible with Claude Desktop
"""

import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from .config import load_config
from .ssh_transport import SSHClientWrapper
from .tools.ssh_exec import SSHExecRequest

# Initialize MCP Server
server = Server("ssh-mcp-server")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available SSH execution tool"""
    return [
        types.Tool(
            name="ssh_exec",
            description="Execute a shell command on a remote host via SSH. Configured targets are loaded from config/hosts.yaml",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets (e.g., 'pi-lan')"
                    },
                    "command": {
                        "type": "string",
                        "description": "Shell command to run on remote host"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory on remote host (optional)"
                    },
                    "env": {
                        "type": "object",
                        "description": "Environment variables as key-value pairs (optional)",
                        "additionalProperties": {"type": "string"}
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (optional)"
                    }
                },
                "required": ["target", "command"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls from Claude"""
    
    if name != "ssh_exec":
        raise ValueError(f"Unknown tool: {name}")
    
    try:
        # Load configuration
        cfg = load_config()
        
        # Validate request
        req = SSHExecRequest(**arguments)
        
        if req.target not in cfg.targets:
            available_targets = ", ".join(cfg.targets.keys())
            return [types.TextContent(
                type="text",
                text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
            )]
        
        # Execute SSH command
        target_cfg = cfg.targets[req.target]
        with SSHClientWrapper(target_cfg) as cli:
            result = cli.exec(req.command, cwd=req.cwd, env=req.env, timeout=req.timeout)
            
            # Format response
            response_text = f"Command: {req.command}\n"
            response_text += f"Target: {req.target} ({target_cfg.host})\n"
            response_text += f"Exit Code: {result.exit_code}\n\n"
            
            if result.stdout:
                response_text += f"STDOUT:\n{result.stdout}\n\n"
            
            if result.stderr:
                response_text += f"STDERR:\n{result.stderr}\n"
            
            return [types.TextContent(
                type="text",
                text=response_text
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing SSH command: {str(e)}"
        )]

async def main():
    """Main entry point for the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
