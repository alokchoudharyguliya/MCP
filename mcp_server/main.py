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

@app.middleware("http")
async def auth_and_rate_limit(request: Request, call_next):
    # Allow certain endpoints without authentication
    public_endpoints = ["/docs", "/redoc", "/openapi.json", "/health"]
    if request.url.path in public_endpoints:
        response = await call_next(request)
        return response
    
    # Reload policies each request so edits to policies.yaml take effect dynamically
    refresh_policies()
    token = extract_token(request)
    ip = request.client.host if request.client else "unknown"
    try:
        claims = verify_auth(token)
        enforce_rate_limit(ip, token or "no-token")
    except HTTPException as e:
        _audit("auth_denied", {"ip": ip, "path": request.url.path, "detail": e.detail})
        raise
    request.state.auth = claims
    response = await call_next(request)
    return response

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
        TOOL_DEPLOY_HOOK,
    ]
    filtered = [t for t in available if tool_allowed(t["name"], target=None)]
    return {"tools": filtered}

@app.post("/tools")
def call_tool(body: ToolCall, request: Request):
    name = body.name
    args = body.arguments or {}
    target = args.get("target")

    # Enforce tool allowlist
    if not tool_allowed(name, target=target):
        _audit("tool_blocked", {"tool": name, "target": target})
        raise HTTPException(status_code=403, detail="Tool not allowed by policy")

    # Extra policy: gate ssh_exec content
    if name == "ssh_exec":
        cmd = args.get("command", "")
        if not ssh_exec_allowed(cmd):
            _audit("ssh_exec_blocked", {"target": target, "command": cmd})
            raise HTTPException(status_code=403, detail="Command not allowed by policy")

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
@app.post("/tools/ssh_exec")
def call_ssh_exec(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="ssh_exec", arguments=args), request)

@app.post("/tools/scp_put")
def call_scp_put(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="scp_put", arguments=args), request)

@app.post("/tools/scp_get")
def call_scp_get(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="scp_get", arguments=args), request)

@app.post("/tools/tmux/ensure")
def call_tmux_ensure(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="tmux_ensure", arguments=args), request)

@app.post("/tools/tmux/send_keys")
def call_tmux_send(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="tmux_send_keys", arguments=args), request)

@app.post("/tools/tmux/kill")
def call_tmux_kill(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="tmux_kill", arguments=args), request)

@app.post("/tools/systemd")
def call_systemd(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="systemd_service", arguments=args), request)

@app.post("/tools/django/manage")
def call_django_manage(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="django_manage", arguments=args), request)

@app.post("/tools/django/runserver_tmux")
def call_django_runserver(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="django_runserver_tmux", arguments=args), request)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tools/git/status")
def call_git_status(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="git_status", arguments=args), request)

@app.post("/tools/git/checkout")
def call_git_checkout(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="git_checkout", arguments=args), request)

@app.post("/tools/git/pull")
def call_git_pull(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="git_pull", arguments=args), request)

@app.post("/tools/deploy/hook")
def call_deploy_hook(args: Dict[str, Any], request: Request):
    return call_tool(ToolCall(name="deploy_hook", arguments=args), request)