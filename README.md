# 🤖 Personal AI Employee (Digital FTE)

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A comprehensive autonomous AI agent system built with Qwen Code and Obsidian that proactively manages personal and business affairs 24/7.

## 🎯 What This Does

This is a **Digital Full-Time Equivalent (FTE)** - an AI employee that:

- **Monitors** Gmail, WhatsApp, files, and bug reports 24/7
- **Processes** incoming tasks autonomously
- **Fixes bugs** end-to-end (reproduce → plan → fix → verify → deploy)
- **Generates CEO Briefings** with revenue, bottlenecks, and suggestions
- **Requires approval** for sensitive actions (payments, client comms)
- **Logs everything** for audit and review

## 📊 Human vs Digital FTE Comparison

| Feature | Human FTE | Digital FTE |
|---------|-----------|-------------|
| Availability | 40 hours/week | 168 hours/week (24/7) |
| Monthly Cost | $4,000-$8,000+ | $50-$200 (API costs) |
| Ramp-up Time | 3-6 months | Instant (via SKILL.md) |
| Consistency | 85-95% | 99%+ |
| Scaling | Hire 10 for 10x work | Instant duplication |
| Cost per Task | ~$5.00 | ~$0.50 |
| Annual Hours | ~2,000 | ~8,760 |

**💡 The 'Aha!' Moment**: A Digital FTE works nearly 9,000 hours/year vs a human's 2,000. That's **85-90% cost savings**.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                         │
│     Gmail    WhatsApp    Bug Reports    Files    Bank APIs  │
└────────┬─────────┬───────────┬───────────┬─────────┬────────┘
         │         │           │           │         │
         ▼         ▼           ▼           ▼         ▼
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER (Watchers)              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ │
│  │Gmail Watcher│ │WhatsApp W.│ │Bug Watcher │ │File Watch│ │
│  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └────┬─────┘ │
└─────────┼──────────────┼──────────────┼─────────────┼───────┘
          │              │              │             │
          ▼              ▼              ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (Memory/GUI)              │
│  /Needs_Action/  /Plans/  /Done/  /Pending_Approval/        │
│  Dashboard.md  Company_Handbook.md  Business_Goals.md       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    REASONING LAYER (Qwen Code)              │
│         Read → Think → Plan → Write → Request Approval      │
│         + Ralph Wiggum Loop (persistence until done)        │
└────────────────────────┬────────────────────────────────────┘
                         │
              ┌──────────┴───────────┐
              ▼                      ▼
