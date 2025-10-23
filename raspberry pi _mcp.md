### mcp-pi — MCP-style SSH Tool Server for Raspberry Pi + Django

This project exposes a secure set of “tools” over HTTP (MCP-style) that let an LLM or client app execute controlled operations on a Raspberry Pi over SSH. It’s optimized for managing Django apps (migrate, collectstatic, runserver via tmux, and production services via systemd), while providing guardrails (auth, rate limiting, allowlists, auditing).

This README explains what each module does and how the pieces work together, with setup and usage tips.

---

### High-level architecture

- FastAPI app serves a minimal MCP-style interface:
  - Discovery endpoint: `GET /.well-known/mcp/tools` returns available tool schemas
  - Invocation endpoint: `POST /tools` takes `{ name, arguments }` and routes to the tool
- SSH transport powered by Paramiko for exec and SFTP
- Tool set:
  - ssh_exec — run controlled commands
  - scp_put/get — file upload/download via SFTP
  - tmux — ensure session, send keys, kill sessions (for long-lived processes)
  - django — run `manage.py` commands and dev server in tmux
  - systemd — manage services (start/stop/restart/status)
- Security + governance:
  - API key or JWT auth, CORS, rate limiting
  - Tool and command allowlists
  - Structured JSON logging with redaction
- Config-driven:
  - `hosts.yaml` for SSH targets
  - `policies.yaml` for security and allowlists

---

### Directory structure

- mcp_server/
  - main.py
  - config.py
  - ssh_transport.py
  - logging_setup.py
  - security.py
  - allowlist.py
  - tools/
    - ssh_exec.py
    - scp_put.py
    - scp_get.py
    - tmux.py
    - django.py
    - systemd.py
    - common.py
- config/
  - hosts.yaml (you create from example)
  - policies.yaml (you create from example)
  - hosts.example.yaml
  - policies.example.yaml
- deploy/
  - systemd/mcp-pi.service
- scripts/
  - dev_run.sh
- pyproject.toml
- README.md (this file)

---

### Module-by-module overview

#### 1) mcp_server/main.py — API surface and tool router

- What it does:
  - Initializes FastAPI app with logging and security middleware
  - Exposes:
    - GET `/.well-known/mcp/tools` — returns schemas for enabled tools
    - POST `/tools` — accepts a `ToolCall` with `name` and `arguments`, enforces policy, calls the tool, returns structured results
  - Also provides convenience per-tool endpoints (e.g., `/tools/ssh_exec`) that internally call the same router
- How it works:
  - On each request, middleware:
    - Refreshes policies dynamically (so changes to `policies.yaml` are picked up without restart)
    - Extracts Bearer token, verifies API key or JWT, enforces rate limit
  - When a tool is called:
    - Checks allowlist for tool and, for ssh_exec, validates command policy
    - Invokes the corresponding function, wraps results/errors, and audit-logs them

Why it matters:
- This is the “MCP server” entry point your LLM client connects to.
- Keeps a clean separation between transport, security, and tool logic.

---

#### 2) mcp_server/config.py — configuration loaders

- What it does:
  - Loads SSH target definitions from `config/hosts.yaml`
  - Loads policy config (auth, CORS, rate limiting, allowlists) from `config/policies.yaml`
  - Defines Pydantic models for both configs
- How it works:
  - `load_config()` returns `AppConfig` with a map of targets
  - `load_policies()` returns `PolicyConfig` with security + allowlist settings
- Why it matters:
  - Decouples runtime behavior from code, making environments easy to manage
  - Lets you ship the same server with different targets/policies

Tip: You can set environment variables `MCP_PI_CONFIG` and `MCP_PI_POLICY` to point to custom paths.

---

#### 3) mcp_server/ssh_transport.py — SSH and SFTP operations

- What it does:
  - Opens SSH connections with strong key-based auth
  - Exposes:
    - `exec(command, cwd, env, timeout)` — run a remote command, collect stdout/stderr/exit code
    - `put_bytes(data, remote_path, mode)` — upload bytes via SFTP
    - `get_bytes(remote_path)` — download bytes via SFTP
- How it works:
  - Paramiko client is created per request using `TargetConfig` (host, user, key path)
  - Optionally enforces `known_hosts` if configured (strict host checking)
  - Wraps results in a small `SSHResult` object

Why it matters:
- A single, consistent SSH layer that tools build upon
- Easy to swap for a different transport or extend (port forwards, etc.)

---

