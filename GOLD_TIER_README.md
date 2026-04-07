# Personal AI Employee - Gold Tier 🏆

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A **Digital FTE (Full-Time Equivalent)** that proactively manages personal and business affairs 24/7 using Claude Code/Qwen Code as the reasoning engine and Obsidian as the management dashboard.

---

## 🎯 Gold Tier Features

| Feature | Status | Description |
|---------|--------|-------------|
| **WhatsApp Monitoring** | ✅ | Detects keywords (invoice, payment, urgent) via Playwright |
| **Gmail Monitoring** | ✅ | Monitors unread important emails via Gmail API |
| **Email Automation** | ✅ | Send/search emails via Gmail MCP server |
| **LinkedIn Posting** | ✅ | Post updates/articles via LinkedIn MCP |
| **Twitter/X Posting** | ✅ | Post tweets/threads via Twitter MCP |
| **Facebook/Instagram** | ✅ | Cross-platform posting via Social MCP |
| **Odoo Integration** | ✅ | Invoice creation/payment via Odoo MCP |
| **Approval Workflow** | ✅ | Human-in-the-loop for sensitive actions |
| **Ralph Wiggum Loop** | ✅ | Autonomous multi-step task completion |
| **CEO Briefing** | ✅ | Weekly Monday Morning CEO reports |
| **Audit Logging** | ✅ | Complete audit trail of all actions |
| **Error Recovery** | ✅ | Circuit breakers and retry logic |
| **Health Monitoring** | ✅ | HTTP health endpoint for monitoring |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Node.js v24+
- Claude Code or Qwen Code
- Obsidian (optional, for viewing)

### Setup (5 minutes)

```bash
# 1. Clone and setup
git clone <repo-url>
cd Personal_AI_Employee

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and configure environment
cp .env.example .env
# Edit .env and add your API keys

# 5. Install Playwright browsers
playwright install chromium
```

### Run Gold Tier Demo

```bash
# Quick validation
python demo/validate_gold_tier.py --vault ./vault

# Run end-to-end demo
python demo/end_to_end_demo.py --vault ./vault

# OR use the quick start script
./demo/quick_start.sh
```

All demos run in **DRY_RUN mode** - safe for testing without real external actions.

---

## 🏗️ Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                         │
│  Gmail  │  WhatsApp  │  Bank APIs  │  Files  │  Social     │
└────────┬────────┬───────────┬──────────┬─────────┬──────────┘
         │        │           │          │         │
         ▼        ▼           ▼          ▼         ▼
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                         │
│  Gmail Watcher  │  WhatsApp Watcher  │  Filesystem Watcher │
└────────┬────────┴──────────┬────────┴─────────┬─────────────┘
         │                   │                  │
         ▼                   ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT                           │
│  Needs_Action  │  Plans  │  Pending_Approval  │  Approved   │
│  Done  │  Logs  │  Briefings  │  Dashboard.md               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                          │
│              Claude Code / Qwen Code                        │
│         Ralph Wiggum Loop for Persistence                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌──────────────────────┐    ┌──────────────────────────────┐
│  HUMAN-IN-THE-LOOP   │    │         ACTION LAYER         │
│  Review & Approve    │    │  Email MCP  │  Social MCP    │
│  Pending → Approved  │    │  LinkedIn   │  Twitter MCP   │
└──────────┬───────────┘    │  Odoo MCP   │  Browser MCP   │
           │                └─────────────┬─────────────────┘
           │                             │
           └──────────┬──────────────────┘
                      ▼
              External Actions
         (Email, Social, Payments)
