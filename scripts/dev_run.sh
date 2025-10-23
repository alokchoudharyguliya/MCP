#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
uvicorn mcp_server.main:app --host 0.0.0.0 --port 7800