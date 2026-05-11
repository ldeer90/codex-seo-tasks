#!/bin/bash
# Runs the Monday API MCP server from a local install (avoids npx peer-dep issues).
# Sources .env to get MONDAY_API_KEY and remaps it to MONDAY_TOKEN.
set -a
source "/Users/laurencedeer/Desktop/SEO Automation/.env"
set +a
export MONDAY_TOKEN="$MONDAY_API_KEY"
exec /Users/laurencedeer/.nvm/versions/node/v22.14.0/bin/node \
  "/Users/laurencedeer/Desktop/SEO Automation/.claude/monday-mcp-server/node_modules/@mondaydotcomorg/monday-api-mcp/dist/index.js"
