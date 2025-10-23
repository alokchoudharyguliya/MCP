# SSH MCP Server - Claude Desktop Configuration Guide

## Overview
This MCP server allows Claude Desktop to execute shell commands on remote hosts via SSH. It's configured to work with your Raspberry Pi and other SSH-accessible machines.

## Prerequisites

1. **Python Environment**: Python 3.10+ with dependencies installed
2. **SSH Configuration**: SSH keys and host access configured
3. **Claude Desktop**: Installed on your system

## Installation Steps

### 1. Install Dependencies

```powershell
# Navigate to project directory
cd C:\Users\alok4\Desktop\MCPs

# Install with uv (recommended)
uv pip install -e .

# OR with pip
pip install -e .
```

### 2. Configure SSH Targets

Edit `config/hosts.yaml` to add your SSH targets:

```yaml
targets:
  pi-lan:
    host: 10.22.96.113
    port: 22
    username: alok
    private_key_path: C:\Users\alok4\.ssh\id_ed25519
    connect_timeout: 10
  
  # Add more targets as needed
  my-server:
    host: example.com
    port: 22
    username: myuser
    private_key_path: C:\Users\alok4\.ssh\id_rsa
```

### 3. Test the Server Locally

Before configuring Claude Desktop, test the server:

```powershell
python -m mcp_server.mcp_ssh_server
```

The server should start without errors. Press Ctrl+C to stop.

### 4. Configure Claude Desktop

**Location of Claude Desktop config file:**

```
%APPDATA%\Claude\claude_desktop_config.json
```

Or typically:
```
C:\Users\alok4\AppData\Roaming\Claude\claude_desktop_config.json
```

**Add this configuration:**

```json
{
  "mcpServers": {
    "ssh-server": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server.mcp_ssh_server"
      ],
      "cwd": "C:\\Users\\alok4\\Desktop\\MCPs",
      "env": {
        "MCP_PI_CONFIG": "config/hosts.yaml"
      }
    }
  }
}
```

**Important:** If you already have other MCP servers configured, add the `ssh-server` section to your existing `mcpServers` object.

### 5. Alternative: Use Conda Environment

If you're using conda (GPU_ENV), update the Claude Desktop config:

```json
{
  "mcpServers": {
    "ssh-server": {
      "command": "C:\\Users\\alok4\\anaconda3\\envs\\GPU_ENV\\python.exe",
      "args": [
        "-m",
        "mcp_server.mcp_ssh_server"
      ],
      "cwd": "C:\\Users\\alok4\\Desktop\\MCPs",
      "env": {
        "MCP_PI_CONFIG": "config/hosts.yaml"
      }
    }
  }
}
```

### 6. Restart Claude Desktop

1. **Quit** Claude Desktop completely (check system tray)
2. **Restart** Claude Desktop
3. Look for the SSH server in the MCP tools list

## Usage in Claude

Once configured, you can ask Claude to:

### Example Commands

**Check disk space on Raspberry Pi:**
```
Use the ssh_exec tool to check disk space on pi-lan with the command: df -h
```

**List files in home directory:**
```
Execute ls -la on the pi-lan target
```

**Run a Python script:**
```
Run python3 /home/alok/my_script.py on pi-lan
```

**Install a package:**
```
Execute sudo apt-get update && sudo apt-get install -y htop on pi-lan
```

**Check system information:**
```
Get system info from pi-lan using: uname -a && cat /proc/cpuinfo | grep "model name" | head -1
```

## Tool Schema

The `ssh_exec` tool accepts:

- **target** (required): Target name from config (e.g., "pi-lan")
- **command** (required): Shell command to execute
- **cwd** (optional): Working directory on remote host
- **env** (optional): Environment variables as key-value pairs
- **timeout** (optional): Timeout in seconds

## Troubleshooting

### Server not appearing in Claude

1. Check Claude Desktop logs:
   - Windows: `%APPDATA%\Claude\logs`
   
2. Verify config file syntax (valid JSON)

3. Test server manually:
   ```powershell
   python -m mcp_server.mcp_ssh_server
   ```

### SSH Connection Errors

1. Verify SSH key permissions
2. Test SSH connection manually:
   ```powershell
   ssh -i C:\Users\alok4\.ssh\id_ed25519 alok@10.22.96.113
   ```
3. Check firewall settings
4. Verify host is reachable: `ping 10.22.96.113`

### Import Errors

```powershell
# Reinstall dependencies
cd C:\Users\alok4\Desktop\MCPs
pip install -e .
```

### Known Hosts Issues

If you want stricter security, add to `hosts.yaml`:

```yaml
targets:
  pi-lan:
    host: 10.22.96.113
    # ... other settings ...
    known_hosts_path: C:\Users\alok4\.ssh\known_hosts
```

## Security Considerations

1. **Private Keys**: Keep SSH private keys secure and never commit to git
2. **Config File**: Add `config/hosts.yaml` to `.gitignore`
3. **Known Hosts**: Use `known_hosts_path` for production environments
4. **Command Validation**: Be cautious with destructive commands
5. **Timeouts**: Set reasonable timeouts to prevent hung connections

## Adding More Targets

Edit `config/hosts.yaml`:

```yaml
targets:
  production-server:
    host: prod.example.com
    port: 22
    username: deploy
    private_key_path: C:\Users\alok4\.ssh\deploy_key
    known_hosts_path: C:\Users\alok4\.ssh\known_hosts
    connect_timeout: 15

  staging-server:
    host: staging.example.com
    port: 2222
    username: deploy
    private_key_path: C:\Users\alok4\.ssh\deploy_key
```

Then restart Claude Desktop to use the new targets.

## Uninstalling

To remove from Claude Desktop:

1. Open `%APPDATA%\Claude\claude_desktop_config.json`
2. Remove the `ssh-server` section
3. Restart Claude Desktop

---

## Quick Start Summary

```powershell
# 1. Install
cd C:\Users\alok4\Desktop\MCPs
pip install -e .

# 2. Configure
# Edit config/hosts.yaml with your SSH targets

# 3. Add to Claude Desktop
# Edit: %APPDATA%\Claude\claude_desktop_config.json
# Add the ssh-server configuration

# 4. Restart Claude Desktop

# 5. Test in Claude
# Ask: "Use ssh_exec to run 'hostname' on pi-lan"
```

Enjoy remote SSH execution through Claude! 🚀