```

### Data Flow

1. **Detection**: Watchers monitor Gmail, WhatsApp, filesystem
2. **Creation**: New items create `.md` files in `Needs_Action/`
3. **Analysis**: Orchestrator triggers AI to analyze items
4. **Planning**: AI creates `Plan.md` with action steps
5. **Approval**: Sensitive actions go to `Pending_Approval/`
6. **Execution**: Human moves to `Approved/` → MCP executes
7. **Logging**: All actions logged to `Logs/YYYY-MM-DD.json`
8. **Completion**: Items moved to `Done/`

---

## 📁 Vault Structure

```
vault/
├── Dashboard.md              # Real-time status dashboard
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Objectives and KPIs
├── Needs_Action/             # Items requiring attention
├── In_Progress/              # Items being processed
├── Plans/                    # AI-generated action plans
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Ready for execution
├── Done/                     # Completed tasks
├── Rejected/                 # Rejected items
├── Logs/                     # Daily audit logs (JSON)
├── Briefings/                # CEO weekly reports
└── Teams/                    # Agent team logs
```

---

## 🎬 Demo Scripts

### Validation Script

Check all Gold Tier components are working:

```bash
python demo/validate_gold_tier.py --vault ./vault
```

**What it checks:**
- ✅ Vault structure (all folders exist)
- ✅ Watchers (Gmail, WhatsApp, Filesystem)
- ✅ MCP Servers (Email, LinkedIn, Twitter, Social, Odoo)
- ✅ Orchestrator (importable, initializable)
- ✅ Helper scripts (CEO Briefing, Ralph Loop, etc.)
- ✅ Dependencies (all Python packages installed)
- ✅ Environment configuration (.env, API keys)

### End-to-End Demo

Complete automation flow demonstration:

```bash
python demo/end_to_end_demo.py --vault ./vault
```

**What it demonstrates:**
1. WhatsApp message detection → Action file creation
2. AI analysis → Plan generation
3. Approval workflow → Pending → Approved
4. Email MCP execution → Send invoice
5. Social media posting → LinkedIn, Twitter, Facebook
6. Odoo invoice creation
7. Dashboard auto-update
8. CEO Briefing generation

### Quick Start Script

Run validation + demo in one command:

```bash
./demo/quick_start.sh
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```bash
# AI Provider (choose one)
ANTHROPIC_API_KEY=your_key_here
# GEMINI_API_KEY=your_key_here
# OPENROUTER_API_KEY=your_key_here

# Gmail API
GMAIL_CREDENTIALS_PATH=./secrets/credentials.json
GMAIL_TOKEN_PATH=./secrets/gmail_token.json

# Odoo (optional)
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_API_KEY=your_odoo_key

# Mode
DRY_RUN=true  # Set to false for real actions
```

### MCP Server Configuration

MCP servers are configured in `mcp_config.json`. Copy to your Claude Code config:

```bash
cp mcp_config.json ~/.config/claude-code/mcp.json
# Edit paths and credentials
```

---

## 🔄 Orchestrator Usage

### Basic Usage

```bash
# DRY RUN mode (safe)
python orchestrator.py --vault ./vault --dry-run

# LIVE mode (real actions)
python orchestrator.py --vault ./vault --live
```

### Ralph Wiggum Loop

For autonomous multi-step tasks:

```bash
# Enable Ralph mode
python orchestrator.py --vault ./vault --ralph-mode --ralph-max-iterations 10

# With custom prompt
python orchestrator.py --vault ./vault --ralph-mode --ralph-prompt "Process all pending invoices"
```

### Health Monitoring

```bash
# Start with health server
python orchestrator.py --vault ./vault --health-port 8080

# Check health
curl http://localhost:8080/health
```

---

## 📊 Gold Tier Features in Detail

### 1. WhatsApp Monitoring

**How it works:**
- Playwright monitors WhatsApp Web
- Detects keywords: invoice, payment, urgent, help
- Creates action files in `Needs_Action/`

**Setup:**
```bash
python watchers/whatsapp_watcher.py --vault ./vault --session-path ./secrets/whatsapp_session
# Scan QR code on first run
```

### 2. Gmail Monitoring

**How it works:**
- Gmail API polls for unread important emails
- Auto-marks as read after processing
- Creates structured action files

**Setup:**
```bash
# Enable Gmail API in Google Cloud Console
# Download credentials.json
python watchers/gmail_watcher.py --vault ./vault --credentials ./secrets/credentials.json
```

### 3. Email Automation (MCP)

**Capabilities:**
- Send emails with attachments
- Search emails
- Mark as read
- Send from vault-approved templates

**Example:**
```python
# Create approval file
# vault/Pending_Approval/EMAIL_invoice.md
---
action: send_email
to: client@example.com
subject: Invoice #1234 - $2,500
---

Invoice attached. Move to Approved to send.
```

### 4. Social Media Automation

**Platforms:**
- LinkedIn: Post updates with images
- Twitter/X: Post tweets and threads
- Facebook: Post to pages
- Instagram: Post with images (requires image_url)

**Cross-Platform Posting:**
```python
# Post to all platforms simultaneously
# vault/Approved/SOCIAL_announcement.md
---
action: post_cross_platform
platforms: [linkedin, twitter, facebook, instagram]
content: "Exciting announcement!"
image_url: https://example.com/image.jpg
---
```

### 5. Odoo Integration

**Capabilities:**
- Create invoices
- Post invoices
- Register payments
- Financial summaries

**Example:**
```python
# vault/Pending_Approval/ODOO_new_invoice.md
---
action: odoo_invoice
partner_name: Client Corp
partner_email: client@example.com
amount: 2500.00
---

Invoice details here...
```

### 6. CEO Briefing Generation

**Weekly Monday Morning Report:**
```bash
python scripts/generate_ceo_briefing.py --vault ./vault --period 7
```

