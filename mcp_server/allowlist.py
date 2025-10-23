# POLICY SYSTEM DISABLED - All allowlist functions commented out
# from __future__ import annotations
# from typing import List, Dict
# from .config import load_policies

# _policies = load_policies()

# def refresh_policies():
#     global _policies
#     _policies = load_policies()

# def tool_allowed(tool_name: str, target: str | None = None) -> bool:
#     al = _policies.allowlist
#     # If enabled_tools is non-empty, tool must be in it
#     if al.enabled_tools and tool_name not in al.enabled_tools:
#         return False
#     # If per-target restriction exists, enforce it
#     if target and target in al.per_target_tools:
#         return tool_name in al.per_target_tools[target]
#     return True

# def ssh_exec_allowed(command: str) -> bool:
#     al = _policies.allowlist
#     # deny substrings first
#     for s in al.ssh_exec_denied_substrings:
#         if s in command:
#             return False
#     # if prefixes defined, require one to match
#     if al.ssh_exec_allowed_prefixes:
#         return any(command.strip().startswith(p) for p in al.ssh_exec_allowed_prefixes)
#     return True