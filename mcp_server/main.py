# # from __future__ import annotations

# # from fastapi import FastAPI, HTTPException
# # from pydantic import BaseModel
# # from typing import Any, Dict

# # from tools.ssh_exec import ssh_exec, SSHExecRequest, TOOL_SCHEMA as SSH_EXEC_SCHEMA

# ## pp = FastAPI(title="MCP Pi Tool Server", version="0.1.0")

# ## lass ToolCall(BaseModel):
# ##    name: str
# ##    arguments: Dict[str, Any]

# ## app.get("/.well-known/mcp/tools")
# ## ef list_tools():
# ##    # Advertise tool(s) to clients
# ##    return {"tools": [SSH_EXEC_SCHEMA]}

# ## app.post("/tools")
# ## ef call_tool(body: ToolCall):
# ##    try:
# ##        if body.name == "ssh_exec":
# ##            req = SSHExecRequest(**body.arguments)
# ##            resp = ssh_exec(req)
# ##            return resp.model_dump()
# ##        else:
# ##            raise HTTPException(status_code=404, detail=f"Unknown tool: {body.name}")
# ##    except Exception as e:
# ##        raise HTTPException(status_code=400, detail=str(e))

# ##  Convenience direct endpoint for ssh_exec
# ## app.post("/tools/ssh_exec")
# ## ef call_ssh_exec(args: Dict[str, Any]):
# ##    try:
# ##        req = SSHExecRequest(**args)
# ##        resp = ssh_exec(req)
# ##        return resp.model_dump()
# ##    except Exception as e:
# ##        raise HTTPException(status_code=400, detail=str(e))

# ## app.get("/health")
# ## ef health():
# ##    return {"status": "ok"}

# from __future__ import annotations

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Any, Dict

# # Existing
# from .tools.ssh_exec import ssh_exec, SSHExecRequest, TOOL_SCHEMA as SSH_EXEC_SCHEMA

# # New tools
# from .tools.scp_put import scp_put, ScpPutRequest, TOOL_SCHEMA as SCP_PUT_SCHEMA
# from .tools.scp_get import scp_get, ScpGetRequest, TOOL_SCHEMA as SCP_GET_SCHEMA
# from .tools.tmux import tmux_ensure, tmux_send_keys, tmux_kill, TmuxEnsureRequest, TmuxSendKeysRequest, TmuxKillRequest, TMUX_ENSURE_SCHEMA, TMUX_SEND_KEYS_SCHEMA, TMUX_KILL_SCHEMA
# from .tools.systemd import service_action, ServiceActionRequest, SERVICE_ACTION_SCHEMA
# from .tools.django import (
#     django_manage, DjangoManageRequest, DJANGO_MANAGE_SCHEMA,
#     django_runserver_tmux, DjangoRunserverRequest, DJANGO_RUNSERVER_SCHEMA
# )

# app = FastAPI(title="MCP Pi Tool Server", version="0.2.0")

# class ToolCall(BaseModel):
#     name: str
#     arguments: Dict[str, Any]

# @app.get("/.well-known/mcp/tools")
# def list_tools():
#     return {"tools": [
#         SSH_EXEC_SCHEMA,
#         SCP_PUT_SCHEMA,
#         SCP_GET_SCHEMA,
#         TMUX_ENSURE_SCHEMA,
#         TMUX_SEND_KEYS_SCHEMA,
#         TMUX_KILL_SCHEMA,
#         SERVICE_ACTION_SCHEMA,
#         DJANGO_MANAGE_SCHEMA,
#         DJANGO_RUNSERVER_SCHEMA,
#     ]}

# @app.post("/tools")
# def call_tool(body: ToolCall):
#     try:
#         name = body.name
#         args = body.arguments