┌─────────────────────┐  ┌──────────────────────────────────┐
│  HUMAN-IN-THE-LOOP  │  │       ACTION LAYER (MCP)         │
│  Review & Approve   │  │  Email  Browser  Vercel  Odoo   │
└─────────────────────┘  └──────────────────────────────────┘
```

## 📁 Project Structure

```
Personal_AI_Employee/
├── vault/                          # Obsidian vault (Memory/GUI)
│   ├── Dashboard.md               # Real-time status (auto-updated)
│   ├── Company_Handbook.md        # AI behavior rules
│   ├── Business_Goals.md          # Objectives and KPIs
│   ├── Needs_Action/              # Items requiring attention
│   ├── In_Progress/               # Active tasks (claim-by-move)
│   ├── Pending_Approval/          # Awaiting human approval
│   ├── Approved/                  # Ready for execution
│   ├── Done/                      # Completed tasks
│   ├── Rejected/                  # Rejected items
│   ├── Plans/                     # AI-generated action plans
│   ├── Logs/                      # Activity audit logs (JSON)
│   └── Briefings/                 # CEO weekly reports
│
├── mcp/                           # MCP servers (7 servers, 49 tools)
│   ├── email/server.py            # Gmail send/search/mark_read (5 tools)
│   ├── filesystem/server.py       # File operations (8 tools)
│   ├── approval/server.py         # Approval workflow (7 tools)
│   ├── linkedin/server.py         # LinkedIn posting (5 tools)
│   ├── twitter/server.py          # Twitter/X posting (6 tools)
│   ├── social/server.py           # Facebook/Instagram (8 tools)
│   └── odoo/server.py             # Accounting integration (10 tools)
│
├── watchers/                      # Perception layer
│   ├── base_watcher.py            # Abstract base class
│   ├── gmail_watcher.py           # Gmail API polling
│   ├── whatsapp_watcher.py        # WhatsApp Web monitoring
│   └── filesystem_watcher.py      # Drop directory monitoring
│
├── scripts/                       # Operations
│   ├── start_all.sh               # Start services (PM2 or direct)
│   ├── stop_all.sh                # Stop services (--force)
│   ├── status_all.sh              # System status
│   ├── reset_all.sh               # Clean state management
│   ├── logs_all.sh                # Unified log viewing
│   ├── health_check.sh            # Health validation
│   ├── setup_cron.sh              # Install cron jobs
│   ├── silver_tier_demo.sh        # Email flow demo
│   ├── gold_tier_demo.sh          # Full integration demo
│   ├── cron/                      # Scheduled tasks
│   │   ├── process_needs_action.sh   # Every 5 minutes
│   │   ├── daily_briefing.sh         # 8:00 AM daily
│   │   ├── weekly_ceo_briefing.sh    # Monday 7:00 AM
│   │   └── health_check.sh           # Every hour
│   ├── orchestrator.py            # Master coordinator
│   ├── generate_ceo_briefing.py   # CEO briefing generator
│   ├── ralph_loop.py              # Persistence pattern
│   ├── health_server.py           # HTTP health server
│   ├── error_recovery.py          # Base error recovery
│   └── error_recovery_integration.py  # Orchestrator wiring
│
├── tests/                         # Integration tests (272 tests)
│   ├── test_integration.py        # Watcher + MCP + E2E tests
│   ├── test_orchestrator_flow.py  # Orchestrator lifecycle tests
│   ├── test_error_recovery_integration.py  # Circuit breaker tests
│   ├── test_health_server.py      # Health server tests
│   ├── test_error_recovery_resilience.py   # Recovery chain tests
│   └── ...                        # (14 test files total)
│
├── ecosystem.config.js            # PM2 process manager
├── orchestrator.py                # Main entry point
├── .env.example                   # Environment template
├── pyproject.toml                 # Python dependencies
│
├── ARCHITECTURE.md                # System architecture documentation
├── CHANGELOG.md                   # Implementation history
├── OPERATIONS_RUNBOOK.md          # Daily operations guide
├── AGENTS.md                      # Technical specification
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Check Node.js (need 18+)
node -v  # Should be v18+

# Check Python (need 3.13+)
python3 --version
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install PM2 for 24/7 operation (Silver Tier)
npm install -g pm2
```

### 3. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required for Silver Tier:
# - GMAIL_CREDENTIALS_PATH (for Gmail watcher)
# - LINKEDIN_ACCESS_TOKEN (for LinkedIn posting)
```

### 4. Configure LinkedIn (Silver Tier - Optional)

```bash
# Get LinkedIn token from:
# https://www.linkedin.com/developers/apps

# Set environment variable
export LINKEDIN_ACCESS_TOKEN=your_token_here

# OR create vault secrets file
mkdir -p vault/secrets
echo "your_token_here" > vault/secrets/linkedin_token.txt
```

### 5. Start 24/7 Operation (Silver Tier)

```bash
# Preview what would start (no services actually started)
./scripts/start_all.sh --dry-run

# Start all watchers and orchestrator with PM2
./scripts/start_all.sh

# Save for auto-restart on boot
pm2 save
pm2 startup

# Check status
./scripts/status_all.sh
```

### 6. Setup Scheduled Tasks (Silver Tier)

```bash
# Preview cron entries
./scripts/setup_cron.sh --dry-run

# Install cron jobs for:
# - Process Needs_Action (every 5 minutes)
# - Daily briefing (8:00 AM)
# - Weekly CEO briefing (Monday 7:00 AM)
# - Hourly health check
./scripts/setup_cron.sh
```

### 7. Validate System Health

```bash
# Run comprehensive health check
./scripts/health_check.sh

# View all logs
./scripts/logs_all.sh
```

### 8. Run Demos

```bash
# Silver Tier demo (email flow)
./scripts/silver_tier_demo.sh

# Gold Tier demo (social + odoo + briefing)
./scripts/gold_tier_demo.sh
```

## 🎫 Fix Ticket Skill (Autonomous Bug Fixer)

The **fix-ticket** skill transforms Qwen into an autonomous software engineer:

### Workflow

