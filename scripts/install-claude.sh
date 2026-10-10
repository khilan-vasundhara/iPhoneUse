#!/bin/sh
# One-step Claude Code setup: registers the iPhone Use MCP server for this user.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
command -v claude >/dev/null || { echo "Install Claude Code first"; exit 1; }
claude mcp remove iphone_use -s user >/dev/null 2>&1 || true
claude mcp add -s user iphone_use -- python3 "$root/server/iphone_use.py"

mkdir -p "$HOME/.claude/skills"
for s in iphone-use iphone-use-setup; do ln -sfn "$root/skills/$s" "$HOME/.claude/skills/$s"; done
echo "Done. Restart Claude Code, then ask: use iphone-use-setup to configure my iPhone."
