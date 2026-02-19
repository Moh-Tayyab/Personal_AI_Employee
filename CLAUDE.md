# Personal AI Employee - Project Context

This is a Personal AI Employee project - a Digital FTE (Full-Time Equivalent) that autonomously manages personal and business affairs using Claude Code, Obsidian, and MCP servers.

## Project Summary

A local-first, autonomous AI agent that:
- Monitors email, WhatsApp, and files via Python watchers
- Uses Claude Code as the reasoning engine
- Stores everything in an Obsidian Markdown vault
- Executes actions through MCP (Model Context Protocol) servers
- Requires human approval for sensitive operations

## Architecture

```
External Sources → Watchers → Obsidian Vault → Claude Code → MCP → Actions
```

## Key Files

- `orchestrator.py` - Main coordinator that triggers Claude and processes items
- `watchers/` - Python scripts that monitor Gmail, files, WhatsApp
- `mcp/` - MCP servers for email, social media, Odoo accounting
- `vault/` - Obsidian vault with all data and rules

## Vault Structure

```
vault/
├── Dashboard.md           # System status
├── Company_Handbook.md  # AI rules and autonomy levels
├── Business_Goals.md    # Revenue targets, KPIs
├── Needs_Action/        # Items requiring processing
├── Plans/               # Generated plan files
├── Done/                # Completed tasks
├── Pending_Approval/    # Items needing human approval
├── Approved/            # Approved items ready for execution
├── Logs/                # Daily activity logs
└── Briefings/           # CEO briefing reports
```

## Commands

```bash
# File watcher
python watchers/filesystem_watcher.py --vault ./vault --watch-path ./drop

# Orchestrator
python orchestrator.py --vault ./vault --dry-run

# Generate CEO Briefing
python scripts/generate_briefing.py --vault ./vault

# Vault sync (Platinum)
python scripts/vault_sync.py --vault ./vault --mode pull
```

## Tiers Implemented

1. **Bronze** - Foundation (watchers, vault, Claude integration)
2. **Silver** - Functional (MCP servers, approval workflow)
3. **Gold** - Autonomous (Odoo, social media, CEO briefings)
4. **Platinum** - Cloud + Local (24/7, vault sync)

## Key Patterns

- **Human-in-the-Loop**: Sensitive actions require moving files to Approved/
- **Claim-by-Move**: First agent to claim an item owns it
- **Ralph Wiggum Loop**: Claude keeps working until task is complete