**Includes:**
- Revenue tracking
- Completed tasks
- Bottleneck detection
- Social media summary
- Cost optimization suggestions
- Upcoming deadlines

---

## 🛡️ Safety Features

### Human-in-the-Loop

All sensitive actions require approval:

1. AI creates approval request in `Pending_Approval/`
2. Human reviews the request
3. Human moves file to `Approved/` or `Rejected/`
4. Orchestrator executes approved actions

### DRY_RUN Mode

Default mode prevents real external actions:

```bash
# Safe for testing - logs actions instead of executing
export DRY_RUN=true

# Real actions - use with caution
export DRY_RUN=false
```

### Audit Logging

Every action logged to `Logs/YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-04-06T10:30:00",
  "type": "email_sent",
  "details": {
    "to": "client@example.com",
    "subject": "Invoice #1234",
    "result": "success"
  }
}
```

### Error Recovery

- **Circuit Breakers**: Prevent cascading failures
- **Retry Logic**: Exponential backoff for transient errors
- **Quarantine**: Corrupted items moved for manual review
- **Graceful Degradation**: System continues with reduced functionality

---

## 📈 Performance Metrics

| Metric | Human FTE | Digital FTE |
|--------|-----------|-------------|
| Availability | 40 hrs/week | 168 hrs/week (24/7) |
| Monthly Cost | $4,000-$8,000 | $50-$200 |
| Ramp-up Time | 3-6 months | Instant |
| Consistency | 85-95% | 99%+ |
| Cost per Task | $3-6 | $0.25-0.50 |

---

## 🧪 Testing

### Run Validation

```bash
# Quick validation
python demo/validate_gold_tier.py

# Full end-to-end demo
python demo/end_to_end_demo.py
```

### Manual Testing

```bash
# 1. Create test item
cat > vault/Needs_Action/TEST_email_request.md << EOF
---
type: email
from: test@example.com
subject: Test Request
---

Please process this test email.
EOF

# 2. Run orchestrator briefly
python orchestrator.py --vault ./vault --dry-run

# 3. Check results
ls -la vault/Done/
cat vault/Dashboard.md
```

---

## 📚 Documentation

- [AGENTS.md](AGENTS.md) - Technical specification
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) - Operations guide
- [requirements.md](requirements.md) - Full hackathon requirements

---

## 🎓 Learning Resources

### Prerequisites
- [Claude Code Fundamentals](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [Obsidian Setup](https://help.obsidian.org/Getting+started)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)

### Core Learning
- [Claude + Obsidian Integration](https://www.youtube.com/watch?v=sCIS05Qt79Y)
- [Building MCP Servers](https://modelcontextprotocol.io/quickstart)
- [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

---

## 🏆 Hackathon Submission

### Tier Declaration: **Gold Tier**

### Features Demonstrated
- ✅ Multiple watchers (Gmail + WhatsApp + Files)
- ✅ Claude reasoning loop with Plan.md generation
- ✅ Multiple MCP servers (Email, Social, LinkedIn, Twitter, Odoo)
- ✅ Human-in-the-loop approval workflow
- ✅ Weekly CEO Briefing generation
- ✅ Error recovery and graceful degradation
- ✅ Comprehensive audit logging
- ✅ Ralph Wiggum loop for autonomous task completion

### Judging Criteria Coverage

| Criterion | Coverage |
|-----------|----------|
| **Functionality (30%)** | All Gold Tier features working |
| **Innovation (25%)** | Multi-platform automation, CEO Briefing |
| **Practicality (20%)** | Real business use cases, daily usable |
| **Security (15%)** | HITL workflow, DRY_RUN, audit logs |
| **Documentation (10%)** | This README + demo scripts |

---

## 🔧 Troubleshooting

### Common Issues

**Q: Watchers stop running**
A: Use PM2 or supervisord for process management:
```bash
pm2 start watchers/gmail_watcher.py --interpreter python3
pm2 save
```

**Q: MCP servers won't connect**
A: Check server is running and path is absolute in `mcp_config.json`

**Q: AI makes incorrect decisions**
A: Update `Company_Handbook.md` with more specific rules

**Q: WhatsApp QR code expires**
A: Run watcher with visible browser: `--headless false`

### Get Help

- Check `Logs/YYYY-MM-DD.json` for today's activity
- Run validation: `python demo/validate_gold_tier.py`
- Check health endpoint: `curl http://localhost:8080/health`

---

## 📝 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- [Claude Code](https://claude.com/product/claude-code) - Reasoning engine
- [Obsidian](https://obsidian.md) - Knowledge base & dashboard
- [Model Context Protocol](https://modelcontextprotocol.io) - External integrations
- [Panaversity Hackathon](https://agentfactory.panaversity.org)

---

**Built with ❤️ for the Personal AI Employee Hackathon 2026**
