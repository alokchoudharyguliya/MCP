# Complete MCP Server Documentation

## 🎯 **Project Overview**

This project provides a comprehensive MCP (Model Context Protocol) server that exposes SSH management tools for remote hosts, particularly Raspberry Pi devices. It includes both a FastAPI server for HTTP access and an MCP server for Claude Desktop integration.

## 📁 **Project Structure**

```
MCPs/
├── mcp_server/                    # Main server package
│   ├── main.py                   # FastAPI server with all endpoints
│   ├── mcp_complete_server.py   # MCP protocol server for Claude Desktop
│   ├── mcp_ssh_server.py         # Basic SSH-only MCP server
│   ├── config.py                 # Configuration management
│   ├── security.py               # Authentication & rate limiting
│   ├── allowlist.py              # Tool allowlisting
│   ├── ssh_transport.py          # SSH connection wrapper
│   └── tools/                    # Tool implementations
│       ├── ssh_exec.py           # SSH command execution
│       ├── scp_put.py            # File upload
│       ├── scp_get.py            # File download
│       ├── tmux.py               # Tmux session management
│       ├── git_tools.py          # Git operations
│       ├── gpio_tools.py         # GPIO control
│       ├── systemd.py            # Systemd service management
│       └── django.py             # Django management
├── config/                       # Configuration files
│   ├── hosts.yaml               # SSH target configuration
│   ├── policies.yaml            # Security policies
│   └── policies.example.yaml    # Example policies
└── Various test files and documentation
```

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
# Or install individually:
pip install fastapi uvicorn pydantic pyyaml paramiko
```

### **2. Configure SSH Targets**
Edit `config/hosts.yaml`:
```yaml
targets:
  pi-lan:
    host: 10.22.96.113
    port: 22
    username: alok
    private_key_path: C:\Users\alok4\.ssh\id_ed25519
```

### **3. Configure Security**
Edit `config/policies.yaml`:
```yaml
security:
  api_keys:
    - "kklWgaHK48zQXttGl35YMQYZMgtntrqJ"  # Your API key
  cors_allow_origins:
    - "http://localhost:7800"
  rate_limit_per_minute: 120

allowlist:
  enabled_tools:
    - ssh_exec
    - scp_put
    - scp_get
    - tmux_ensure
    - tmux_send_keys
    - tmux_kill
    - systemd_service
    - django_manage
    - django_runserver_tmux
    - git_status
    - git_checkout
    - git_pull
    - deploy_hook
    - gpio_write
    - gpio_read
    - gpio_pwm
    - macro_run
```

### **4. Start the Server**
```bash
# FastAPI Server
uvicorn mcp_server.main:app --host 0.0.0.0 --port 8000 --reload

