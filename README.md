# Personal AI Employee 🤖

> **A Digital FTE (Full-Time Equivalent)** - An autonomous AI agent that manages personal and business affairs using Claude Code, Obsidian, and MCP servers.

[![Tier: Platinum](https://img.shields.io/badge/Tier-Platinum-blueviolet)]()
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

## 🎯 What is a Digital FTE?

A Digital FTE is an AI employee that works 24/7 to manage your life and business. Unlike traditional software, it proactively:

- 📧 **Monitors** email, WhatsApp, and files for important items
- 🧠 **Analyzes** and plans responses using Claude Code
- ⚡ **Executes** actions through MCP servers
- ✅ **Asks for approval** on sensitive operations
- 📊 **Generates** weekly CEO briefings

## ✨ Implementation Status

| Tier | Status | Features |
|------|--------|----------|
| **Bronze** | ✅ Complete | Vault, watchers, Claude integration |
| **Silver** | ✅ Complete | MCP servers, approval workflow |
| **Gold** | ✅ Complete | Odoo, social media APIs, briefings |
| **Platinum** | ✅ Complete | Cloud deployment, PM2, health monitoring |
| **Latest** | ✅ New | HTTP hooks, parallel processing, interactive approvals |

### Features by Tier

**Bronze Tier (8-12 hours)**
- ✅ Obsidian vault with Dashboard, Company Handbook, Business Goals
- ✅ Gmail watcher with OAuth2 authentication
- ✅ WhatsApp watcher with Playwright automation
- ✅ Filesystem watcher with file categorization
- ✅ Orchestrator coordinating Claude Code

**Silver Tier (20-30 hours)**
- ✅ Email MCP server (send, reply, search, draft)
- ✅ Filesystem MCP server
- ✅ LinkedIn MCP server with session management
- ✅ Human-in-the-loop approval workflow
- ✅ Dry-run safety mode

**Gold Tier (40+ hours)**
- ✅ Odoo MCP server (invoices, contacts, accounting)
- ✅ Twitter MCP server with OAuth 1.0a API
- ✅ Facebook/Instagram Graph API integration
- ✅ CEO Briefing generator
- ✅ Ralph Wiggum loop (persistent execution)

**Platinum Tier (60+ hours)**
- ✅ PM2 ecosystem configuration
- ✅ Cloud deployment scripts (Oracle/AWS)
- ✅ Health monitoring
- ✅ Vault sync with Git
- ✅ Claim-by-move agent coordination

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.11+
python --version

# Node.js 20+ (for PM2)
node --version

# Claude Code CLI
npm install -g @anthropic/claude-code

# Obsidian (optional, for vault viewing)
# Download from https://obsidian.md
```

### One-Command Start

```bash
# Start all services (orchestrator + hooks + watchers)
./scripts/start_all.sh

# Or start individual services:
./scripts/start_hooks.sh    # HTTP endpoints only
python orchestrator.py --vault ./vault  # Orchestrator only
```

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/personal-ai-employee.git
cd personal-ai-employee

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for WhatsApp/LinkedIn)
playwright install chromium

# Copy environment template
cp .env.example .env
# Edit .env with your credentials
```

### Gmail Setup

```bash
# Run Gmail OAuth setup
python scripts/quick_setup_gmail.py

# Or manually:
# 1. Go to Google Cloud Console
# 2. Create OAuth 2.0 credentials
# 3. Download credentials to vault/secrets/gmail_credentials.json
# 4. Run a watcher to generate token
```

### Running the System

```bash
# Option 1: Run with PM2 (recommended for production)
pm2 start ecosystem.config.js

# Option 2: Run individually
python orchestrator.py --vault ./vault
python watchers/gmail_watcher.py --vault ./vault

# Option 3: Dry-run mode (safe testing)
python orchestrator.py --vault ./vault --dry-run
```

### Demo

```bash
# Run the demo script to see all capabilities
chmod +x scripts/demo.sh
./scripts/demo.sh platinum
```

## 📁 Project Structure

```
personal-ai-employee/
├── vault/                    # Obsidian vault (AI brain)
│   ├── Dashboard.md          # System status
│   ├── Company_Handbook.md   # AI rules and autonomy levels
│   ├── Business_Goals.md     # Revenue targets, KPIs
│   ├── Needs_Action/         # Items awaiting processing
│   ├── Plans/                # Generated action plans
│   ├── Done/                 # Completed items
│   ├── Pending_Approval/     # Items needing human approval
│   ├── Approved/             # Approved items ready for execution
│   ├── Drafts/               # Draft communications
│   ├── Logs/                 # Daily activity logs
│   └── secrets/              # API credentials (not synced)
├── watchers/                 # Sentinel scripts
│   ├── base_watcher.py       # Abstract base class
│   ├── gmail_watcher.py      # Gmail API integration
│   ├── filesystem_watcher.py # File drop monitoring
│   └── whatsapp_watcher.py   # WhatsApp Web automation
├── mcp/                      # MCP servers for actions
│   ├── base.py               # MCP protocol base
│   ├── email/                # Gmail actions
│   ├── filesystem/           # File operations
│   ├── odoo/                 # Accounting integration
│   ├── linkedin/             # LinkedIn posting
│   ├── twitter/              # Twitter/X API
│   └── social/               # Facebook/Instagram
├── scripts/                  # Utility scripts
│   ├── generate_briefing.py  # CEO briefing generator
│   ├── vault_sync.py         # Git-based sync
│   ├── process_scheduled.py  # Scheduled posts
│   └── demo.sh               # Hackathon demo
├── cloud/                    # Cloud deployment
│   ├── cloud_setup.sh        # Full cloud setup
│   ├── deploy.sh             # Quick deploy
│   └── health_check.sh       # Health monitoring
├── .agents/                  # Claude Code skills
├── ecosystem.config.js       # PM2 configuration
├── orchestrator.py           # Main coordinator
├── mcp_client.py             # Unified MCP client
└── requirements.txt          # Python dependencies
```

## 🔄 How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Gmail     │     │  WhatsApp   │     │   Files     │
│  Watcher    │     │  Watcher    │     │  Watcher    │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Needs_Action/  │
                  │   (New Items)   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Orchestrator  │
                  │  (Triggers AI)  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Claude Code   │
                  │   (Reasoning)   │
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Plans/  │ │Approved/ │ │ Pending/ │
        └────┬─────┘ └────┬─────┘ └──────────┘
             │            │
             ▼            ▼
        ┌─────────────────────┐
        │    MCP Servers      │
        │ (Execute Actions)   │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │      Done/          │
        │  (Completed Items)  │
        └─────────────────────┘
```

### Workflow

1. **Watchers** monitor external sources (email, WhatsApp, files)
2. New items create action files in `Needs_Action/`
3. **Orchestrator** triggers Claude Code to process items
4. Claude creates **Plan.md** files with action steps
5. For sensitive actions, Claude creates approval requests
6. User reviews and moves files to `Approved/`
7. **MCP servers** execute the approved actions
8. Completed items move to `Done/`

## 🌐 Cloud Deployment

### HTTP Endpoints (NEW)

The Personal AI Employee now exposes HTTP endpoints for external integrations:

```bash
# Start hook server
./scripts/start_hooks.sh --port 8080 --vault ./vault

# Check health
curl http://localhost:8080/health

# Get pending approvals
curl http://localhost:8080/pending

# Trigger processing
curl -X POST http://localhost:8080/trigger/process
```

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/status` | GET | System status |
| `/pending` | GET | Pending approvals |
| `/dashboard` | GET | Dashboard data |
| `/webhook/email` | POST | Email webhooks |
| `/webhook/approval` | POST | Approval callbacks |
| `/webhook/github` | POST | GitHub integration |

### Webhook Notifications

Configure Slack/Discord notifications in `vault/secrets/webhooks.json`:

```json
{
  "webhooks": {
    "slack": "https://hooks.slack.com/services/YOUR/WEBHOOK",
    "discord": "https://discord.com/api/webhooks/YOUR/WEBHOOK"
  }
}
```

### Quick Deploy

```bash
# Set target server
export CLOUD_USER=ubuntu
export CLOUD_HOST=your-vm.example.com

# Deploy
./cloud/deploy.sh $CLOUD_USER@$CLOUD_HOST
```

### Full Setup

```bash
# On a fresh Ubuntu VM
./cloud/cloud_setup.sh --provider oracle

# Or for AWS
./cloud/cloud_setup.sh --provider aws
```

### Health Monitoring

```bash
# Run health check
./cloud/health_check.sh --alert-email you@example.com

# Add to cron for automated monitoring
*/5 * * * * /opt/ai-employee/cloud/health_check.sh
```

## 📚 Documentation

- [CLAUDE.md](CLAUDE.md) - Project context for Claude Code
- [vault/Company_Handbook.md](vault/Company_Handbook.md) - AI behavior rules
- [vault/Business_Goals.md](vault/Business_Goals.md) - Objectives and KPIs

## 🛡️ Security

- **Secrets never synced** - `vault/secrets/` is in `.gitignore`
- **Human-in-the-loop** - Sensitive actions require approval
- **Dry-run mode** - Test without executing actions
- **Payment protection** - No auto-approval for financial operations

## 📄 License

MIT
