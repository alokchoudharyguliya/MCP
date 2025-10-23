"""
Complete MCP Server - Exposes all FastAPI tools via MCP protocol
Compatible with Claude Desktop and other MCP clients
"""

import asyncio
import sys
import base64
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# Import all the tool functions and schemas
from .config import load_config
from .ssh_transport import SSHClientWrapper
from .tools.ssh_exec import ssh_exec, SSHExecRequest
from .tools.scp_put import scp_put, ScpPutRequest
from .tools.scp_get import scp_get, ScpGetRequest
from .tools.tmux import tmux_ensure, tmux_send_keys, tmux_kill, TmuxEnsureRequest, TmuxSendKeysRequest, TmuxKillRequest
from .tools.git_tools import (
    git_status, git_checkout, git_pull, deploy_hook, 
    GitStatusRequest, GitCheckoutRequest, GitPullRequest, DeployHookRequest,
    TOOL_GIT_STATUS, TOOL_GIT_CHECKOUT, TOOL_GIT_PULL, TOOL_DEPLOY_HOOK
)
from .tools.systemd import service_action, ServiceActionRequest
from .tools.django import django_manage, django_runserver_tmux, DjangoManageRequest, DjangoRunserverRequest

# Initialize MCP Server
server = Server("mcp-complete-server")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List all available tools from the FastAPI server"""
    return [
        # SSH Execution
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
        ),
        
        # File Transfer - Upload
        types.Tool(
            name="scp_put",
            description="Upload a file to the target via SFTP (content as base64)",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "remote_path": {
                        "type": "string",
                        "description": "Absolute path to write on remote host"
                    },
                    "content_b64": {
                        "type": "string",
                        "description": "Base64-encoded file content"
                    },
                    "mode": {
                        "type": "integer",
                        "description": "Octal file mode, e.g., 0o644 (optional)"
                    }
                },
                "required": ["target", "remote_path", "content_b64"]
            }
        ),
        
        # File Transfer - Download
        types.Tool(
            name="scp_get",
            description="Download a file from the target via SFTP (content as base64)",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "remote_path": {
                        "type": "string",
                        "description": "Absolute path of file to read from remote host"
                    }
                },
                "required": ["target", "remote_path"]
            }
        ),
        
        # Tmux Management
        types.Tool(
            name="tmux_ensure",
            description="Ensure a tmux session exists (create if needed). Sessions are prefixed with 'mcp_'",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "session": {
                        "type": "string",
                        "description": "Session name (suffix); will be prefixed with 'mcp_'"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory for the session (optional)"
                    }
                },
                "required": ["target", "session"]
            }
        ),
        
        types.Tool(
            name="tmux_send_keys",
            description="Send keys/command to a tmux session (adds Enter by default)",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "session": {
                        "type": "string",
                        "description": "Session name (suffix); will be prefixed with 'mcp_'"
                    },
                    "keys": {
                        "type": "string",
                        "description": "Command to send; will append Enter by default"
                    },
                    "enter": {
                        "type": "boolean",
                        "description": "Whether to append Enter key (default: true)"
                    }
                },
                "required": ["target", "session", "keys"]
            }
        ),
        
        types.Tool(
            name="tmux_kill",
            description="Kill a tmux session",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "session": {
                        "type": "string",
                        "description": "Session name (suffix); will be prefixed with 'mcp_'"
                    }
                },
                "required": ["target", "session"]
            }
        ),
        
        # Systemd Service Management
        types.Tool(
            name="systemd_service",
            description="Manage a systemd service on the target",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "name": {
                        "type": "string",
                        "description": "systemd service name (e.g., myproj.service)"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["start", "stop", "restart", "reload", "enable", "disable", "status"],
                        "description": "Action to perform on the service"
                    }
                },
                "required": ["target", "name", "action"]
            }
        ),
        
        # Django Management
        types.Tool(
            name="django_manage",
            description="Run python manage.py with given args (migrate, collectstatic, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "project_dir": {
                        "type": "string",
                        "description": "Remote project working directory (contains manage.py)"
                    },
                    "manage_args": {
                        "type": "string",
                        "description": "Arguments to manage.py, e.g., 'migrate' or 'collectstatic --noinput'"
                    },
                    "venv_path": {
                        "type": "string",
                        "description": "Remote virtualenv bin path, e.g., /home/pi/apps/myproj/.venv/bin (optional)"
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
                "required": ["target", "project_dir", "manage_args"]
            }
        ),
        
        types.Tool(
            name="django_runserver_tmux",
            description="Run Django dev server in a tmux session (sends Ctrl-C first, then runserver)",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "project_dir": {
                        "type": "string",
                        "description": "Remote project working directory (contains manage.py)"
                    },
                    "session": {
                        "type": "string",
                        "description": "Tmux session suffix to use (will be prefixed with 'mcp_')"
                    },
                    "host": {
                        "type": "string",
                        "description": "Host to bind to (default: 0.0.0.0)"
                    },
                    "port": {
                        "type": "integer",
                        "description": "Port to bind to (default: 8000)"
                    },
                    "extra_args": {
                        "type": "string",
                        "description": "Extra args, e.g., --settings=... (optional)"
                    },
                    "venv_path": {
                        "type": "string",
                        "description": "Remote virtualenv bin path (optional)"
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
                "required": ["target", "project_dir", "session"]
            }
        ),
        
        # Git Tools
        types.Tool(
            name="git_status",
            description="Get git repository status on remote host",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "project_dir": {
                        "type": "string",
                        "description": "Remote project directory containing the git repo"
                    },
                    "short": {
                        "type": "boolean",
                        "description": "If true, runs 'git status --short --branch' else full 'git status'"
                    }
                },
                "required": ["target", "project_dir"]
            }
        ),
        
        types.Tool(
            name="git_checkout",
            description="Checkout a git branch or tag on remote host",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "project_dir": {
                        "type": "string",
                        "description": "Remote project directory containing the git repo"
                    },
                    "branch_or_tag": {
                        "type": "string",
                        "description": "Branch name or tag to checkout"
                    }
                },
                "required": ["target", "project_dir", "branch_or_tag"]
            }
        ),
        
        types.Tool(
            name="git_pull",
            description="Pull latest changes from git repository on remote host",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "project_dir": {
                        "type": "string",
                        "description": "Remote project directory containing the git repo"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch to pull (default: current branch)"
                    }
                },
                "required": ["target", "project_dir"]
            }
        ),
        
        types.Tool(
            name="deploy_hook",
            description="Execute deployment hook on remote host",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target name from config.targets"
                    },
                    "project_dir": {
                        "type": "string",
                        "description": "Remote project directory"
                    },
                    "hook_script": {
                        "type": "string",
                        "description": "Path to deployment hook script"
                    },
                    "env": {
                        "type": "object",
                        "description": "Environment variables for the hook",
                        "additionalProperties": {"type": "string"}
                    }
                },
                "required": ["target", "project_dir", "hook_script"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls from MCP clients"""
    
    try:
        # Load configuration
        cfg = load_config()
        
        # Route to appropriate tool handler
        if name == "ssh_exec":
            return await _handle_ssh_exec(arguments, cfg)
        elif name == "scp_put":
            return await _handle_scp_put(arguments, cfg)
        elif name == "scp_get":
            return await _handle_scp_get(arguments, cfg)
        elif name == "tmux_ensure":
            return await _handle_tmux_ensure(arguments, cfg)
        elif name == "tmux_send_keys":
            return await _handle_tmux_send_keys(arguments, cfg)
        elif name == "tmux_kill":
            return await _handle_tmux_kill(arguments, cfg)
        elif name == "systemd_service":
            return await _handle_systemd_service(arguments, cfg)
        elif name == "django_manage":
            return await _handle_django_manage(arguments, cfg)
        elif name == "django_runserver_tmux":
            return await _handle_django_runserver(arguments, cfg)
        elif name == "git_status":
            return await _handle_git_status(arguments, cfg)
        elif name == "git_checkout":
            return await _handle_git_checkout(arguments, cfg)
        elif name == "git_pull":
            return await _handle_git_pull(arguments, cfg)
        elif name == "deploy_hook":
            return await _handle_deploy_hook(arguments, cfg)
        else:
            return [types.TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'. Available tools: ssh_exec, scp_put, scp_get, tmux_ensure, tmux_send_keys, tmux_kill, systemd_service, django_manage, django_runserver_tmux, git_status, git_checkout, git_pull, deploy_hook"
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing tool '{name}': {str(e)}"
        )]