# MCP Server (for Claude Desktop)
python -m mcp_server.mcp_complete_server
```

## 🛠️ **Available Tools**

### **1. SSH Execution**
- **Tool**: `ssh_exec`
- **Description**: Execute shell commands on remote hosts
- **Parameters**:
  - `target`: Target name from config
  - `command`: Shell command to run
  - `cwd`: Working directory (optional)
  - `env`: Environment variables (optional)
  - `timeout`: Timeout in seconds (optional)

### **2. File Transfer**
- **Tools**: `scp_put`, `scp_get`
- **Description**: Upload/download files via SFTP
- **Parameters**:
  - `target`: Target name from config
  - `remote_path`: Remote file path
  - `content_b64`: Base64-encoded content (for upload)
  - `mode`: File permissions (for upload)

### **3. Tmux Session Management**
- **Tools**: `tmux_ensure`, `tmux_send_keys`, `tmux_kill`
- **Description**: Manage tmux sessions on remote hosts
- **Parameters**:
  - `target`: Target name from config
  - `session`: Session name
  - `cwd`: Working directory (optional)
  - `keys`: Keys to send (for send_keys)

### **4. Git Operations**
- **Tools**: `git_status`, `git_checkout`, `git_pull`, `deploy_hook`
- **Description**: Git repository management on remote hosts
- **Parameters**:
  - `target`: Target name from config
  - `project_dir`: Remote project directory
  - `branch_or_tag`: Branch/tag to checkout (for checkout)
  - `branch`: Branch to pull (for pull)
  - `hook_script`: Deployment script path (for deploy_hook)

### **5. GPIO Control**
- **Tools**: `gpio_write`, `gpio_read`, `gpio_pwm`, `macro_run`
- **Description**: Control GPIO pins on Raspberry Pi
- **Parameters**:
  - `target`: Target name from config
  - `pin`: GPIO pin number
  - `value`: Value to write (0 or 1)
  - `mode`: GPIO mode (BCM or BOARD)
  - `frequency`: PWM frequency (for PWM)
  - `duty_cycle`: PWM duty cycle (for PWM)

### **6. Systemd Services**
- **Tool**: `systemd_service`
- **Description**: Manage systemd services
- **Parameters**:
  - `target`: Target name from config
  - `name`: Service name
  - `action`: Action (start, stop, restart, etc.)

### **7. Django Management**
- **Tools**: `django_manage`, `django_runserver_tmux`
- **Description**: Django project management
- **Parameters**:
  - `target`: Target name from config
  - `project_dir`: Django project directory
  - `manage_args`: Django management command arguments
  - `session`: Tmux session name (for runserver)

## 🔐 **Security Features**

### **Authentication**
- API key authentication for all endpoints
- JWT token support (optional)
- Rate limiting (120 requests/minute by default)
- CORS protection

### **Tool Allowlisting**
- Global tool allowlist
- Per-target tool restrictions
- SSH command allowlisting
- GPIO pin restrictions

### **Audit Logging**
- All operations logged
- Authentication attempts tracked
- Tool usage monitored
- Error tracking

## 📡 **API Endpoints**

### **FastAPI Server Endpoints**
- `GET /docs` - API documentation
- `GET /health` - Health check
- `GET /.well-known/mcp/tools` - List available tools
- `POST /tools` - Execute any tool
- `POST /tools/ssh_exec` - SSH execution
- `POST /tools/scp_put` - File upload
- `POST /tools/scp_get` - File download
- `POST /tools/tmux/ensure` - Create tmux session
- `POST /tools/tmux/send_keys` - Send keys to tmux
- `POST /tools/tmux/kill` - Kill tmux session
- `POST /tools/git/status` - Git status
- `POST /tools/git/checkout` - Git checkout
- `POST /tools/git/pull` - Git pull
- `POST /tools/deploy/hook` - Deploy hook
- `POST /tools/gpio/write` - GPIO write
- `POST /tools/gpio/read` - GPIO read
- `POST /tools/gpio/pwm` - GPIO PWM
- `POST /tools/gpio/macro_run` - GPIO macro
- `POST /tools/systemd` - Systemd service
- `POST /tools/django/manage` - Django management
- `POST /tools/django/runserver_tmux` - Django runserver

## 🤖 **Claude Desktop Integration**

### **Configuration**
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-complete-server": {
      "command": "python",
      "args": ["-m", "mcp_server.mcp_complete_server"],
      "cwd": "C:\\Users\\alok4\\Desktop\\MCPs",
      "env": {
        "PYTHONPATH": "C:\\Users\\alok4\\Desktop\\MCPs"
      }
    }
  }
}
```

### **Usage in Claude Desktop**
Once configured, you can use all tools directly in Claude Desktop:
- "Check the git status on my pi-lan server"
- "Upload a file to the remote server"
- "Start a Django development server"
- "Control GPIO pin 17 on the Raspberry Pi"

## 🧪 **Testing**

