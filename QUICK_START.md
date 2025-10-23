# Quick Setup - SSH MCP Server for Claude Desktop

## 📋 TL;DR

1. **Install dependencies**: `pip install -e .`
2. **Configure**: Edit `config/hosts.yaml` with your SSH targets
3. **Add to Claude Desktop**: Edit `%APPDATA%\Claude\claude_desktop_config.json`
4. **Restart Claude Desktop**

---

## 📝 Claude Desktop Config

**File location:** `C:\Users\alok4\AppData\Roaming\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ssh-server": {
      "command": "python",
      "args": ["-m", "mcp_server.mcp_ssh_server"],
      "cwd": "C:\\Users\\alok4\\Desktop\\MCPs",
      "env": {
        "MCP_PI_CONFIG": "config/hosts.yaml"
      }
    }
  }
}
```

**OR with Conda:**

```json
{
  "mcpServers": {
    "ssh-server": {
      "command": "C:\\Users\\alok4\\anaconda3\\envs\\GPU_ENV\\python.exe",
      "args": ["-m", "mcp_server.mcp_ssh_server"],
      "cwd": "C:\\Users\\alok4\\Desktop\\MCPs",
      "env": {
        "MCP_PI_CONFIG": "config/hosts.yaml"
      }
    }
  }
}
```

---

## 🎯 Example Usage in Claude

Once configured, ask Claude:

- ✅ "Run `ls -la` on pi-lan"
- ✅ "Check disk space on pi-lan with `df -h`"
- ✅ "Execute `hostname && uptime` on pi-lan"
- ✅ "Install htop on pi-lan"
- ✅ "Run my Python script at /home/alok/script.py on pi-lan"

---

## 🔧 Current Configuration

Your `config/hosts.yaml`:
- **Target:** `pi-lan`
- **Host:** `10.22.96.113:22`
- **User:** `alok`
- **Key:** `C:\Users\alok4\.ssh\id_ed25519`

---

## ✅ Verification

Test locally before configuring Claude:

```powershell
python -m mcp_server.mcp_ssh_server
```

Should start without errors (Ctrl+C to stop).

---

## 🐛 Troubleshooting

**Server not showing in Claude?**
- Check logs: `%APPDATA%\Claude\logs`
- Verify JSON syntax in config
- Restart Claude Desktop completely

**SSH errors?**
- Test: `ssh -i C:\Users\alok4\.ssh\id_ed25519 alok@10.22.96.113`
- Check firewall
- Verify key permissions

---

For detailed instructions, see `MCP_SSH_SETUP.md`
