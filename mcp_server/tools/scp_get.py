from __future__ import annotations
import base64
from pydantic import BaseModel, Field

from .common import TargetedRequest, use_client

class ScpGetRequest(TargetedRequest):
    remote_path: str = Field(description="Absolute path of file to read from remote host")

class ScpGetResponse(BaseModel):
    remote_path: str
    content_b64: str

def scp_get(req: ScpGetRequest) -> ScpGetResponse:
    cli = use_client(req.target)
    with cli:
        data = cli.get_bytes(req.remote_path)
    return ScpGetResponse(remote_path=req.remote_path, content_b64=base64.b64encode(data).decode("ascii"))

TOOL_SCHEMA = {
    "name": "scp_get",
    "description": "Download a file from the target via SFTP (content as base64)",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "remote_path": {"type": "string"},
        },
        "required": ["target", "remote_path"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "remote_path": {"type": "string"},
            "content_b64": {"type": "string"},
        },
        "required": ["remote_path", "content_b64"]
    }
}