1. **Read** bug report from `/vault/Needs_Action/bugs/`
2. **Reproduce** bug using Playwright CLI
3. **Research** root cause in codebase
4. **Plan** fix with detailed steps
5. **Implement** fix with code review
6. **Verify** fix in browser
7. **Commit** and **Deploy** to Vercel
8. **Log** and move to `/vault/Done/`

### Example Bug Report

Create a file in `/vault/Needs_Action/bugs/BUG-2026-03-12.md`:

```markdown
---
type: bug_report
priority: P1
url: https://your-app.com
created: 2026-03-12T10:00:00Z
---

## Bug Description
"Get Started" button doesn't work on homepage

## Steps to Reproduce
1. Go to https://your-app.com
2. Click "Get Started" button
3. Nothing happens

## Expected Behavior
Should navigate to /get-started page

## Actual Behavior
Console shows: "Uncaught TypeError: Cannot read property..."
```

### Run Fix Ticket

```bash
qwen --prompt "/fix-ticket process-all" --cwd vault
```

## 📊 CEO Briefing

Generates weekly business audit every Monday:

```bash
qwen --prompt "Generate weekly CEO briefing" --cwd vault
```

### Includes:
- Revenue this week and MTD
- Completed tasks
- Bottlenecks with delay analysis
- Cost optimization suggestions
- Upcoming deadlines
- Key metrics vs targets

## 📜 Tiers (Hackathon Scope)

### 🥉 Bronze Tier (8-12 hours) - 100% COMPLETE ✅
- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher (Filesystem)
- [x] Qwen Code reading/writing to vault
- [x] Basic folder structure
- [x] Agent Skills implemented

### 🥈 Silver Tier (20-30 hours) - 100% COMPLETE ✅
- [x] Multiple watchers (Gmail + WhatsApp + Files)
- [x] Plan.md generation for each task
- [x] Email MCP server — 5 tools, fully functional
- [x] HITL approval workflow — 7 tools
- [x] Basic scheduling (PM2 + cron)
- [x] LinkedIn MCP server — 5 tools, with image posting
- [x] Twitter/X MCP server — 6 tools, with thread support
- [x] Operations scripts (start/stop/status/reset/logs/health)
- [x] Demo scripts (silver_tier_demo.sh)

### 🥇 Gold Tier (40+ hours) - 100% COMPLETE ✅
- [x] Full cross-domain integration (Personal + Business)
- [x] Odoo accounting integration — 10 tools, session-based auth
- [x] Facebook/Instagram integration — 8 tools, cross-platform posting
- [x] 7 MCP servers, 49 tools total
- [x] Weekly CEO Briefing with revenue tracking
- [x] Error recovery & graceful degradation — 5 error categories, circuit breakers
- [x] Comprehensive audit logging
- [x] Ralph Wiggum loop for multi-step tasks — 3 completion strategies
- [x] Health server with 6 HTTP endpoints
- [x] 272 integration tests, 100% pass rate
- [x] Demo scripts (gold_tier_demo.sh)

### 📚 Documentation
- [x] [ARCHITECTURE.md](./ARCHITECTURE.md) — System architecture and design
- [x] [CHANGELOG.md](./CHANGELOG.md) — Implementation history
- [x] [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md) — Daily operations guide
- [x] [AGENTS.md](./AGENTS.md) — Technical specification
- [x] [requirements.md](./requirements.md) — Hackathon requirements

### 💎 Platinum Tier (60+ hours) - 0% NOT STARTED
- [ ] Cloud VM deployment (24/7)
- [ ] Work-zone specialization (Cloud vs Local)
- [ ] Git-based vault sync
- [ ] Multi-agent coordination

## 🔧 Configuration

### Company Handbook

Edit `/vault/Company_Handbook.md` to set rules:

```markdown
## Payment Rules
- Flag any payment >$500 for review
- Never auto-approve new recipients
- Always log transactions

## Communication Rules
- Response time target: <24 hours
- Be professional and courteous
- No messages after 9 PM
```

### Business Goals

Edit `/vault/Business_Goals.md`:

```yaml
Revenue Target:
  Monthly: $10,000
  Current MTD: $4,500

Metrics:
  Client response time: <24 hours
  Invoice payment rate: >90%
  Software costs: <$500/month
```

## 🔐 Security

### Credential Management

```bash
# NEVER commit .env files
# Use environment variables:
export GMAIL_API_KEY="your-key"
export VERCEL_TOKEN="your-token"

# For banking, use system keychain:
# macOS: security add-generic-password
# Windows: credman module
```

