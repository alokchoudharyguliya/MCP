from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

from .common import TargetedRequest, use_client

SESSION_PREFIX = "mcp_"

class TmuxEnsureRequest(TargetedRequest):
    session: str = Field(description="Session name (suffix); will be prefixed with 'mcp_'")
    cwd: Optional[str] = None

class TmuxSendKeysRequest(TargetedRequest):
    session: str
    keys: str = Field(description="Command to send; will append Enter by default")
    enter: bool = True

class TmuxKillRequest(TargetedRequest):
    session: str

class TmuxResponse(BaseModel):
    ok: bool
    session: str
    detail: str

def _full_session(name: str) -> str:
    return f"{SESSION_PREFIX}{name}"

def tmux_ensure(req: TmuxEnsureRequest) -> TmuxResponse:
    sess = _full_session(req.session)
    cli = use_client(req.target)
    with cli:
        # Check session exists
        exists = cli.exec(f"tmux has-session -t {sess}", timeout=5)
        if exists.exit_code != 0:
            # Create session with shell
            create = cli.exec(f"tmux new-session -d -s {sess}", cwd=req.cwd)
            if create.exit_code != 0:
                return TmuxResponse(ok=False, session=sess, detail=create.stderr or create.stdout)
        return TmuxResponse(ok=True, session=sess, detail="ensured")

def tmux_send_keys(req: TmuxSendKeysRequest) -> TmuxResponse:
    sess = _full_session(req.session)
    cli = use_client(req.target)
    with cli:
        cmd = f"tmux send-keys -t {sess} {repr(req.keys)}"
        if req.enter:
            cmd += " Enter"
        r = cli.exec(cmd)
        ok = (r.exit_code == 0)
        return TmuxResponse(ok=ok, session=sess, detail=r.stderr or r.stdout)

def tmux_kill(req: TmuxKillRequest) -> TmuxResponse:
    sess = _full_session(req.session)
    cli = use_client(req.target)
    with cli:
        r = cli.exec(f"tmux kill-session -t {sess}")
        ok = (r.exit_code == 0)
        return TmuxResponse(ok=ok, session=sess, detail=r.stderr or r.stdout)

TMUX_ENSURE_SCHEMA = {
    "name": "tmux_ensure",
    "description": "Ensure a tmux session exists (create if needed).",
    "input_schema": {
        "type": "object",
        "properties": {"target": {"type": "string"}, "session": {"type": "string"}, "cwd": {"type": "string"}},
        "required": ["target", "session"]
    },
    "output_schema": {
        "type": "object",
        "properties": {"ok": {"type": "boolean"}, "session": {"type": "string"}, "detail": {"type": "string"}},
        "required": ["ok", "session"]
    }
}

TMUX_SEND_KEYS_SCHEMA = {
    "name": "tmux_send_keys",
    "description": "Send keys/command to a tmux session (adds Enter by default).",
    "input_schema": {
        "type": "object",
        "properties": {"target": {"type": "string"}, "session": {"type": "string"}, "keys": {"type": "string"}, "enter": {"type": "boolean"}},
        "required": ["target", "session", "keys"]
    },
    "output_schema": TMUX_ENSURE_SCHEMA["output_schema"]
}

TMUX_KILL_SCHEMA = {
    "name": "tmux_kill",
    "description": "Kill a tmux session.",
    "input_schema": {
        "type": "object",
        "properties": {"target": {"type": "string"}, "session": {"type": "string"}},
        "required": ["target", "session"]
    },
    "output_schema": TMUX_ENSURE_SCHEMA["output_schema"]
}