#         if name == "ssh_exec":
#             return ssh_exec(SSHExecRequest(**args)).model_dump()
#         if name == "scp_put":
#             return scp_put(ScpPutRequest(**args)).model_dump()
#         if name == "scp_get":
#             return scp_get(ScpGetRequest(**args)).model_dump()
#         if name == "tmux_ensure":
#             return tmux_ensure(TmuxEnsureRequest(**args)).model_dump()
#         if name == "tmux_send_keys":
#             return tmux_send_keys(TmuxSendKeysRequest(**args)).model_dump()
#         if name == "tmux_kill":
#             return tmux_kill(TmuxKillRequest(**args)).model_dump()
#         if name == "systemd_service":
#             return service_action(ServiceActionRequest(**args)).model_dump()
#         if name == "django_manage":
#             return django_manage(DjangoManageRequest(**args)).model_dump()
#         if name == "django_runserver_tmux":
#             return django_runserver_tmux(DjangoRunserverRequest(**args)).model_dump()

#         raise HTTPException(status_code=404, detail=f"Unknown tool: {name}")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# # Optional convenience direct endpoints (mirror the router pattern)
# @app.post("/tools/scp_put")
# def call_scp_put(args: Dict[str, Any]):
#     return scp_put(ScpPutRequest(**args)).model_dump()

# @app.post("/tools/scp_get")
# def call_scp_get(args: Dict[str, Any]):
#     return scp_get(ScpGetRequest(**args)).model_dump()

# @app.post("/tools/tmux/ensure")
# def call_tmux_ensure(args: Dict[str, Any]):
#     return tmux_ensure(TmuxEnsureRequest(**args)).model_dump()

# @app.post("/tools/tmux/send_keys")
# def call_tmux_send(args: Dict[str, Any]):
#     return tmux_send_keys(TmuxSendKeysRequest(**args)).model_dump()

# @app.post("/tools/tmux/kill")
# def call_tmux_kill(args: Dict[str, Any]):
#     return tmux_kill(TmuxKillRequest(**args)).model_dump()

# @app.post("/tools/systemd")
# def call_systemd(args: Dict[str, Any]):
#     return service_action(ServiceActionRequest(**args)).model_dump()

# @app.post("/tools/django/manage")
# def call_django_manage(args: Dict[str, Any]):
#     return django_manage(DjangoManageRequest(**args)).model_dump()

# @app.post("/tools/django/runserver_tmux")
# def call_django_runserver(args: Dict[str, Any]):
#     return django_runserver_tmux(DjangoRunserverRequest(**args)).model_dump()

# @app.get("/health")
# def health():
#     return {"status": "ok"}


from __future__ import annotations

import logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict

from .logging_setup import setup_logging
from .config import load_policies
from .security import build_cors, extract_token, verify_auth, enforce_rate_limit
from .allowlist import tool_allowed, ssh_exec_allowed, refresh_policies

from .tools.gpio_tools import (
    gpio_write, GPIOWriteRequest, TOOL_GPIO_WRITE,
    gpio_read, GPIOReadRequest, TOOL_GPIO_READ,
    gpio_pwm, GPIOPWMRequest, TOOL_GPIO_PWM,
    gpio_blink, GPIOBlinkRequest, TOOL_GPIO_BLINK,
    macro_run, GPIOMacroRequest, TOOL_GPIO_MACRO_RUN,
)
# Existing tool imports (from Parts 1 and 2)
from .tools.ssh_exec import ssh_exec, SSHExecRequest, TOOL_SCHEMA as SSH_EXEC_SCHEMA
from .tools.scp_put import scp_put, ScpPutRequest, TOOL_SCHEMA as SCP_PUT_SCHEMA
from .tools.scp_get import scp_get, ScpGetRequest, TOOL_SCHEMA as SCP_GET_SCHEMA
from .tools.tmux import (
    tmux_ensure, tmux_send_keys, tmux_kill,
    TmuxEnsureRequest, TmuxSendKeysRequest, TmuxKillRequest,
    TMUX_ENSURE_SCHEMA, TMUX_SEND_KEYS_SCHEMA, TMUX_KILL_SCHEMA
)
from .tools.git_tools import (
    git_status, GitStatusRequest, TOOL_GIT_STATUS,
    git_checkout, GitCheckoutRequest, TOOL_GIT_CHECKOUT,
    git_pull, GitPullRequest, TOOL_GIT_PULL,
    deploy_hook, DeployHookRequest, TOOL_DEPLOY_HOOK
)
from .tools.systemd import service_action, ServiceActionRequest, SERVICE_ACTION_SCHEMA
from .tools.django import (
    django_manage, DjangoManageRequest, DJANGO_MANAGE_SCHEMA,
    django_runserver_tmux, DjangoRunserverRequest, DJANGO_RUNSERVER_SCHEMA
)