### Human-in-the-Loop

Sensitive actions require approval:

1. Qwen creates file in `/vault/Pending_Approval/`
2. Human reviews and moves to:
   - `/Approved/` → Execute action
   - `/Rejected/` → Log and skip

### Audit Logging

All actions logged to `/vault/Logs/`:

```json
{
  "timestamp": "2026-03-12T10:30:00Z",
  "action": "bug_fix",
  "bug_id": "BUG-001",
  "status": "success",
  "details": {...}
}
```

## 📝 Example Flows

### Email Processing Flow

```
1. Gmail Watcher detects new email
2. Creates /vault/Needs_Action/EMAIL_001.md
3. Orchestrator triggers Qwen
4. Qwen reads email, categorizes, drafts response
5. If sensitive → creates approval request
6. Human approves (moves to /Approved/)
7. Email MCP sends response
8. Move to /Done/, log action
```

### Bug Fix Flow

```
1. Bug report placed in /vault/Needs_Action/bugs/
2. Bug Watcher detects new report
3. Qwen triggers /fix-ticket skill
4. Playwright reproduces bug
5. Qwen researches and plans fix
6. Implements fix, runs tests
7. Verifies in browser
8. Commits and deploys to Vercel
9. Moves to /Done/, updates Dashboard
```

### CEO Briefing Flow

```
1. Cron triggers every Monday 7 AM
2. Qwen reads Business_Goals.md
3. Analyzes /vault/Done/ for completed tasks
4. Analyzes /vault/Accounting/ for revenue
5. Detects bottlenecks from task durations
6. Audits subscriptions for cost optimization
7. Generates briefing in /vault/Briefings/
8. Creates action items in /vault/Needs_Action/
```

## 🛠️ Troubleshooting

### Quick Health Check

```bash
# Run comprehensive health check
./scripts/health_check.sh

# View system status
./scripts/status_all.sh

# View all logs
./scripts/logs_all.sh
```

### Service Not Starting

```bash
# Check what would start (dry run)
./scripts/start_all.sh --dry-run

# Check Python environment
.venv/bin/python --version

# Install dependencies
.venv/bin/pip install -e .

# Check PM2 status
pm2 list
```

### Stuck Items in In_Progress

```bash
# View stuck items
ls vault/In_Progress/

# Move back to Needs_Action
mv vault/In_Progress/*.md vault/Needs_Action/

# Or use reset script
./scripts/reset_all.sh --dry-run  # Preview
./scripts/reset_all.sh             # Execute
```

### Reset to Clean State

```bash
# Soft reset (keeps Done, Plans, Approved)
./scripts/reset_all.sh

# Full reset (also clears Done, Plans, Briefings)
./scripts/reset_all.sh --all
```

### MCP Server Errors

```bash
# Validate all MCP servers
./scripts/health_check.sh

# Test individual server in dry_run mode
DRY_RUN=true .venv/bin/python -c "
from orchestrator import Orchestrator
orch = Orchestrator(vault_path='./vault', dry_run=True)
print(orch._call_mcp_server('email', 'send_email', {
    'to': 'test@test.com', 'subject': 'T', 'body': 'B', 'cc': '', 'bcc': ''
}))
"
```

### Cron Issues

```bash
# View current cron jobs
crontab -l

# Preview cron entries
./scripts/setup_cron.sh --dry-run

# Remove and re-install
./scripts/setup_cron.sh --remove
./scripts/setup_cron.sh

# View cron logs
tail -f logs/cron.log
```

## 📚 Learning Resources

- [Qwen Code Docs](https://qwen.ai/)
- [Obsidian](https://obsidian.md)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Playwright](https://playwright.dev)
- [Panaversity Hackathon](https://agentfactory.panaversity.org)

## 🤝 Contributing

This is a hackathon project. Contributions welcome:

1. Fork the repository
2. Create feature branch
3. Implement enhancement
4. Add documentation
5. Submit PR

## 📄 License

MIT License - Build your own AI Employee!

## 📞 Support

- Wednesday Research Meetings: 10 PM PKT on Zoom
- YouTube: [@panaversity](https://www.youtube.com/@panaversity)
- Hackathon Form: [Submit Here](https://forms.gle/JR9T1SJq5rmQyGkGA)

---

**Built with ❤️ for the Personal AI Employee Hackathon 2026**

*Your Digital FTE awaits!*
