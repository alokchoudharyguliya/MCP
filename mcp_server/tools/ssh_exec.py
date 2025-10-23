from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from ..config import load_config
from ..ssh_transport import SSHClientWrapper

class SSHExecRequest(BaseModel):
    target: str = Field(description="Target name from config.targets (e.g., 'pi-lan')")
    command: str = Field(description="Shell command to run on remote host")
    cwd: Optional[str] = Field(default=None, description="Working directory on remote host")
    env: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    timeout: Optional[int] = Field(default=None, description="Timeout in seconds")

class SSHExecResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int

def ssh_exec(req: SSHExecRequest) -> SSHExecResponse:
    cfg = load_config()
    if req.target not in cfg.targets:
        raise ValueError(f"Unknown target: {req.target}")

    target_cfg = cfg.targets[req.target]
    with SSHClientWrapper(target_cfg) as cli:
        result = cli.exec(req.command, cwd=req.cwd, env=req.env, timeout=req.timeout)
        return SSHExecResponse(stdout=result.stdout, stderr=result.stderr, exit_code=result.exit_code)

# Tool schema (MCP-style description)
TOOL_SCHEMA = {
    "name": "ssh_exec",
    "description": "Execute a command over SSH on a configured target",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "command": {"type": "string"},
            "cwd": {"type": "string"},
            "env": {"type": "object", "additionalProperties": {"type": "string"}},
            "timeout": {"type": "integer"},
        },
        "required": ["target", "command"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "stdout": {"type": "string"},
            "stderr": {"type": "string"},
            "exit_code": {"type": "integer"}
        },
        "required": ["stdout", "stderr", "exit_code"]
    }
}