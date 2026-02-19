# Personal AI Employee

A local-first, autonomous AI agent that manages personal and business affairs using Claude Code, Obsidian, and MCP servers.

## What is a Digital FTE?

A Digital FTE (Full-Time Equivalent) is an AI employee that works 24/7 to manage your life and business. Unlike traditional software, it proactively:

- Monitors email, WhatsApp, and files for important items
- Analyzes and plans responses
- Executes actions through MCP servers
- Asks for approval on sensitive operations
- Generates weekly business briefings

## Quick Start

### Prerequisites

```bash
# Install Python 3.13+
python --version

# Install Claude Code
npm install -g @anthropic/claude-code
```

### Setup

```bash
# Clone and enter project
cd personal-ai-employee

# Copy environment template
cp .env.example .env

# Install dependencies
pip install -e .

# Open vault in Obsidian
obsidian ./vault
```

### Run

```bash
# Start file watcher
python watchers/filesystem_watcher.py --vault ./vault --watch-path ./drop

# Start orchestrator (in another terminal)
python orchestrator.py --vault ./vault --dry-run
```

## Project Structure

```
personal-ai-employee/
├── vault/                    # Obsidian vault (brain)
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── Needs_Action/
│   ├── Plans/
│   ├── Done/
│   ├── Pending_Approval/
│   ├── Approved/
│   └── Logs/
├── watchers/               # Sentinel scripts
│   ├── base_watcher.py
│   ├── gmail_watcher.py
│   ├── filesystem_watcher.py
│   └── whatsapp_watcher.py
├── mcp/                    # MCP servers
│   ├── email/
│   ├── filesystem/
│   ├── odoo/
│   ├── linkedin/
│   ├── twitter/
│   └── social/
├── scripts/                # Utility scripts
│   ├── generate_briefing.py
│   ├── vault_sync.py
│   └── agent_coordinator.py
├── cloud/                  # Cloud deployment
│   ├── cloud_setup.sh
│   ├── health_monitor.sh
│   └── deploy_odoo.sh
└── orchestrator.py         # Main coordinator
```

## How It Works

1. **Watchers** monitor external sources (email, files, WhatsApp)
2. New items create action files in `Needs_Action/`
3. **Orchestrator** triggers Claude Code to process items
4. Claude creates **Plan.md** files with action steps
5. For sensitive actions, Claude creates approval requests
6. User reviews and moves files to `Approved/`
7. **MCP servers** execute the approved actions

## Tiers

| Tier | Features |
|------|----------|
| Bronze | Vault, one watcher, Claude integration |
| Silver | Multiple watchers, MCP servers, approval workflow |
| Gold | Odoo accounting, social media, CEO briefings |
| Platinum | Cloud deployment, 24/7 operation, vault sync |

## Documentation

- [AGENTS.md](AGENTS.md) - Technical specification
- [vault/Company_Handbook.md](vault/Company_Handbook.md) - AI behavior rules
- [vault/Business_Goals.md](vault/Business_Goals.md) - Objectives

## License

MIT
