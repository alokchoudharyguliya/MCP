from __future__ import annotations
import base64
from typing import Optional
from pydantic import BaseModel, Field

from .common import TargetedRequest, use_client

class ScpPutRequest(TargetedRequest):
    remote_path: str = Field(description="Absolute path to write on remote host")
    content_b64: str = Field(description="Base64-encoded file content")
    mode: Optional[int] = Field(default=None, description="Octal file mode, e.g., 0o644")

class ScpPutResponse(BaseModel):
    remote_path: str
    size: int
    mode: Optional[int] = None

def scp_put(req: ScpPutRequest) -> ScpPutResponse:
    data = base64.b64decode(req.content_b64)
    cli = use_client(req.target)
    with cli:
        cli.put_bytes(data, req.remote_path, req.mode)
    return ScpPutResponse(remote_path=req.remote_path, size=len(data), mode=req.mode)

TOOL_SCHEMA = {
    "name": "scp_put",
    "description": "Upload a file to the target via SFTP (content as base64)",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "remote_path": {"type": "string"},
            "content_b64": {"type": "string"},
            "mode": {"type": "integer"},
        },
        "required": ["target", "remote_path", "content_b64"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "remote_path": {"type": "string"},
            "size": {"type": "integer"},
            "mode": {"type": "integer"},
        },
        "required": ["remote_path", "size"]
    }
}