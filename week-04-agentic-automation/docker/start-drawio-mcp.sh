#!/bin/sh
set -eu

PORT="${DRAWIO_MCP_PORT:-8083}"
LOG_LEVEL="${MCP_LOG_LEVEL:-info}"

exec supergateway \
  --stdio "npx -y @drawio/mcp" \
  --outputTransport streamableHttp \
  --streamableHttpPath /mcp \
  --port "${PORT}" \
  --logLevel "${LOG_LEVEL}"