### **Test Scripts**
- `test_server_auth.py` - Test authentication
- `test_mcp_server.py` - Test MCP server
- `verify_git_integration.py` - Verify git tools
- `test_git_tools_mcp.py` - Test git tools in MCP

### **Manual Testing**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with authentication
curl -H "Authorization: Bearer kklWgaHK48zQXttGl35YMQYZMgtntrqJ" \
     http://localhost:8000/.well-known/mcp/tools

# Test SSH execution
curl -X POST -H "Authorization: Bearer kklWgaHK48zQXttGl35YMQYZMgtntrqJ" \
     -H "Content-Type: application/json" \
     -d '{"target": "pi-lan", "command": "echo hello"}' \
     http://localhost:8000/tools/ssh_exec
```

## 🔧 **Configuration Details**

### **Hosts Configuration** (`config/hosts.yaml`)
```yaml
targets:
  pi-lan:
    host: 10.22.96.113
    port: 22
    username: alok
    private_key_path: C:\Users\alok4\.ssh\id_ed25519
    # Optional:
    # known_hosts_path: /path/to/known_hosts
    # connect_timeout: 10
```

### **Policies Configuration** (`config/policies.yaml`)
```yaml
security:
  api_keys:
    - "your-api-key-here"
  cors_allow_origins:
    - "http://localhost:7800"
  rate_limit_per_minute: 120

allowlist:
  enabled_tools:
    - ssh_exec
    - scp_put
    - scp_get
    # ... all tools
  per_target_tools:
    pi-lan:
      - ssh_exec
      - gpio_write
      # ... specific tools for this target
  ssh_exec_allowed_prefixes:
    - "echo "
    - "ls"
    - "git "
    # ... allowed command prefixes
  ssh_exec_denied_substrings:
    - "rm -rf"
    - "shutdown"
    # ... forbidden command patterns

gpio:
  targets:
    pi-lan:
      agent_path: "/home/alok/gpio_agent.py"
      default_mode: "BCM"
      allowed_pins:
        BCM: [17, 18, 27, 22, 23, 24, 25]
        BOARD: [11, 12, 13, 15, 16, 18, 22]
      capabilities:
        "17": ["read", "write"]
        "18": ["read", "write", "pwm"]
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **401 Unauthorized**
   - Check API key in `policies.yaml`
   - Ensure Authorization header is correct

2. **Import Errors**
   - Install missing dependencies: `pip install paramiko`
   - Check Python path

3. **SSH Connection Failed**
   - Verify SSH key path
   - Check network connectivity
   - Verify target configuration

4. **Tool Not Allowed**
   - Check tool is in `enabled_tools` list
   - Verify per-target restrictions

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn mcp_server.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📈 **Performance**

### **Rate Limiting**
- Default: 120 requests/minute per IP
- Configurable in `policies.yaml`
- Per-token rate limiting

### **Connection Pooling**
- SSH connections are pooled
- Automatic cleanup of idle connections
- Configurable timeouts

## 🔄 **Recent Changes**

### **What Was Added/Fixed**
1. **Authentication Fixed**: Updated API key in policies.yaml
2. **GPIO Tools Added**: Complete GPIO control integration
3. **MCP Server Enhanced**: All tools now available in Claude Desktop
4. **Documentation Updated**: Comprehensive README with all tools
5. **Configuration Cleaned**: Removed commented sections
6. **Error Handling Improved**: Better error messages and logging

### **New Features**
- GPIO pin control (read, write, PWM)
- GPIO macro execution
- Enhanced security policies
- Per-target tool restrictions
- Comprehensive audit logging

## 🎯 **Next Steps**

1. **Test All Tools**: Verify all endpoints work correctly
2. **Add More Tools**: Consider adding more remote management tools
3. **Enhance Security**: Add more security features
4. **Improve Documentation**: Add more examples and use cases
5. **Performance Optimization**: Optimize for high-load scenarios

This documentation provides a complete overview of the MCP server project, including all tools, configuration options, and usage instructions.