# Initialize logging and app
setup_logging("INFO")
log = logging.getLogger("mcp.main")
app = FastAPI(title="MCP Pi Tool Server", version="0.3.0")

# CORS
build_cors(app)

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

def _audit(event: str, extra: Dict[str, Any]):
    # Structured audit logging with redaction handled by formatter
    log.info(event, extra={"extra": extra})

# @app.middleware("http")
# async def auth_and_rate_limit(request: Request, call_next):
#     # Allow certain endpoints without authentication
#     public_endpoints = ["/docs", "/redoc", "/openapi.json", "/health"]
#     if request.url.path in public_endpoints:
#         response = await call_next(request)
#         return response
#     
#     # Reload policies each request so edits to policies.yaml take effect dynamically
#     refresh_policies()
#     token = extract_token(request)
#     ip = request.client.host if request.client else "unknown"
#     try:
#         claims = verify_auth(token)
#         enforce_rate_limit(ip, token or "no-token")
#     except HTTPException as e:
#         _audit("auth_denied", {"ip": ip, "path": request.url.path, "detail": e.detail})
#         raise
#     request.state.auth = claims
#     response = await call_next(request)
#     return response

@app.get("/.well-known/mcp/tools")
def list_tools():
    available = [
        SSH_EXEC_SCHEMA,
        SCP_PUT_SCHEMA,
        SCP_GET_SCHEMA,
        TMUX_ENSURE_SCHEMA,
        TMUX_SEND_KEYS_SCHEMA,
        TMUX_KILL_SCHEMA,
        SERVICE_ACTION_SCHEMA,
        DJANGO_MANAGE_SCHEMA,
        DJANGO_RUNSERVER_SCHEMA,
        TOOL_GIT_STATUS,
        TOOL_GIT_CHECKOUT,
        TOOL_GIT_PULL,
        TOOL_GPIO_WRITE,
TOOL_GPIO_READ,
TOOL_GPIO_PWM,
TOOL_GPIO_BLINK,
TOOL_GPIO_MACRO_RUN,
        TOOL_DEPLOY_HOOK,
    ]
    # filtered = [t for t in available if tool_allowed(t["name"], target=None)]
    return {"tools": available}

