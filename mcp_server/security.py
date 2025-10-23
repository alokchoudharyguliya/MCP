from __future__ import annotations
import time
import base64
from typing import Optional, Dict, Tuple
from fastapi import Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import jwt  # PyJWT
from .config import load_policies

log = logging.getLogger("mcp.security")
_policies = load_policies()

# naive in-memory rate limiting (IP+key); replace with Redis for multi-instance
BUCKET: Dict[Tuple[str, str], Tuple[int, float]] = {}  # key: (ip, token), value: (count, window_start)

def build_cors(app):
    origins = _policies.security.cors_allow_origins or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def extract_token(request: Request) -> Optional[str]:
    # Support: Authorization: Bearer <token> (API key or JWT)
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None

def verify_auth(token: Optional[str]) -> Dict:
    sec = _policies.security
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    # Accept either API key or JWT
    if token in (sec.api_keys or []):
        return {"mode": "api_key"}

    if sec.jwt_public_key_pem:
        try:
            claims = jwt.decode(token, sec.jwt_public_key_pem, algorithms=["RS256", "ES256", "EdDSA"])
            return {"mode": "jwt", "claims": claims}
        except Exception as e:
            log.warning("JWT verification failed: %s", e)
            raise HTTPException(status_code=401, detail="Invalid JWT")

    # If no valid match
    raise HTTPException(status_code=401, detail="Unauthorized")

def enforce_rate_limit(ip: str, token: str):
    limit = _policies.security.rate_limit_per_minute or 60
    now = time.time()
    key = (ip, token)
    count, start = BUCKET.get(key, (0, now))
    if now - start >= 60.0:
        BUCKET[key] = (1, now)
        return
    count += 1
    if count > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    BUCKET[key] = (count, start)