#### 4) mcp_server/logging_setup.py — structured logging with redaction

- What it does:
  - Installs a JSON formatter for logs
  - Best-effort redaction of sensitive fields (api keys, private key paths, passwords)
- How it works:
  - `setup_logging("INFO")` called at startup
  - Audit logs from `main.py` go through this formatter
- Why it matters:
  - Easier to ingest in log systems (journald, ELK, CloudWatch)
  - Reduces risk of leaking secrets in logs

---

#### 5) mcp_server/security.py — auth, CORS, rate limiting

- What it does:
  - CORS configuration
  - Token extraction (Bearer)
  - Verifies API keys or JWTs (PyJWT)
  - Naive in-memory rate limiter per IP+token
- How it works:
  - Uses `policies.yaml` to configure:
    - `security.api_keys`: list of allowed shared secrets
    - `security.jwt_public_key_pem`: if provided, verifies JWTs
    - `security.cors_allow_origins`: restricts allowed origins
    - `security.rate_limit_per_minute`: per minute per ip+token
- Why it matters:
  - Essential to control who can call tools and how often
  - JWT enables SSO/OIDC style integration if you have an IdP

Note: For multi-instance scaling, replace in-memory buckets with Redis.

---

#### 6) mcp_server/allowlist.py — tool and command governance

- What it does:
  - Decides if a tool is enabled globally and for a specific target
  - For `ssh_exec`, checks that commands start with allowed prefixes and don’t contain denied substrings
- How it works:
  - Reads from `policies.yaml`:
    - `allowlist.enabled_tools`
    - `allowlist.per_target_tools`
    - `allowlist.ssh_exec_allowed_prefixes`
    - `allowlist.ssh_exec_denied_substrings`
- Why it matters:
  - Prevents accidental or malicious misuse (e.g., `rm -rf /`)
  - You can keep `ssh_exec` enabled but locked down to safe maintenance commands

---

#### 7) mcp_server/tools/common.py — shared helpers for tools

- What it does:
  - Provides a `TargetedRequest` Pydantic base with `target`
  - `use_client(target)` returns a connected `SSHClientWrapper`
- Why it matters:
  - Reduces duplication across tools
  - Enforces consistent target lookup and errors

---

#### 8) mcp_server/tools/ssh_exec.py — execute remote commands

- What it does:
  - Tool: `ssh_exec`
  - Input: `target`, `command`, optional `cwd`, `env`, `timeout`
  - Output: `stdout`, `stderr`, `exit_code`
- How it works:
  - Calls `SSHClientWrapper.exec` with prefix logic:
    - Exports `env` vars
    - `cd` to `cwd`
    - Runs `command`
- Policy integration:
  - `main.py` calls `ssh_exec_allowed(command)` before invoking
- Use cases:
  - Diagnostics (`uname -a`, `df -h`, `journalctl ...`)
  - Controlled maintenance (`git pull`, `python manage.py migrate`, etc.)

---

#### 9) mcp_server/tools/scp_put.py and scp_get.py — file transfer

- What they do:
  - `scp_put`: Uploads a file (base64 content) to a `remote_path`, optional `mode`
  - `scp_get`: Downloads a file from `remote_path`, returns base64 content
- How they work:
  - Use SFTP via `SSHClientWrapper`
  - Base64 prevents JSON encoding issues
- Use cases:
  - Push `.env`, settings snippets, small artifacts
  - Retrieve logs or generated files

Note: For very large files, consider chunking or out-of-band transfer.

---

#### 10) mcp_server/tools/tmux.py — session/process management

- What it does:
  - `tmux_ensure`: ensures a tmux session exists (creates if not)
  - `tmux_send_keys`: sends commands/keys to a tmux session (default adds Enter)
  - `tmux_kill`: kills a tmux session
- How it works:
  - Namespaced session names with `mcp_` prefix to avoid collisions
  - `tmux_send_keys` supports sending Ctrl-C (`\x03`) for clean restarts
- Use cases:
  - Run Django dev server or background scripts persistently
  - Interactive debugging session the LLM can control lightly

---

#### 11) mcp_server/tools/django.py — Django utilities

- What it does:
  - `django_manage`: run `python manage.py <args>` (migrate, collectstatic, etc.)
  - `django_runserver_tmux`: run dev server in tmux, restartable with Ctrl-C
- How it works:
  - Accepts `project_dir`, optional `venv_path` (bin dir), `env`, `timeout`
  - Prepends `PATH` to prioritise venv
