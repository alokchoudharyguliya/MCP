from __future__ import annotations

import paramiko
import socket
from typing import Optional, Tuple
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

    def __enter__(self):
        self._client = paramiko.SSHClient()
        # Auto-add policy is convenient for dev; harden in Part 3 using known_hosts
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
        if self._client:
            self._client.close()
        self._client = None

    def exec(self, command: str, cwd: Optional[str] = None, env: Optional[dict] = None, timeout: Optional[int] = None) -> SSHResult:
        if not self._client:
            raise RuntimeError("SSH client not connected")

        prefix = ""
        if env:
            exports = " ".join([f'{k}="{str(v).replace(chr(34), chr(92)+chr(34))}"' for k, v in env.items()])
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
        return self._client.open_sftp()

    def put_bytes(self, data: bytes, remote_path: str, mode: Optional[int] = None):
        s = self.sftp()
        
        # Ensure parent directory exists
        import os
        parent_dir = os.path.dirname(remote_path)
        if parent_dir and parent_dir != '/':
            try:
                s.stat(parent_dir)
            except FileNotFoundError:
                # Create parent directories recursively
                self._mkdir_p(s, parent_dir)
        
        with s.file(remote_path, "wb") as f:
            f.write(data)
        if mode is not None:
            s.chmod(remote_path, mode)
    
    def _mkdir_p(self, sftp, remote_path):
        """Create remote directory recursively"""
        import os
        if remote_path == '/' or remote_path == '':
            return
        try:
            sftp.stat(remote_path)
        except FileNotFoundError:
            parent = os.path.dirname(remote_path)
            if parent and parent != '/':
                self._mkdir_p(sftp, parent)
            try:
                sftp.mkdir(remote_path)
            except OSError:
                pass  # Directory might already exist

    def get_bytes(self, remote_path: str) -> bytes:
        s = self.sftp()
        with s.file(remote_path, "rb") as f:
            return f.read()