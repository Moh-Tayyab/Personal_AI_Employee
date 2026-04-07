# Quick Reference Guide

## 🚀 Quick Start (30 seconds)

```bash
# Validate everything
python3 demo/validate_gold_tier.py --vault ./vault

# Run integration test
python3 demo/simple_integration_test.py

# Run full demo
python3 demo/end_to_end_demo.py --vault ./vault
```

---

## 📁 Key Directories

| Directory | Purpose |
|-----------|---------|
| `vault/Needs_Action/` | Items awaiting processing |
| `vault/Plans/` | AI-generated action plans |
| `vault/Pending_Approval/` | Awaiting human approval |
| `vault/Approved/` | Ready for execution |
| `vault/Done/` | Completed items |
| `vault/Logs/` | Daily audit logs (JSON) |
| `vault/Briefings/` | CEO weekly reports |
| `watchers/` | Gmail, WhatsApp, Filesystem monitors |
| `mcp/` | Email, Social, LinkedIn, Twitter, Odoo servers |
| `scripts/` | Helper scripts |
| `demo/` | Demo and validation scripts |

---

## 🎯 Common Commands

### Validation & Testing

```bash
# Validate all components
python3 demo/validate_gold_tier.py --vault ./vault

# Run integration test
python3 demo/simple_integration_test.py

# Run end-to-end demo
python3 demo/end_to_end_demo.py --vault ./vault

# Quick start (validation + demo)
./demo/quick_start.sh
```

### Running the Orchestrator

```bash
# DRY RUN mode (safe, default)
python3 orchestrator.py --vault ./vault --dry-run

# LIVE mode (real actions)
python3 orchestrator.py --vault ./vault --live

# With Ralph Wiggum loop
python3 orchestrator.py --vault ./vault --ralph-mode --ralph-max-iterations 10

# With health monitoring
python3 orchestrator.py --vault ./vault --health-port 8080
```

### CEO Briefing

```bash
# Generate weekly briefing
python3 scripts/generate_ceo_briefing.py --vault ./vault --period 7

# View latest briefing
ls -lt vault/Briefings/ | head -1
cat vault/Briefings/2026-04-06_CEO_Briefing.md
```

### Watchers

```bash
# Start Gmail Watcher
python3 watchers/gmail_watcher.py --vault ./vault --credentials ./secrets/credentials.json

# Start WhatsApp Watcher
python3 watchers/whatsapp_watcher.py --vault ./vault --session-path ./secrets/whatsapp_session

# Start Filesystem Watcher
python3 watchers/filesystem_watcher.py --vault ./vault
```

### Health Check

```bash
# Check health endpoint
curl http://localhost:8080/health

# View system status
cat vault/Dashboard.md
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# AI Provider (choose one)
ANTHROPIC_API_KEY=your_key
GEMINI_API_KEY=your_key
OPENROUTER_API_KEY=your_key

# Gmail API
GMAIL_CREDENTIALS_PATH=./secrets/credentials.json
GMAIL_TOKEN_PATH=./secrets/gmail_token.json

# Odoo (optional)
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_API_KEY=your_key

# Mode
DRY_RUN=true  # Set to false for real actions
```

### MCP Servers (mcp_config.json)

Copy to `~/.config/claude-code/mcp.json` for Claude Code integration.

---

## 📊 Gold Tier Features

| Feature | MCP Server | Watcher | Status |
|---------|------------|---------|--------|
| Email | ✅ Email MCP | ✅ Gmail Watcher | ✅ |
| WhatsApp | - | ✅ WhatsApp Watcher | ✅ |
| LinkedIn | ✅ LinkedIn MCP | - | ✅ |
| Twitter/X | ✅ Twitter MCP | - | ✅ |
| Facebook | ✅ Social MCP | - | ✅ |
| Instagram | ✅ Social MCP | - | ✅ |
| Odoo | ✅ Odoo MCP | - | ✅ |
| Files | ✅ Filesystem MCP | ✅ Filesystem Watcher | ✅ |

---

## 🎬 Demo Flow

1. **WhatsApp Message Arrives**
   - Watcher detects keywords (invoice, payment)
   - Creates action file in `Needs_Action/`

2. **AI Analyzes**
   - Orchestrator triggers AI
   - Creates `Plan.md` with actions
   - Flags approval requirement

3. **Human Reviews**
   - Approval request in `Pending_Approval/`
   - Human moves to `Approved/` or `Rejected/`

4. **Action Executes**
   - Orchestrator processes `Approved/` items
   - Calls appropriate MCP server
   - Logs result to `Logs/`

5. **Completion**
   - Item moved to `Done/`
   - Dashboard updated
   - Audit trail complete

---

## 🛡️ Safety

### DRY_RUN Mode

```bash
# Check current mode
echo $DRY_RUN

# Enable safe mode
export DRY_RUN=true

# Enable real actions
export DRY_RUN=false
```

### Approval Workflow

```bash
# View pending approvals
ls -la vault/Pending_Approval/

# Approve (move to Approved)
mv vault/Pending_Approval/ITEM.md vault/Approved/

# Reject (move to Rejected)
mv vault/Pending_Approval/ITEM.md vault/Rejected/
```

---

## 🐛 Troubleshooting

### Validation Fails

```bash
# Check what's missing
python3 demo/validate_gold_tier.py --vault ./vault

# Install missing dependencies
pip3 install -r requirements.txt
```

### Orchestrator Errors

```bash
# Check logs
cat vault/Logs/$(date +%Y-%m-%d).json

# Check dashboard
cat vault/Dashboard.md

# Restart orchestrator
pkill -f orchestrator.py
python3 orchestrator.py --vault ./vault
```

### Watcher Issues

```bash
# Check if running
ps aux | grep watcher

# Restart watcher
pkill -f gmail_watcher
python3 watchers/gmail_watcher.py --vault ./vault
```

### MCP Server Problems

```bash
# Test MCP server
python3 mcp/email/server.py  # Should start without errors

# Check config
cat mcp_config.json
```

---

## 📚 Documentation

- [GOLD_TIER_README.md](GOLD_TIER_README.md) - Full documentation
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details
- [AGENTS.md](AGENTS.md) - Technical specification
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [requirements.md](requirements.md) - Hackathon requirements
- [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) - Operations guide

---

## 🏆 Hackathon Submission

**Tier:** Gold Tier

**Demo Commands:**
```bash
# 1. Validate (2 min)
python3 demo/validate_gold_tier.py --vault ./vault

# 2. Integration Test (1 min)
python3 demo/simple_integration_test.py

# 3. End-to-End Demo (5 min)
python3 demo/end_to_end_demo.py --vault ./vault
```

**Features Demonstrated:**
- ✅ Multiple watchers (Gmail + WhatsApp + Files)
- ✅ Multiple MCP servers (Email, Social, LinkedIn, Twitter, Odoo)
- ✅ Human-in-the-loop approval workflow
- ✅ CEO Briefing generation
- ✅ Ralph Wiggum loop
- ✅ Error recovery and audit logging

---

**Last Updated:** 2026-04-06
**Version:** 1.0 (Gold Tier)
