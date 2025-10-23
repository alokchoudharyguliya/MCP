from __future__ import annotations

import paramiko
from typing import Optional, Dict
from .config import TargetConfig

class SSHResult:
    def __init__(self, stdout: str, stderr: str, exit_code: int):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code

class SSHClientWrapper:
    def __init__(self, cfg: TargetConfig):
        self.cfg = cfg
        self._client: Optional[paramiko.SSHClient] = None
        self._sftp: Optional[paramiko.SFTPClient] = None

    def __enter__(self):
        self._client = paramiko.SSHClient()
        if self.cfg.known_hosts_path:
            self._client.load_host_keys(self.cfg.known_hosts_path)
            self._client.set_missing_host_key_policy(paramiko.RejectPolicy())
        else:
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        pkey = paramiko.Ed25519Key.from_private_key_file(self.cfg.private_key_path)
        self._client.connect(
            hostname=self.cfg.host,
            port=self.cfg.port,
            username=self.cfg.username,
            pkey=pkey,
            timeout=self.cfg.connect_timeout,
            auth_timeout=self.cfg.connect_timeout,
            banner_timeout=self.cfg.connect_timeout,
        )
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                pass
            self._sftp = None
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

    def exec(self, command: str, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> SSHResult:
        if not self._client:
            raise RuntimeError("SSH client not connected")

        prefix = ""
        if env:
            exports = " ".join([f'{k}="{str(v).replace("\"","\\\"")}"' for k, v in env.items()])
            prefix += f"export {exports}; "
        if cwd:
            prefix += f"cd {cwd} && "

        full_cmd = prefix + command

        stdin, stdout, stderr = self._client.exec_command(full_cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        exit_code = stdout.channel.recv_exit_status()
        return SSHResult(out, err, exit_code)

    def sftp(self) -> paramiko.SFTPClient:
        if not self._client:
            raise RuntimeError("SSH client not connected")
        if not self._sftp:
            self._sftp = self._client.open_sftp()
        return self._sftp

    def put_bytes(self, data: bytes, remote_path: str, mode: Optional[int] = None):
        s = self.sftp()
        with s.file(remote_path, "wb") as f:
            f.write(data)
        if mode is not None:
            s.chmod(remote_path, mode)

    def get_bytes(self, remote_path: str) -> bytes:
        s = self.sftp()
        with s.file(remote_path, "rb") as f:
            return f.read()