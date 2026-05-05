#!/bin/sh
set -eu

PORT="${GITHUB_MCP_PORT:-8082}"
LOG_LEVEL="${MCP_LOG_LEVEL:-info}"

exec supergateway \
  --stdio "npx -y @modelcontextprotocol/server-github" \
  --outputTransport streamableHttp \
  --streamableHttpPath /mcp \
  --port "${PORT}" \
  --logLevel "${LOG_LEVEL}"