async def _handle_ssh_exec(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle SSH execution tool"""
    req = SSHExecRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = ssh_exec(req)
    
    response_text = f"Command: {req.command}\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Exit Code: {result.exit_code}\n\n"
    
    if result.stdout:
        response_text += f"STDOUT:\n{result.stdout}\n\n"
    
    if result.stderr:
        response_text += f"STDERR:\n{result.stderr}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_scp_put(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle file upload tool"""
    req = ScpPutRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = scp_put(req)
    
    response_text = f"File uploaded successfully!\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Remote Path: {result.remote_path}\n"
    response_text += f"Size: {result.size} bytes\n"
    if result.mode:
        response_text += f"Mode: {oct(result.mode)}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_scp_get(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle file download tool"""
    req = ScpGetRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = scp_get(req)
    
    response_text = f"File downloaded successfully!\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Remote Path: {result.remote_path}\n"
    response_text += f"Content (Base64): {result.content_b64}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_tmux_ensure(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle tmux session ensure tool"""
    req = TmuxEnsureRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = tmux_ensure(req)
    
    response_text = f"Tmux Session: {result.session}\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Status: {'OK' if result.ok else 'Failed'}\n"
    response_text += f"Detail: {result.detail}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_tmux_send_keys(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle tmux send keys tool"""
    req = TmuxSendKeysRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = tmux_send_keys(req)
    
    response_text = f"Tmux Session: {result.session}\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Keys Sent: {req.keys}\n"
    response_text += f"Status: {'OK' if result.ok else 'Failed'}\n"
    response_text += f"Detail: {result.detail}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_tmux_kill(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle tmux session kill tool"""
    req = TmuxKillRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = tmux_kill(req)
    
    response_text = f"Tmux Session: {result.session}\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Status: {'Killed' if result.ok else 'Failed to kill'}\n"
    response_text += f"Detail: {result.detail}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_systemd_service(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle systemd service management tool"""
    req = ServiceActionRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = service_action(req)
    
    response_text = f"Service: {result.name}\n"
    response_text += f"Action: {result.action}\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Status: {'OK' if result.ok else 'Failed'}\n"
    response_text += f"Exit Code: {result.exit_code}\n\n"
    
    if result.stdout:
        response_text += f"STDOUT:\n{result.stdout}\n\n"
    
    if result.stderr:
        response_text += f"STDERR:\n{result.stderr}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_django_manage(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle Django management tool"""
    req = DjangoManageRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = django_manage(req)
    
    response_text = f"Django Management Command: {req.manage_args}\n"
    response_text += f"Project Directory: {req.project_dir}\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Exit Code: {result.exit_code}\n\n"
    
    if result.stdout:
        response_text += f"STDOUT:\n{result.stdout}\n\n"
    
    if result.stderr:
        response_text += f"STDERR:\n{result.stderr}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_django_runserver(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle Django runserver tool"""
    req = DjangoRunserverRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = django_runserver_tmux(req)
    
    response_text = f"Django Runserver\n"
    response_text += f"Session: {result.session}\n"
    response_text += f"Project Directory: {req.project_dir}\n"
    response_text += f"Host: {req.host}:{req.port}\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Status: {'OK' if result.ok else 'Failed'}\n"
    response_text += f"Detail: {result.detail}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_git_status(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle git status tool"""
    req = GitStatusRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = git_status(req)
    
    response_text = f"Git Status\n"
    response_text += f"Project Directory: {req.project_dir}\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Exit Code: {result.exit_code}\n\n"
    
    if result.stdout:
        response_text += f"STDOUT:\n{result.stdout}\n\n"
    
    if result.stderr:
        response_text += f"STDERR:\n{result.stderr}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_git_checkout(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle git checkout tool"""
    req = GitCheckoutRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = git_checkout(req)
    
    response_text = f"Git Checkout\n"
    response_text += f"Branch/Tag: {req.branch_or_tag}\n"
    response_text += f"Project Directory: {req.project_dir}\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Exit Code: {result.exit_code}\n\n"
    
    if result.stdout:
        response_text += f"STDOUT:\n{result.stdout}\n\n"
    
    if result.stderr:
        response_text += f"STDERR:\n{result.stderr}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_git_pull(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle git pull tool"""
    req = GitPullRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = git_pull(req)
    
    response_text = f"Git Pull\n"
    response_text += f"Branch: {req.branch or 'current'}\n"
    response_text += f"Project Directory: {req.project_dir}\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Exit Code: {result.exit_code}\n\n"
    
    if result.stdout:
        response_text += f"STDOUT:\n{result.stdout}\n\n"
    
    if result.stderr:
        response_text += f"STDERR:\n{result.stderr}\n"
    
    return [types.TextContent(type="text", text=response_text)]

async def _handle_deploy_hook(arguments: dict, cfg) -> list[types.TextContent]:
    """Handle deploy hook tool"""
    req = DeployHookRequest(**arguments)
    
    if req.target not in cfg.targets:
        available_targets = ", ".join(cfg.targets.keys())
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown target '{req.target}'. Available targets: {available_targets}"
        )]
    
    result = deploy_hook(req)
    
    response_text = f"Deploy Hook\n"
    response_text += f"Hook Script: {req.hook_script}\n"
    response_text += f"Project Directory: {req.project_dir}\n"
    response_text += f"Target: {req.target} ({cfg.targets[req.target].host})\n"
    response_text += f"Exit Code: {result.exit_code}\n\n"
    
    if result.stdout:
        response_text += f"STDOUT:\n{result.stdout}\n\n"
    
    if result.stderr:
        response_text += f"STDERR:\n{result.stderr}\n"
    
    return [types.TextContent(type="text", text=response_text)]

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
