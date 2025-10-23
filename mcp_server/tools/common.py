from __future__ import annotations
from typing import Dict, Any
from pydantic import BaseModel, Field
from ..config import load_config
from ..ssh_transport import SSHClientWrapper

class TargetedRequest(BaseModel):
    target: str = Field(description="Target name from config.targets")

def use_client(target: str) -> SSHClientWrapper:
    cfg = load_config()
    if target not in cfg.targets:
        raise ValueError(f"Unknown target: {target}")
    return SSHClientWrapper(cfg.targets[target])