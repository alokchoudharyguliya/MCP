FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
COPY mcp_server /app/mcp_server
COPY config /app/config

RUN pip install --upgrade pip && pip install -e .

ENV MCP_PI_CONFIG=/app/config/hosts.yaml
ENV MCP_PI_POLICY=/app/config/policies.yaml

EXPOSE 7800
CMD ["uvicorn", "mcp_server.main:app", "--host", "0.0.0.0", "--port", "7800"]