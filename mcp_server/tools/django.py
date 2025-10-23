from __future__ import annotations
from typing import Optional, Dict
from pydantic import BaseModel, Field

from .common import TargetedRequest, use_client

class DjangoBase(TargetedRequest):
    project_dir: str = Field(description="Remote project working directory (contains manage.py)")
    venv_path: Optional[str] = Field(default=None, description="Remote virtualenv bin path, e.g., /home/pi/apps/myproj/.venv/bin")
    env: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None

def _mk_prefix(venv_path: Optional[str]) -> str:
    if venv_path:
        return f'export PATH="{venv_path}:$PATH"; '
    return ""

class DjangoManageRequest(DjangoBase):
    manage_args: str = Field(description='Arguments to manage.py, e.g., "migrate" or "collectstatic --noinput"')

class DjangoManageResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int

def django_manage(req: DjangoManageRequest) -> DjangoManageResponse:
    cli = use_client(req.target)
    with cli:
        prefix = _mk_prefix(req.venv_path)
        r = cli.exec(f'{prefix}python manage.py {req.manage_args}', cwd=req.project_dir, env=req.env, timeout=req.timeout)
        return DjangoManageResponse(stdout=r.stdout, stderr=r.stderr, exit_code=r.exit_code)

DJANGO_MANAGE_SCHEMA = {
    "name": "django_manage",
    "description": "Run python manage.py with given args (migrate, collectstatic, etc.)",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "project_dir": {"type": "string"},
            "venv_path": {"type": "string"},
            "env": {"type": "object", "additionalProperties": {"type": "string"}},
            "timeout": {"type": "integer"},
            "manage_args": {"type": "string"},
        },
        "required": ["target", "project_dir", "manage_args"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "stdout": {"type": "string"},
            "stderr": {"type": "string"},
            "exit_code": {"type": "integer"},
        },
        "required": ["stdout", "stderr", "exit_code"]
    }
}

# Dev runserver via tmux
class DjangoRunserverRequest(DjangoBase):
    session: str = Field(description="Tmux session suffix to use (will be prefixed)")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    extra_args: Optional[str] = Field(default=None, description="Extra args, e.g., --settings=...")

class DjangoRunserverResponse(BaseModel):
    ok: bool
    session: str
    detail: str

def django_runserver_tmux(req: DjangoRunserverRequest) -> DjangoRunserverResponse:
    # Use tmux to run a long-lived server
    from .tmux import tmux_ensure, tmux_send_keys, TmuxEnsureRequest, TmuxSendKeysRequest  # local import to avoid cycle
    ensure = tmux_ensure(TmuxEnsureRequest(target=req.target, session=req.session, cwd=req.project_dir))
    if not ensure.ok:
        return DjangoRunserverResponse(ok=False, session=ensure.session, detail=ensure.detail)

    cmd = f'{_mk_prefix(req.venv_path)}python manage.py runserver {req.host}:{req.port}'
    if req.extra_args:
        cmd += f" {req.extra_args}"
    # Clear existing command: send C-c and then run fresh
    tmux_send_keys(TmuxSendKeysRequest(target=req.target, session=req.session, keys="\x03", enter=False))
    run = tmux_send_keys(TmuxSendKeysRequest(target=req.target, session=req.session, keys=cmd, enter=True))
    return DjangoRunserverResponse(ok=run.ok, session=ensure.session, detail=run.detail)

DJANGO_RUNSERVER_SCHEMA = {
    "name": "django_runserver_tmux",
    "description": "Run Django dev server in a tmux session (sends Ctrl-C first, then runserver).",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "project_dir": {"type": "string"},
            "venv_path": {"type": "string"},
            "env": {"type": "object", "additionalProperties": {"type": "string"}},
            "timeout": {"type": "integer"},
            "session": {"type": "string"},
            "host": {"type": "string"},
            "port": {"type": "integer"},
            "extra_args": {"type": "string"},
        },
        "required": ["target", "project_dir", "session"]
    },
    "output_schema": {
        "type": "object",
        "properties": {"ok": {"type": "boolean"}, "session": {"type": "string"}, "detail": {"type": "string"}},
        "required": ["ok", "session"]
    }
}