@app.post("/tools")
def call_tool(body: ToolCall, request: Request):
    name = body.name
    args = body.arguments or {}
    target = args.get("target")

    # # Enforce tool allowlist
    # if not tool_allowed(name, target=target):
    #     _audit("tool_blocked", {"tool": name, "target": target})
    #     raise HTTPException(status_code=403, detail="Tool not allowed by policy")

    # # Extra policy: gate ssh_exec content
    # if name == "ssh_exec":
    #     cmd = args.get("command", "")
    #     if not ssh_exec_allowed(cmd):
    #         _audit("ssh_exec_blocked", {"target": target, "command": cmd})
    #         raise HTTPException(status_code=403, detail="Command not allowed by policy")

    try:
        if name == "ssh_exec":
            resp = ssh_exec(SSHExecRequest(**args)).model_dump()
        elif name == "scp_put":
            resp = scp_put(ScpPutRequest(**args)).model_dump()
        elif name == "scp_get":
            resp = scp_get(ScpGetRequest(**args)).model_dump()
        elif name == "tmux_ensure":
            resp = tmux_ensure(TmuxEnsureRequest(**args)).model_dump()
        elif name == "tmux_send_keys":
            resp = tmux_send_keys(TmuxSendKeysRequest(**args)).model_dump()
        elif name == "tmux_kill":
            resp = tmux_kill(TmuxKillRequest(**args)).model_dump()
        elif name == "systemd_service":
            resp = service_action(ServiceActionRequest(**args)).model_dump()
        elif name == "django_manage":
            resp = django_manage(DjangoManageRequest(**args)).model_dump()
        elif name == "django_runserver_tmux":
            resp = django_runserver_tmux(DjangoRunserverRequest(**args)).model_dump()
        elif name == "git_status":
            return git_status(GitStatusRequest(**args)).model_dump()
        elif name == "git_checkout":
            resp = git_checkout(GitCheckoutRequest(**args)).model_dump()
        elif name == "git_pull":
            resp = git_pull(GitPullRequest(**args)).model_dump()
        elif name == "gpio_write":
            resp = gpio_write(GPIOWriteRequest(**args)).model_dump()
        elif name == "gpio_read":
            resp = gpio_read(GPIOReadRequest(**args)).model_dump()
        elif name == "gpio_pwm":
            resp = gpio_pwm(GPIOPWMRequest(**args)).model_dump()
        elif name == "gpio_blink":
            resp = gpio_blink(GPIOBlinkRequest(**args)).model_dump()
        elif name == "macro_run":
            resp = macro_run(GPIOMacroRequest(**args)).model_dump()
        elif name == "deploy_hook":
            resp = deploy_hook(DeployHookRequest(**args)).model_dump()
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {name}")

        _audit("tool_call", {"tool": name, "target": target, "ok": True})
        return resp
    except HTTPException:
        raise
    except Exception as e:
        _audit("tool_error", {"tool": name, "target": target, "error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))

# Optional convenience direct endpoints (mirror)
@app.post("/tools/ssh_exec",
          summary="SSH Execute - Run Command on Remote Host",
          description="Execute a shell command on a remote host via SSH. Configured targets are loaded from config/hosts.yaml",
          response_description="Returns command output, error messages, and exit code")
def call_ssh_exec(args: Dict[str, Any], request: Request):
    """
    **SSH Execute Tool**
    
    Executes a shell command on a remote host via SSH.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "command": "ls -la /home/pi",
      "cwd": "/home/pi",
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin"
      },
      "timeout": 30
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `command`: Shell command to run on remote host
    - `cwd`: Working directory on remote host (optional)
    - `env`: Environment variables as key-value pairs (optional)
    - `timeout`: Timeout in seconds (optional)
    """
    return call_tool(ToolCall(name="ssh_exec", arguments=args), request)

@app.post("/tools/scp_put",
          summary="SCP Put - Upload File to Remote Host",
          description="Upload a file to the target via SFTP (content as base64). Use this to transfer files to remote hosts.",
          response_description="Returns upload status, file size, and remote path")
def call_scp_put(args: Dict[str, Any], request: Request):
    """
    **SCP Put Tool**
    
    Uploads a file to a remote host via SFTP.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "remote_path": "/home/pi/uploaded_file.txt",
      "content_b64": "SGVsbG8gV29ybGQh",
      "mode": 420
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `remote_path`: Absolute path to write on remote host
    - `content_b64`: Base64-encoded file content
    - `mode`: Octal file mode, e.g., 420 (0o644) (optional)
    """
    return call_tool(ToolCall(name="scp_put", arguments=args), request)

@app.post("/tools/scp_get",
          summary="SCP Get - Download File from Remote Host",
          description="Download a file from the target via SFTP (content as base64). Use this to retrieve files from remote hosts.",
          response_description="Returns file content as base64 and remote path")
def call_scp_get(args: Dict[str, Any], request: Request):
    """
    **SCP Get Tool**
    
    Downloads a file from a remote host via SFTP.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "remote_path": "/home/pi/config.txt"
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `remote_path`: Absolute path of file to read from remote host
    """
    return call_tool(ToolCall(name="scp_get", arguments=args), request)

@app.post("/tools/tmux/ensure",
          summary="Tmux Ensure - Create or Verify Session",
          description="Ensure a tmux session exists (create if needed). Use this to manage persistent terminal sessions on remote hosts.",
          response_description="Returns session status and creation details")
def call_tmux_ensure(args: Dict[str, Any], request: Request):
    """
    **Tmux Ensure Tool**
    
    Ensures a tmux session exists, creating it if necessary.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "session": "my_session",
      "cwd": "/home/pi/project"
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `session`: Session name (suffix); will be prefixed with 'mcp_'
    - `cwd`: Working directory for the session (optional)
    """
    return call_tool(ToolCall(name="tmux_ensure", arguments=args), request)

@app.post("/tools/tmux/send_keys",
          summary="Tmux Send Keys - Send Command to Session",
          description="Send keys/command to a tmux session (adds Enter by default). Use this to execute commands in existing tmux sessions.",
          response_description="Returns command execution status and details")
def call_tmux_send(args: Dict[str, Any], request: Request):
    """
    **Tmux Send Keys Tool**
    
    Sends keys/command to a tmux session.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "session": "my_session",
      "keys": "ls -la",
      "enter": true
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `session`: Session name (suffix); will be prefixed with 'mcp_'
    - `keys`: Command to send; will append Enter by default
    - `enter`: Whether to append Enter key (optional, defaults to true)
    """
    return call_tool(ToolCall(name="tmux_send_keys", arguments=args), request)

@app.post("/tools/tmux/kill",
          summary="Tmux Kill - Terminate Session",
          description="Kill a tmux session. Use this to clean up and terminate tmux sessions on remote hosts.",
          response_description="Returns session termination status and details")
def call_tmux_kill(args: Dict[str, Any], request: Request):
    """
    **Tmux Kill Tool**
    
    Kills a tmux session.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "session": "my_session"
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `session`: Session name (suffix); will be prefixed with 'mcp_'
    """
    return call_tool(ToolCall(name="tmux_kill", arguments=args), request)

@app.post("/tools/systemd",
          summary="Systemd Service - Manage Services",
          description="Manage a systemd service on the target. Use this to start, stop, restart, enable, disable, or check status of services.",
          response_description="Returns service operation status, output, and exit code")
def call_systemd(args: Dict[str, Any], request: Request):
    """
    **Systemd Service Tool**
    
    Manages systemd services on remote hosts.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "name": "nginx.service",
      "action": "start"
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `name`: systemd service name (e.g., 'nginx.service', 'myapp.service')
    - `action`: One of: start, stop, restart, reload, enable, disable, status
    """
    return call_tool(ToolCall(name="systemd_service", arguments=args), request)

@app.post("/tools/django/manage",
          summary="Django Manage - Run Management Commands",
          description="Run python manage.py with given args (migrate, collectstatic, etc.). Use this to execute Django management commands on remote hosts.",
          response_description="Returns command output, error messages, and exit code")
def call_django_manage(args: Dict[str, Any], request: Request):
    """
    **Django Manage Tool**
    
    Runs Django management commands on remote hosts.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "project_dir": "/home/pi/myproject",
      "manage_args": "migrate",
      "venv_path": "/home/pi/myproject/.venv/bin",
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings"
      },
      "timeout": 60
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `project_dir`: Remote project working directory (contains manage.py)
    - `manage_args`: Arguments to manage.py (e.g., 'migrate', 'collectstatic --noinput')
    - `venv_path`: Remote virtualenv bin path (optional)
    - `env`: Environment variables as key-value pairs (optional)
    - `timeout`: Timeout in seconds (optional)
    """
    return call_tool(ToolCall(name="django_manage", arguments=args), request)

@app.post("/tools/django/runserver_tmux",
          summary="Django Runserver - Start Dev Server in Tmux",
          description="Run Django dev server in a tmux session (sends Ctrl-C first, then runserver). Use this to start Django development servers on remote hosts.",
          response_description="Returns server startup status and session details")
def call_django_runserver(args: Dict[str, Any], request: Request):
    """
    **Django Runserver Tool**
    
    Runs Django development server in a tmux session on remote hosts.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "project_dir": "/home/pi/myproject",
      "session": "django_server",
      "host": "0.0.0.0",
      "port": 8000,
      "venv_path": "/home/pi/myproject/.venv/bin",
      "extra_args": "--settings=myproject.settings"
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `project_dir`: Remote project working directory (contains manage.py)
    - `session`: Tmux session suffix to use (will be prefixed)
    - `host`: Host to bind to (optional, defaults to '0.0.0.0')
    - `port`: Port to bind to (optional, defaults to 8000)
    - `venv_path`: Remote virtualenv bin path (optional)
    - `extra_args`: Extra args, e.g., '--settings=...' (optional)
    - `env`: Environment variables as key-value pairs (optional)
    - `timeout`: Timeout in seconds (optional)
    """
    return call_tool(ToolCall(name="django_runserver_tmux", arguments=args), request)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/gpio/examples")
def gpio_examples():
    """
    **GPIO Examples Collection**
    
    Returns a collection of ready-to-use JSON examples for all GPIO tools.
    """
    return {
        "gpio_write_examples": {
            "basic_high": {
                "target": "pi-lan",
                "pin": 17,
                "value": 1,
                "mode": "BCM"
            },
            "basic_low": {
                "target": "pi-lan",
                "pin": 17,
                "value": 0,
                "mode": "BCM"
            },
            "boolean_true": {
                "target": "pi-lan",
                "pin": 18,
                "value": True,
                "mode": "BCM"
            }
        },
        "gpio_read_examples": {
            "basic_read": {
                "target": "pi-lan",
                "pin": 17,
                "mode": "BCM"
            },
            "with_pullup": {
                "target": "pi-lan",
                "pin": 18,
                "mode": "BCM",
                "pull": "up"
            }
        },
        "gpio_pwm_examples": {
            "basic_pwm": {
                "target": "pi-lan",
                "pin": 18,
                "duty": 50.0,
                "freq": 1000.0,
                "duration": 2.0,
                "mode": "BCM"
            },
            "servo_control": {
                "target": "pi-lan",
                "pin": 18,
                "duty": 7.5,
                "freq": 50.0,
                "duration": 1.0,
                "mode": "BCM"
            }
        },
        "gpio_blink_examples": {
            "basic_blink": {
                "target": "pi-lan",
                "pin": 17,
                "count": 5,
                "on_time": 0.5,
                "off_time": 0.5,
                "mode": "BCM"
            },
            "fast_blink": {
                "target": "pi-lan",
                "pin": 18,
                "count": 10,
                "on_time": 0.1,
                "off_time": 0.1,
                "mode": "BCM"
            }
        },
        "gpio_macro_examples": {
            "simple_sequence": {
                "target": "pi-lan",
                "steps": [
                    {
                        "op": "write",
                        "data": {"pin": 17, "value": 1, "mode": "BCM"}
                    },
                    {
                        "op": "blink",
                        "data": {"pin": 18, "count": 3, "on_time": 0.2, "off_time": 0.2, "mode": "BCM"}
                    },
                    {
                        "op": "write",
                        "data": {"pin": 17, "value": 0, "mode": "BCM"}
                    }
                ],
                "mode": "BCM"
            }
        },
        "available_pins": {
            "bcm": [17, 18, 22, 23, 24, 25],
            "board": [11, 12, 13, 15, 16, 18, 22],
            "pwm_capable": [18, 22, 23, 24, 25]
        },
        "targets": ["pi-lan"]
    }


@app.post("/tools/git/status",
          summary="Git Status - Check Repository Status",
          description="Get git status for a project directory. Use this to check the current state of git repositories on remote hosts.",
          response_description="Returns git status output, error messages, and exit code")
def call_git_status(args: Dict[str, Any], request: Request):
    """
    **Git Status Tool**
    
    Gets git status for a project directory on remote hosts.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "project_dir": "/home/pi/myproject",
      "short": true
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `project_dir`: Remote project directory containing the git repo
    - `short`: If true, runs 'git status --short --branch' else full 'git status' (optional, defaults to true)
    """
    return call_tool(ToolCall(name="git_status", arguments=args), request)

@app.post("/tools/git/checkout",
          summary="Git Checkout - Switch Branch or Tag",
          description="Checkout a branch or tag in the git repo. Use this to switch between different branches or tags on remote hosts.",
          response_description="Returns checkout operation output, error messages, and exit code")
def call_git_checkout(args: Dict[str, Any], request: Request):
    """
    **Git Checkout Tool**
    
    Checks out a branch or tag in the git repository on remote hosts.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "project_dir": "/home/pi/myproject",
      "ref": "main",
      "create_branch": false
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `project_dir`: Remote project directory containing the git repo
    - `ref`: Branch or tag to checkout, e.g., 'main' or 'v1.2.3'
    - `create_branch`: If true, create a new branch from current HEAD (optional, defaults to false)
    """
    return call_tool(ToolCall(name="git_checkout", arguments=args), request)

@app.post("/tools/git/pull",
          summary="Git Pull - Update Repository",
          description="Pull updates from remote; optional fetch --all/prune and reset --hard. Use this to update git repositories on remote hosts.",
          response_description="Returns pull operation output, error messages, and exit code")
def call_git_pull(args: Dict[str, Any], request: Request):
    """
    **Git Pull Tool**
    
    Pulls updates from remote git repositories on remote hosts.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "project_dir": "/home/pi/myproject",
      "remote": "origin",
      "branch": "main",
      "fetch_all": true,
      "reset_hard": false
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `project_dir`: Remote project directory containing the git repo
    - `remote`: Remote name to pull from (optional, defaults to 'origin')
    - `branch`: Branch to pull; if omitted, pulls current branch (optional)
    - `fetch_all`: If true, runs 'git fetch --all --prune' first (optional, defaults to false)
    - `reset_hard`: If true, 'git reset --hard <remote>/<branch>' after fetch (optional, defaults to false)
    """
    return call_tool(ToolCall(name="git_pull", arguments=args), request)

@app.post("/tools/deploy/hook",
          summary="Deploy Hook - Run Deployment Script",
          description="Run a controlled deploy script in the project directory (e.g., migrations, collectstatic, restart). Use this to execute deployment scripts on remote hosts.",
          response_description="Returns deployment script output, error messages, and exit code")
def call_deploy_hook(args: Dict[str, Any], request: Request):
    """
    **Deploy Hook Tool**
    
    Runs deployment scripts on remote hosts.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "project_dir": "/home/pi/myproject",
      "script": "deploy.sh",
      "env": {
        "ENVIRONMENT": "production",
        "DJANGO_SETTINGS_MODULE": "myproject.settings"
      },
      "timeout": 600
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config.targets (e.g., 'pi-lan')
    - `project_dir`: Remote project directory containing deploy.sh
    - `script`: Hook script filename inside project_dir (optional, defaults to 'deploy.sh')
    - `env`: Extra environment variables as key-value pairs (optional)
    - `timeout`: Timeout seconds for the full deploy (optional, defaults to 600)
    """
    return call_tool(ToolCall(name="deploy_hook", arguments=args), request)


@app.post("/tools/gpio/write", 
          summary="GPIO Write - Set Pin HIGH/LOW",
          description="Set a GPIO pin to HIGH (1) or LOW (0). Use this to control LEDs, relays, or other digital outputs.",
          response_description="Returns success status and operation details")
def call_gpio_write(args: Dict[str, Any], request: Request):
    """
    **GPIO Write Tool**
    
    Sets a GPIO pin to HIGH or LOW state.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "pin": 17,
      "value": 1,
      "mode": "BCM",
      "direction": "out"
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config (use "pi-lan")
    - `pin`: GPIO pin number (17, 18, 22, 23, 24, 25)
    - `value`: 0/1 or true/false
    - `mode`: "BCM" or "BOARD" (optional, defaults to BCM)
    - `direction`: "out" (optional, defaults to "out")
    """
    return call_tool(ToolCall(name="gpio_write", arguments=args), request)

@app.post("/tools/gpio/read",
          summary="GPIO Read - Read Pin State",
          description="Read the current state of a GPIO pin. Use this to read button states, sensor outputs, or other digital inputs.",
          response_description="Returns the pin value (0 or 1) and operation details")
def call_gpio_read(args: Dict[str, Any], request: Request):
    """
    **GPIO Read Tool**
    
    Reads the current state of a GPIO pin.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "pin": 17,
      "mode": "BCM",
      "direction": "in",
      "pull": "up"
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config (use "pi-lan")
    - `pin`: GPIO pin number (17, 18, 22, 23, 24, 25)
    - `mode`: "BCM" or "BOARD" (optional, defaults to BCM)
    - `direction`: "in" (optional, defaults to "in")
    - `pull`: "up", "down", or "off" (optional)
    """
    return call_tool(ToolCall(name="gpio_read", arguments=args), request)

@app.post("/tools/gpio/pwm",
          summary="GPIO PWM - Pulse Width Modulation",
          description="Control PWM on a GPIO pin. Use this for motor speed control, servo positioning, or LED brightness control.",
          response_description="Returns PWM operation status and details")
def call_gpio_pwm(args: Dict[str, Any], request: Request):
    """
    **GPIO PWM Tool**
    
    Sets PWM (Pulse Width Modulation) on a GPIO pin.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "pin": 18,
      "duty": 50.0,
      "freq": 1000.0,
      "duration": 2.0,
      "mode": "BCM"
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config (use "pi-lan")
    - `pin`: GPIO pin number (18, 22, 23, 24, 25 - PWM capable)
    - `duty`: Duty cycle percentage (0.0 to 100.0)
    - `freq`: Frequency in Hz (default: 1000.0)
    - `duration`: Duration in seconds (default: 0.2)
    - `mode`: "BCM" or "BOARD" (optional, defaults to BCM)
    """
    return call_tool(ToolCall(name="gpio_pwm", arguments=args), request)

@app.post("/tools/gpio/blink",
          summary="GPIO Blink - LED Blinking",
          description="Blink a GPIO pin (LED) a specified number of times with custom timing. Perfect for status indicators and attention-grabbing patterns.",
          response_description="Returns blink operation status and completion details")
def call_gpio_blink(args: Dict[str, Any], request: Request):
    """
    **GPIO Blink Tool**
    
    Blinks a GPIO pin (LED) a specified number of times.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "pin": 17,
      "count": 5,
      "on_time": 0.5,
      "off_time": 0.5,
      "mode": "BCM"
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config (use "pi-lan")
    - `pin`: GPIO pin number (17, 18, 22, 23, 24, 25)
    - `count`: Number of blinks (default: 5)
    - `on_time`: Seconds LED is ON (default: 0.5)
    - `off_time`: Seconds LED is OFF (default: 0.5)
    - `mode`: "BCM" or "BOARD" (optional, defaults to BCM)
    """
    return call_tool(ToolCall(name="gpio_blink", arguments=args), request)

@app.post("/tools/gpio/macro_run",
          summary="GPIO Macro - Complex Sequences",
          description="Run a sequence of GPIO operations (write, read, pwm, blink) in order. Perfect for complex automation and coordinated device control.",
          response_description="Returns macro execution status and results for each step")
def call_gpio_macro(args: Dict[str, Any], request: Request):
    """
    **GPIO Macro Tool**
    
    Runs a sequence of GPIO operations in order.
    
    **Example JSON:**
    ```json
    {
      "target": "pi-lan",
      "steps": [
        {
          "op": "write",
          "data": {
            "pin": 17,
            "value": 1,
            "mode": "BCM"
          }
        },
        {
          "op": "blink",
          "data": {
            "pin": 18,
            "count": 3,
            "on_time": 0.2,
            "off_time": 0.2,
            "mode": "BCM"
          }
        },
        {
          "op": "write",
          "data": {
            "pin": 17,
            "value": 0,
            "mode": "BCM"
          }
        }
      ],
      "mode": "BCM"
    }
    ```
    
    **Parameters:**
    - `target`: Target name from config (use "pi-lan")
    - `steps`: Array of GPIO operations
    - `mode`: "BCM" or "BOARD" (optional, defaults to BCM)
    
    **Step Operations:**
    - `write`: Set pin HIGH/LOW
    - `read`: Read pin state
    - `pwm`: PWM control
    - `blink`: Blink LED
    """
    return call_tool(ToolCall(name="macro_run", arguments=args), request)