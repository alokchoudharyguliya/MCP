# from __future__ import annotations

# import os
# from typing import Dict, Optional, Any
# import yaml
# from pydantic import BaseModel, Field

# CONFIG_PATH = os.environ.get("MCP_PI_CONFIG", "config/hosts.yaml")

# class TargetConfig(BaseModel):
#     host: str
#     port: int = 22
#     username: str
#     private_key_path: str
#     known_hosts_path: Optional[str] = None
#     connect_timeout: int = 10

# class AppConfig(BaseModel):
#     targets: Dict[str, TargetConfig] = Field(default_factory=dict)

# def load_config(path: str = CONFIG_PATH) -> AppConfig:
#     if not os.path.exists(path):
#         raise FileNotFoundError(f"Config file not found: {path}")
#     with open(path, "r", encoding="utf-8") as f:
#         data: Dict[str, Any] = yaml.safe_load(f) or {}
#     return AppConfig(**data)


from __future__ import annotations

import os
from typing import Dict, Optional, Any, List
import yaml
from pydantic import BaseModel, Field

CONFIG_PATH = os.environ.get("MCP_PI_CONFIG", "config/hosts.yaml")
POLICY_PATH = os.environ.get("MCP_PI_POLICY", "config/policies.yaml")

class TargetConfig(BaseModel):
    host: str
    port: int = 22
    username: str
    private_key_path: str
    known_hosts_path: Optional[str] = None
    connect_timeout: int = 10

class SecurityConfig(BaseModel):
    api_keys: List[str] = Field(default_factory=list)  # simple shared-secret API keys
    jwt_public_key_pem: Optional[str] = None           # optional JWT verification key (PEM)
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = 60

class AllowlistConfig(BaseModel):
    # Tool-level control
    enabled_tools: List[str] = Field(default_factory=list)  # if non-empty, only these tools are enabled

    # Command-level control for ssh_exec
    ssh_exec_allowed_prefixes: List[str] = Field(default_factory=list)  # commands must start with one of these
    ssh_exec_denied_substrings: List[str] = Field(default_factory=list)  # deny if any substring present

    # Per-target tool enablement (optional)
    per_target_tools: Dict[str, List[str]] = Field(default_factory=dict)

class AppConfig(BaseModel):
    targets: Dict[str, TargetConfig] = Field(default_factory=dict)

class PolicyConfig(BaseModel):
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    allowlist: AllowlistConfig = Field(default_factory=AllowlistConfig)

def load_config(path: str = CONFIG_PATH) -> AppConfig:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = yaml.safe_load(f) or {}
    return AppConfig(**data)

def load_policies(path: str = POLICY_PATH) -> PolicyConfig:
    if not os.path.exists(path):
        # Provide defaults if no policy file present
        return PolicyConfig()
    with open(path, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = yaml.safe_load(f) or {}
    
    # Handle None values for per_target_tools
    if "allowlist" in data and "per_target_tools" in data["allowlist"]:
        if data["allowlist"]["per_target_tools"] is None:
            data["allowlist"]["per_target_tools"] = {}
    
    return PolicyConfig(**data)