#!/usr/bin/env bash
set -euo pipefail

config_path="${1:-.mcp.json}"

if [[ ! -f "$config_path" ]]; then
  echo "Missing MCP config: $config_path"
  exit 1
fi

missing=()
for cmd in uvx npx codex; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    missing+=("$cmd")
  fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "Missing required commands: ${missing[*]}"
  exit 1
fi

echo "MCP config present and required commands available."
