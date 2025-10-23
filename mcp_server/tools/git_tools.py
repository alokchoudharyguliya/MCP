from __future__ import annotations
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator

from ..config import load_config
from ..ssh_transport import SSHClientWrapper
from .common import TargetedRequest, use_client

# Shared validation helpers
SAFE_BRANCH_TAG = r"^[A-Za-z0-9._/\-]+$"  # simple safe pattern (no spaces, no shell metachars)

def _mk_env_prefix(env: Optional[Dict[str, str]]) -> str:
    if not env:
        return ""
    exports = " ".join([f'{k}="{str(v).replace(chr(34), chr(92)+chr(34))}"' for k, v in env.items()])
    return f"export {exports}; "

# 1) git_status
class GitStatusRequest(TargetedRequest):
    project_dir: str = Field(description="Remote project directory containing the git repo")
    short: bool = Field(default=True, description="If true, runs 'git status --short --branch' else full 'git status'")

class GitStatusResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int

def git_status(req: GitStatusRequest) -> GitStatusResponse:
    with use_client(req.target) as cli:
        cmd = "git status --short --branch" if req.short else "git status"
        r = cli.exec(cmd, cwd=req.project_dir)
        return GitStatusResponse(stdout=r.stdout, stderr=r.stderr, exit_code=r.exit_code)

TOOL_GIT_STATUS = {
    "name": "git_status",
    "description": "Get git status for a project directory.",
    "input_schema": {
        "type": "object",
        "properties": {"target": {"type": "string"}, "project_dir": {"type": "string"}, "short": {"type": "boolean"}},
        "required": ["target", "project_dir"]
    },
    "output_schema": {
        "type": "object",
        "properties": {"stdout": {"type": "string"}, "stderr": {"type": "string"}, "exit_code": {"type": "integer"}},
        "required": ["stdout", "stderr", "exit_code"]
    }
}

# 2) git_checkout (branch or tag)
class GitCheckoutRequest(TargetedRequest):
    project_dir: str = Field(description="Remote project directory containing the git repo")
    ref: str = Field(description="Branch or tag to checkout, e.g., 'main' or 'v1.2.3'")
    create_branch: bool = Field(default=False, description="If true, create a new branch from current HEAD")

    @validator("ref")
    def validate_ref(cls, v: str) -> str:
        import re
        if not re.match(SAFE_BRANCH_TAG, v):
            raise ValueError("Invalid ref; allowed: letters, digits, . _ / -")
        return v

class GitCheckoutResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    ref: str

def git_checkout(req: GitCheckoutRequest) -> GitCheckoutResponse:
    with use_client(req.target) as cli:
        if req.create_branch:
            cmd = f"git checkout -b {req.ref}"
        else:
            cmd = f"git checkout {req.ref}"
        r = cli.exec(cmd, cwd=req.project_dir)
        return GitCheckoutResponse(stdout=r.stdout, stderr=r.stderr, exit_code=r.exit_code, ref=req.ref)

TOOL_GIT_CHECKOUT = {
    "name": "git_checkout",
    "description": "Checkout a branch or tag in the git repo.",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "project_dir": {"type": "string"},
            "ref": {"type": "string"},
            "create_branch": {"type": "boolean"}
        },
        "required": ["target", "project_dir", "ref"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "stdout": {"type": "string"},
            "stderr": {"type": "string"},
            "exit_code": {"type": "integer"},
            "ref": {"type": "string"},
        },
        "required": ["stdout", "stderr", "exit_code", "ref"]
    }
}

# 3) git_pull (optionally set remote and branch)
class GitPullRequest(TargetedRequest):
    project_dir: str = Field(description="Remote project directory containing the git repo")
    remote: str = Field(default="origin", description="Remote name to pull from")
    branch: Optional[str] = Field(default=None, description="Branch to pull; if omitted, pulls current branch")
    fetch_all: bool = Field(default=False, description="If true, runs 'git fetch --all --prune' first")
    reset_hard: bool = Field(default=False, description="If true, 'git reset --hard <remote>/<branch>' after fetch")

    @validator("branch")
    def validate_branch(cls, v: Optional[str]) -> Optional[str]:
        import re
        if v is not None and not re.match(SAFE_BRANCH_TAG, v):
            raise ValueError("Invalid branch name")
        return v

class GitPullResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    branch: Optional[str] = None

def git_pull(req: GitPullRequest) -> GitPullResponse:
    with use_client(req.target) as cli:
        out_parts: List[str] = []
        err_parts: List[str] = []
        code = 0

        if req.fetch_all:
            r = cli.exec("git fetch --all --prune", cwd=req.project_dir, timeout=120)
            out_parts.append(r.stdout); err_parts.append(r.stderr)
            code = max(code, r.exit_code)
            if r.exit_code != 0:
                return GitPullResponse(stdout="".join(out_parts), stderr="".join(err_parts), exit_code=code, branch=req.branch)

        if req.reset_hard and req.branch:
            r = cli.exec(f"git reset --hard {req.remote}/{req.branch}", cwd=req.project_dir, timeout=60)
            out_parts.append(r.stdout); err_parts.append(r.stderr)
            code = max(code, r.exit_code)
            if r.exit_code != 0:
                return GitPullResponse(stdout="".join(out_parts), stderr="".join(err_parts), exit_code=code, branch=req.branch)

        if req.branch:
            r = cli.exec(f"git pull {req.remote} {req.branch}", cwd=req.project_dir, timeout=120)
        else:
            r = cli.exec("git pull", cwd=req.project_dir, timeout=120)
        out_parts.append(r.stdout); err_parts.append(r.stderr)
        code = max(code, r.exit_code)
        return GitPullResponse(stdout="".join(out_parts), stderr="".join(err_parts), exit_code=code, branch=req.branch)

TOOL_GIT_PULL = {
    "name": "git_pull",
    "description": "Pull updates from remote; optional fetch --all/prune and reset --hard.",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "project_dir": {"type": "string"},
            "remote": {"type": "string"},
            "branch": {"type": "string"},
            "fetch_all": {"type": "boolean"},
            "reset_hard": {"type": "boolean"}
        },
        "required": ["target", "project_dir"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "stdout": {"type": "string"},
            "stderr": {"type": "string"},
            "exit_code": {"type": "integer"},
            "branch": {"type": "string"},
        },
        "required": ["stdout", "stderr", "exit_code"]
    }
}

# 4) deploy_hook (run a controlled deploy script)
class DeployHookRequest(TargetedRequest):
    project_dir: str = Field(description="Remote project directory containing deploy.sh")
    script: str = Field(default="deploy.sh", description="Hook script filename inside project_dir")
    env: Optional[Dict[str, str]] = Field(default=None, description="Extra environment variables")
    timeout: Optional[int] = Field(default=600, description="Timeout seconds for the full deploy")

class DeployHookResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    script_path: str

def deploy_hook(req: DeployHookRequest) -> DeployHookResponse:
    with use_client(req.target) as cli:
        prefix = _mk_env_prefix(req.env)
        # Run script with bash -e (exit on error); ensure it's executable first
        chmod = cli.exec(f"chmod +x {req.script}", cwd=req.project_dir)
        # We don't fail hard if chmod errors (e.g., FS rules), proceed to execution
        r = cli.exec(f'{prefix}bash -e ./{req.script}', cwd=req.project_dir, timeout=req.timeout)
        return DeployHookResponse(stdout=r.stdout, stderr=r.stderr, exit_code=r.exit_code, script_path=f"{req.project_dir}/{req.script}")

TOOL_DEPLOY_HOOK = {
    "name": "deploy_hook",
    "description": "Run a controlled deploy script in the project directory (e.g., migrations, collectstatic, restart).",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "project_dir": {"type": "string"},
            "script": {"type": "string"},
            "env": {"type": "object", "additionalProperties": {"type": "string"}},
            "timeout": {"type": "integer"}
        },
        "required": ["target", "project_dir"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "stdout": {"type": "string"},
            "stderr": {"type": "string"},
            "exit_code": {"type": "integer"},
            "script_path": {"type": "string"}
        },
        "required": ["stdout", "stderr", "exit_code", "script_path"]
    }
}