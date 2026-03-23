# MCP Configuration

## Source of Truth

Use `.mcp.json` as the primary MCP configuration for this repository.

Other MCP config files are legacy examples and may be stale:

- `mcp_config.json`
- `claude_mcp_config.json`

## Validation

Run:

```bash
scripts/validate_mcp.sh
```

This checks for required commands (`uvx`, `npx`, `codex`) and confirms the config file exists.
