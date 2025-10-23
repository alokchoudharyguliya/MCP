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
POLICY_PATH = os.environ.get("MCP_PI_POLICY", "config/policies.yaml")  # GPIO config only

class TargetConfig(BaseModel):
    host: str
    port: int = 22
    username: str
    private_key_path: str
    known_hosts_path: Optional[str] = None
    connect_timeout: int = 10

# POLICY SYSTEM DISABLED - Policy configuration classes commented out
# class SecurityConfig(BaseModel):
#     api_keys: List[str] = Field(default_factory=list)  # simple shared-secret API keys
#     jwt_public_key_pem: Optional[str] = None           # optional JWT verification key (PEM)
#     cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])
#     rate_limit_per_minute: int = 60

# class AllowlistConfig(BaseModel):
#     # Tool-level control
#     enabled_tools: List[str] = Field(default_factory=list)  # if non-empty, only these tools are enabled

#     # Command-level control for ssh_exec
#     ssh_exec_allowed_prefixes: List[str] = Field(default_factory=list)  # commands must start with one of these
#     ssh_exec_denied_substrings: List[str] = Field(default_factory=list)  # deny if any substring present

#     # Per-target tool enablement (optional)
#     per_target_tools: Dict[str, List[str]] = Field(default_factory=dict)

class AppConfig(BaseModel):
    targets: Dict[str, TargetConfig] = Field(default_factory=dict)

# class GPIOConfig(BaseModel):
#     targets: Dict[str, Any] = Field(default_factory=dict)

# class PolicyConfig(BaseModel):
#     security: SecurityConfig = Field(default_factory=SecurityConfig)
#     allowlist: AllowlistConfig = Field(default_factory=AllowlistConfig)
#     gpio: GPIOConfig = Field(default_factory=GPIOConfig)

def load_config(path: str = CONFIG_PATH) -> AppConfig:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = yaml.safe_load(f) or {}
    return AppConfig(**data)

# GPIO configuration loading (separate from security policies)
def load_policies(path: str = POLICY_PATH) -> "PolicyConfig":
    """
    Load policies configuration for GPIO hardware safety.
    Security policies are disabled, but GPIO config is still needed.
    """
    try:
        if not os.path.exists(path):
            # Return minimal config with just GPIO structure
            return type('PolicyConfig', (), {
                'gpio': type('GPIOConfig', (), {
                    'targets': {}
                })()
            })()
        
        with open(path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f) or {}
        
        # Only load GPIO configuration, ignore security policies
        gpio_data = data.get('gpio', {})
        
        # Create minimal policy object with only GPIO config
        policy_obj = type('PolicyConfig', (), {
            'gpio': type('GPIOConfig', (), {
                'targets': gpio_data.get('targets', {})
            })()
        })()
        
        return policy_obj
        
    except Exception as e:
        # If loading fails, return empty GPIO config
        import logging
        log = logging.getLogger("mcp.config")
        log.warning(f"Failed to load GPIO policies from {path}: {e}")
        return type('PolicyConfig', (), {
            'gpio': type('GPIOConfig', (), {
                'targets': {}
            })()
        })()