# Complete MCP Server

This MCP (Model Context Protocol) server exposes all the tools from the FastAPI server, allowing Claude Desktop and other MCP clients to interact with remote SSH hosts.

## Features

The MCP server provides the following tools:

### 1. SSH Execution (`ssh_exec`)
Execute shell commands on remote hosts via SSH.

**Parameters:**
- `target`: Target name from config (required)
- `command`: Shell command to run (required)
- `cwd`: Working directory (optional)
- `env`: Environment variables (optional)
- `timeout`: Timeout in seconds (optional)

### 2. File Transfer

#### Upload (`scp_put`)
Upload files to remote hosts via SFTP.

**Parameters:**
- `target`: Target name from config (required)
- `remote_path`: Absolute path on remote host (required)
- `content_b64`: Base64-encoded file content (required)
- `mode`: Octal file mode, e.g., 0o644 (optional)

#### Download (`scp_get`)
Download files from remote hosts via SFTP.

**Parameters:**
- `target`: Target name from config (required)
- `remote_path`: Absolute path of file to download (required)

### 3. Tmux Session Management

#### Ensure Session (`tmux_ensure`)
Create or ensure a tmux session exists (sessions are prefixed with 'mcp_').

**Parameters:**
- `target`: Target name from config (required)
- `session`: Session name suffix (required)
- `cwd`: Working directory for session (optional)

#### Send Keys (`tmux_send_keys`)
Send commands to a tmux session.

**Parameters:**
- `target`: Target name from config (required)
- `session`: Session name suffix (required)
- `keys`: Command to send (required)
- `enter`: Whether to append Enter key (optional, default: true)

#### Kill Session (`tmux_kill`)
Kill a tmux session.

**Parameters:**
- `target`: Target name from config (required)
- `session`: Session name suffix (required)

### 4. Systemd Service Management (`systemd_service`)
Manage systemd services on remote hosts.

**Parameters:**
- `target`: Target name from config (required)
- `name`: Service name, e.g., "myproj.service" (required)
- `action`: Action to perform - start, stop, restart, reload, enable, disable, status (required)

### 5. Git Operations

#### Git Status (`git_status`)
Get git repository status on remote host.

**Parameters:**
- `target`: Target name from config (required)
- `project_dir`: Remote project directory containing the git repo (required)
- `short`: If true, runs 'git status --short --branch' else full 'git status' (optional, default: true)

#### Git Checkout (`git_checkout`)
Checkout a git branch or tag on remote host.

**Parameters:**
- `target`: Target name from config (required)
- `project_dir`: Remote project directory containing the git repo (required)
- `branch_or_tag`: Branch name or tag to checkout (required)

#### Git Pull (`git_pull`)
Pull latest changes from git repository on remote host.

**Parameters:**
- `target`: Target name from config (required)
- `project_dir`: Remote project directory containing the git repo (required)
- `branch`: Branch to pull (optional, default: current branch)

#### Deploy Hook (`deploy_hook`)
Execute deployment hook on remote host.

**Parameters:**
- `target`: Target name from config (required)
- `project_dir`: Remote project directory (required)
- `hook_script`: Path to deployment hook script (required)
- `env`: Environment variables for the hook (optional)

### 6. Django Management

#### Django Commands (`django_manage`)
Run Django management commands.

**Parameters:**
- `target`: Target name from config (required)
- `project_dir`: Remote project directory containing manage.py (required)
- `manage_args`: Arguments to manage.py (required)
- `venv_path`: Virtual environment bin path (optional)
- `env`: Environment variables (optional)
- `timeout`: Timeout in seconds (optional)

#### Django Runserver (`django_runserver_tmux`)
Run Django development server in a tmux session.

**Parameters:**
- `target`: Target name from config (required)
- `project_dir`: Remote project directory containing manage.py (required)
- `session`: Tmux session suffix (required)
- `host`: Host to bind to (optional, default: "0.0.0.0")
- `port`: Port to bind to (optional, default: 8000)
- `extra_args`: Extra runserver arguments (optional)
- `venv_path`: Virtual environment bin path (optional)
- `env`: Environment variables (optional)
- `timeout`: Timeout in seconds (optional)

## Configuration

The server uses the same configuration as the FastAPI server. Create a `config/hosts.yaml` file with your SSH targets:

```yaml
targets:
  pi-lan:
    host: "192.168.1.100"
    port: 22
    username: "pi"
    private_key_path: "/path/to/private/key"
    known_hosts_path: "/path/to/known_hosts"
    connect_timeout: 30
```

## Usage

### With Claude Desktop

1. Copy `claude_desktop_config_complete.json` to your Claude Desktop config directory
2. Update the paths in the config file to match your setup
3. Restart Claude Desktop

### Direct Usage

```bash
# Run the MCP server directly
python -m mcp_server.mcp_complete_server

# Test the server
python test_mcp_server.py
```

### Programmatic Usage

```python
import asyncio
from mcp_server.mcp_complete_server import server

async def main():
    # List available tools
    tools = await server.list_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")
    
    # Call a tool
    result = await server.call_tool("ssh_exec", {
        "target": "pi-lan",
        "command": "echo 'Hello World'"
    })
    print(result[0].text)

asyncio.run(main())
```

## Error Handling

The server provides detailed error messages for:
- Unknown targets
- SSH connection failures
- File operation errors
- Tool execution errors

All errors are returned as text content that can be displayed to the user.

## Dependencies

- `mcp` - Model Context Protocol library
- `paramiko` - SSH client library
- `pydantic` - Data validation
- `asyncio` - Asynchronous programming

## File Structure

```
mcp_server/
├── mcp_complete_server.py    # Main MCP server
├── config.py                 # Configuration loading
├── ssh_transport.py          # SSH client wrapper
└── tools/                    # Individual tool implementations
    ├── ssh_exec.py
    ├── scp_put.py
    ├── scp_get.py
    ├── tmux.py
    ├── systemd.py
    └── django.py
```

## Security Notes

- SSH keys should be properly secured
- Use known_hosts verification in production
- Consider using SSH agent for key management
- Validate all input parameters
- Use appropriate file permissions for uploaded files
