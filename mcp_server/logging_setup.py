from __future__ import annotations
import logging
import json
import re
from typing import Any, Dict, Optional

REDACT_KEYS = {"private_key_path", "api_key", "authorization", "jwt", "password", "secret"}

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            data.update({"extra": redact(record.extra)})
        return json.dumps(data, ensure_ascii=False)

def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: ("[REDACTED]" if k.lower() in REDACT_KEYS else redact(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    if isinstance(obj, str):
        # best-effort redact obvious secrets in strings
        if "-----BEGIN OPENSSH PRIVATE KEY-----" in obj or len(obj) > 2000:
            return "[REDACTED_STRING]"
    return obj

def setup_logging(level: str = "INFO"):
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(level)