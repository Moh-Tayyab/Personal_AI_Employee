# 🤖 Personal AI Employee (Digital FTE)

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A comprehensive autonomous AI agent system built with Claude Code and Obsidian that proactively manages personal and business affairs 24/7.

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
│                    REASONING LAYER (Claude Code)            │
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
│   ├── Dashboard.md               # Real-time status
│   ├── Company_Handbook.md        # AI behavior rules
│   ├── Business_Goals.md          # Objectives and KPIs
│   ├── Needs_Action/              # Items requiring attention
│   │   ├── bugs/                  # Bug reports
│   │   ├── emails/                # Email action files
│   │   └── files/                 # Dropped files
│   ├── Plans/                     # Generated plans
│   ├── In_Progress/               # Active tasks (claim-by-move)
│   ├── Pending_Approval/          # Awaiting human approval
│   ├── Approved/                  # Ready for execution
│   ├── Done/                      # Completed tasks
│   ├── Logs/                      # Activity audit logs
│   └── Briefings/                 # CEO reports
│
├── .claude/skills/                # Agent Skills
│   ├── fix-ticket/                # Bug fixing automation
│   ├── briefing/                  # CEO briefing generator
│   ├── watchers/                  # Watcher utilities
│   └── playwright-cli/            # Browser automation
│
├── scripts/
│   ├── watchers/
│   │   ├── base_watcher.py        # Abstract base class
│   │   ├── filesystem_watcher.py  # File monitoring
│   │   └── bug_watcher.py         # Bug report monitoring
│   ├── orchestrator/
│   │   └── orchestrator.py        # Master process
│   └── requirements.txt           # Python dependencies
│
├── mcp/                           # MCP servers (optional)
│   ├── jira/
│   ├── vercel/
│   ├── odoo/
│   └── social/
│
└── .env.example                   # Environment template
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
cd scripts
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 3. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# (Gmail, Vercel, etc. - optional for Bronze tier)
```

### 4. Start the System

```bash
# Option A: Start orchestrator (manages all watchers)
cd scripts/orchestrator
python orchestrator.py ../../vault

# Option B: Start individual watchers
cd scripts/watchers
python filesystem_watcher.py ../../vault
python bug_watcher.py ../../vault
```

### 5. Process Tasks

```bash
# Claude will automatically process items in Needs_Action
# Or trigger manually:
claude --prompt "Process all files in /vault/Needs_Action" --cwd vault
```

## 🎫 Fix Ticket Skill (Autonomous Bug Fixer)

The **fix-ticket** skill transforms Claude into an autonomous software engineer:

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
claude --prompt "/fix-ticket process-all" --cwd vault
```

## 📊 CEO Briefing

Generates weekly business audit every Monday:

```bash
claude --prompt "Generate weekly CEO briefing" --cwd vault
```

### Includes:
- Revenue this week and MTD
- Completed tasks
- Bottlenecks with delay analysis
- Cost optimization suggestions
- Upcoming deadlines
- Key metrics vs targets

## 📜 Tiers (Hackathon Scope)

### Bronze Tier (8-12 hours)
- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher (Filesystem)
- [x] Claude Code reading/writing to vault
- [x] Basic folder structure
- [x] Agent Skills implemented

### Silver Tier (20-30 hours)
- [ ] Multiple watchers (Gmail + WhatsApp + Bug)
- [ ] Plan.md generation
- [ ] One MCP server (Email)
- [ ] HITL approval workflow
- [ ] Basic scheduling

### Gold Tier (40+ hours)
- [ ] Full cross-domain integration
- [ ] Odoo accounting integration
- [ ] Social media auto-posting
- [ ] Weekly CEO Briefing
- [ ] Ralph Wiggum loop
- [ ] Comprehensive logging

### Platinum Tier (60+ hours)
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

1. Claude creates file in `/vault/Pending_Approval/`
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
3. Orchestrator triggers Claude
4. Claude reads email, categorizes, drafts response
5. If sensitive → creates approval request
6. Human approves (moves to /Approved/)
7. Email MCP sends response
8. Move to /Done/, log action
```

### Bug Fix Flow

```
1. Bug report placed in /vault/Needs_Action/bugs/
2. Bug Watcher detects new report
3. Claude triggers /fix-ticket skill
4. Playwright reproduces bug
5. Claude researches and plans fix
6. Implements fix, runs tests
7. Verifies in browser
8. Commits and deploys to Vercel
9. Moves to /Done/, updates Dashboard
```

### CEO Briefing Flow

```
1. Cron triggers every Monday 7 AM
2. Claude reads Business_Goals.md
3. Analyzes /vault/Done/ for completed tasks
4. Analyzes /vault/Accounting/ for revenue
5. Detects bottlenecks from task durations
6. Audits subscriptions for cost optimization
7. Generates briefing in /vault/Briefings/
8. Creates action items in /vault/Needs_Action/
```

## 🛠️ Troubleshooting

### Watchers Not Starting
```bash
# Check Python version
python3 --version  # Need 3.13+

# Install dependencies
pip install -r requirements.txt

# Check file permissions
chmod +x scripts/watchers/*.py
```

### Claude Not Processing
```bash
# Check Claude Code installation
claude --version

# Verify vault path
cd vault
claude --prompt "Test"

# Check for items in Needs_Action
ls -la vault/Needs_Action/
```

### Playwright Errors
```bash
# Install browsers
playwright install chromium

# Test Playwright CLI
playwright-cli --help
```

## 📚 Learning Resources

- [Claude Code Docs](https://claude.com/product/claude-code)
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
