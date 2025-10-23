from __future__ import annotations
from pydantic import BaseModel, Field

from .common import TargetedRequest, use_client

class ServiceRequest(TargetedRequest):
    name: str = Field(description="systemd service name (e.g., myproj.service)")

class ServiceActionRequest(ServiceRequest):
    action: str = Field(description="one of: start|stop|restart|reload|enable|disable|status")

class ServiceResponse(BaseModel):
    ok: bool
    name: str
    action: str
    stdout: str
    stderr: str
    exit_code: int

VALID_ACTIONS = {"start", "stop", "restart", "reload", "enable", "disable", "status"}

def service_action(req: ServiceActionRequest) -> ServiceResponse:
    if req.action not in VALID_ACTIONS:
        raise ValueError(f"Invalid action: {req.action}")
    cli = use_client(req.target)
    with cli:
        r = cli.exec(f"systemctl {req.action} {req.name}")
        return ServiceResponse(ok=(r.exit_code == 0), name=req.name, action=req.action, stdout=r.stdout, stderr=r.stderr, exit_code=r.exit_code)

SERVICE_ACTION_SCHEMA = {
    "name": "systemd_service",
    "description": "Manage a systemd service on the target.",
    "input_schema": {
        "type": "object",
        "properties": {"target": {"type": "string"}, "name": {"type": "string"}, "action": {"type": "string", "enum": sorted(list(VALID_ACTIONS))}},
        "required": ["target", "name", "action"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "ok": {"type": "boolean"},
            "name": {"type": "string"},
            "action": {"type": "string"},
            "stdout": {"type": "string"},
            "stderr": {"type": "string"},
            "exit_code": {"type": "integer"},
        },
        "required": ["ok", "name", "action", "exit_code"]
    }
}