- Use cases:
  - CI-like operations from the LLM
  - Dev-time servers on a Pi with quick restarts

Tip: For production, use Gunicorn+systemd instead of `runserver`.

---

#### 12) mcp_server/tools/systemd.py — service control

- What it does:
  - `systemd_service`: `start|stop|restart|reload|enable|disable|status` a service
- How it works:
  - Runs `systemctl <action> <name>`
- Security note:
  - Prefer user services (`systemctl --user`) to avoid sudo
  - If using system-level services, add narrowly scoped sudoers entries and optionally modify the tool to prefix `sudo` for permitted services only

---

### Configuration files

#### config/hosts.yaml

- Defines SSH targets by name:
  - host, port, username, `private_key_path`, optional `known_hosts_path`, timeouts
- Example usage:
  - Set `known_hosts_path` and switch to `RejectPolicy` for strict host key checking

#### config/policies.yaml

- Controls security and tool policies:
  - security.api_keys — array of strong API keys
  - security.jwt_public_key_pem — PEM to verify JWTs (optional)
  - security.cors_allow_origins — allowed origins for browsers
  - security.rate_limit_per_minute — throttle abusive clients
  - allowlist.enabled_tools — explicit allowlist of tools
  - allowlist.per_target_tools — per-target tool restrictions
  - allowlist.ssh_exec_allowed_prefixes — permitted command prefixes
  - allowlist.ssh_exec_denied_substrings — banned substrings

Start permissive in dev, then tighten for prod.

---

### Deployment and operations

- Dev run:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -e .`
  - `./scripts/dev_run.sh`
- Production (systemd on the Pi):
  - Place `deploy/systemd/mcp-pi.service` in `/etc/systemd/system/`
  - `sudo systemctl daemon-reload && sudo systemctl enable mcp-pi && sudo systemctl start mcp-pi`
  - Logs: `journalctl -u mcp-pi -f`
- Docker:
  - Build/run with `Dockerfile` and `docker-compose.yml`
  - Mount `config/` read-only and SSH keys as needed

---

### Security best practices

- SSH
  - Use Ed25519 keys; disable password auth on the Pi
  - Enforce known_hosts with `RejectPolicy` in `hosts.yaml`
- API
  - Use long random API keys or JWT with a trusted IdP
  - Restrict CORS to trusted origins
  - Tune rate limits
- Governance
  - Shrink `ssh_exec_allowed_prefixes` to only what’s required
  - Use `per_target_tools` to limit powerful tools
- Least privilege
  - Run MCP server as a dedicated non-root user
  - Prefer user-level systemd services for app processes
  - Narrow sudoers rules if system services are unavoidable
- Auditing
  - Centralize logs; watch for `tool_blocked` and `ssh_exec_blocked` events
  - Keep secrets out of logs; redaction is best-effort, not absolute

---

### Example flows

- Run diagnostics:
  - `ssh_exec { target: "pi-lan", command: "uname -a" }`
- Deploy steps:
  - `scp_put` a `.env` file
  - `ssh_exec` `git pull && pip install -r requirements.txt`
  - `django_manage` `migrate`
  - `systemd_service` `restart` your Gunicorn service
- Dev server:
  - `tmux_ensure` session
  - `django_runserver_tmux` with desired port
  - `tmux_send_keys` Ctrl-C to restart when needed

---

### Troubleshooting

- 401 Unauthorized:
  - Missing/invalid `Authorization: Bearer <token>`; confirm key/JWT matches `policies.yaml`
- 403 Tool/command blocked:
  - Tool not in allowlist or command violates allowed prefixes/denied substrings
- SSH connect errors:
  - Check `hosts.yaml` target name, key path permissions, reachability, and known_hosts
- systemd permission errors:
  - Use `--user` services or scoped sudoers; verify the service name and user

---

### Extending the server

- Add a new tool:
  - Create `mcp_server/tools/<new_tool>.py` with Pydantic request/response, a function, and a `TOOL_SCHEMA`
  - Import it in `main.py`, add to discovery list and router
  - Add allowlist entries if needed
- Enhance security:
  - Replace in-memory rate limiter with Redis
  - Add per-user quotas based on JWT claims
- Observability:
  - Add metrics (Prometheus) and a `/metrics` endpoint

---

If you want, I can also provide:
- A production-ready Gunicorn systemd unit for Django with environment loading
- A minimal MCP client example to auto-discover and invoke these tools
- A CI/CD snippet (GitHub Actions) to deploy updates to your Pi via this server