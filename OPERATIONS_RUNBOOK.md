# Operations Runbook — Personal AI Employee

Quick reference for daily operations, troubleshooting, and maintenance.

---

## Quick Start

```bash
# Start all services
./scripts/start_all.sh

# Check status
./scripts/status_all.sh

# Stop all services
./scripts/stop_all.sh

# View all logs
./scripts/logs_all.sh

# Validate system health
./scripts/health_check.sh
```

---

## Daily Operations

### Morning Check (8:00 AM)

```bash
# 1. Check service status
./scripts/status_all.sh

# 2. Review pending approvals
ls vault/Pending_Approval/

# 3. Check vault queues
./scripts/status_all.sh | grep -E "Needs_Action|In_Progress|Pending"

# 4. Review yesterday's briefing
cat vault/Briefings/$(date -d 'yesterday' '+%Y-%m-%d')_*_Briefing.md 2>/dev/null || echo "No briefing found"
```

### Evening Check (6:00 PM)

```bash
# 1. Update dashboard
./scripts/status_all.sh

# 2. Check for stalled items
find vault/In_Progress -name "*.md" -mtime +1 2>/dev/null

# 3. Review daily logs
./scripts/logs_all.sh --vault

# 4. Health validation
./scripts/health_check.sh
```

---

## Common Tasks

### Process an Email Manually

```bash
# 1. Create action file
cat > vault/Needs_Action/EMAIL_manual_$(date +%s).md << 'EOF'
---
type: email
from: you@domain.com
subject: Manual Email
priority: normal
---

# Email content here
EOF

# 2. Orchestrator will pick it up on next cycle (every 30s)
# Or trigger manually:
.venv/bin/python -c "
from orchestrator import Orchestrator
orch = Orchestrator(vault_path='./vault', dry_run=True)
items = orch.check_needs_action()
for item in items:
    orch.trigger_ai(f'Process: {item.name}')
    orch.move_to_in_progress(item)
"
```

### Approve a Pending Action

```bash
# 1. Review pending items
ls -la vault/Pending_Approval/

# 2. Read the approval request
cat vault/Pending_Approval/APPROVAL_*.md

# 3. Approve (move to Approved/)
mv vault/Pending_Approval/APPROVAL_item.md vault/Approved/

# 4. Orchestrator will execute on next cycle
# Or execute manually:
.venv/bin/python -c "
from orchestrator import Orchestrator
from pathlib import Path
orch = Orchestrator(vault_path='./vault', dry_run=True)
for item in orch.check_approved():
    orch.process_approved_item(item)
    orch.move_to_done(item)
"
```

### Add a New Social Media Post

```bash
# 1. Create approved post
cat > vault/Approved/SOCIAL_linkedin_$(date +%s).md << 'EOF'
---
type: approval_response
action: linkedin_post
content: Your post content here (max 3000 chars)
visibility: PUBLIC
---

# LinkedIn Post
EOF

# 2. Orchestrator will execute automatically
# Or manually:
./scripts/start_all.sh --no-pm2
.venv/bin/python orchestrator.py --vault ./vault --dry-run
```

---

## Scheduled Tasks

| Task | Schedule | Script |
|------|----------|--------|
| Process Needs_Action | Every 5 min | `scripts/cron/process_needs_action.sh` |
| Daily Briefing | 8:00 AM | `scripts/cron/daily_briefing.sh` |
| Weekly CEO Briefing | Monday 7:00 AM | `scripts/cron/weekly_ceo_briefing.sh` |
| Health Check | Every hour | `scripts/cron/health_check.sh` |

### View Cron Schedule

```bash
crontab -l | grep "Personal AI Employee"
```

### Disable/Enable Cron

```bash
# Disable
./scripts/setup_cron.sh --remove

# Re-enable
./scripts/setup_cron.sh
```

---

## Troubleshooting

### Service Not Starting

```bash
# Check Python environment
./scripts/status_all.sh

# Check for missing dependencies
.venv/bin/pip install -e .

# Check ecosystem config
cat ecosystem.config.js

# Try direct start
.venv/bin/python orchestrator.py --vault ./vault --dry-run
```

### High Memory Usage

```bash
# Check PM2 memory
pm2 monit

# Restart heavy services
pm2 restart ai-orchestrator
pm2 restart gmail-watcher

# Reset if needed
./scripts/reset_all.sh --all
```

### Stuck In_Progress Items

```bash
# View stuck items
find vault/In_Progress -name "*.md" -exec echo "  {}" \;

# Move back to Needs_Action
mv vault/In_Progress/*.md vault/Needs_Action/

# Or use reset script
./scripts/reset_all.sh
```

### Corrupted Logs

```bash
# Validate today's log
python3 -c "import json; json.load(open('vault/Logs/$(date +%Y-%m-%d).json'))"

# If corrupted, rename it
mv vault/Logs/$(date +%Y-%m-%d).json vault/Logs/$(date +%Y-%m-%d).json.bak
```

### MCP Server Errors

```bash
# Validate all MCP servers
./scripts/health_check.sh

# Test individual server
.venv/bin/python -c "
from orchestrator import Orchestrator
orch = Orchestrator(vault_path='./vault', dry_run=True)
print(orch._call_mcp_server('email', 'send_email', {
    'to': 'test@test.com', 'subject': 'T', 'body': 'B', 'cc': '', 'bcc': ''
}))
"
```

---

## Reset Procedures

### Soft Reset (Recommended)

```bash
# Moves In_Progress → Needs_Action
# Clears old logs (>7 days)
# Keeps Done, Plans, Approved intact
./scripts/reset_all.sh --dry-run   # Preview
./scripts/reset_all.sh             # Execute
```

### Full Reset

```bash
# Also clears Done, Rejected, Plans, Briefings
# Does NOT touch Approved or Pending_Approval
./scripts/reset_all.sh --all --dry-run
./scripts/reset_all.sh --all
```

### Nuclear Reset (Everything)

```bash
# Clears ALL vault folders except handbook/goals/dashboard
rm -rf vault/Needs_Action/* vault/In_Progress/* vault/Done/*
rm -rf vault/Pending_Approval/* vault/Approved/* vault/Rejected/*
rm -rf vault/Plans/* vault/Briefings/* vault/Logs/*
```

---

## Production Deployment

### PM2 Setup (24/7)

```bash
# Install PM2
npm install -g pm2

# Start services
./scripts/start_all.sh

# Save process list
pm2 save

# Enable auto-start on boot
pm2 startup

# Monitor
pm2 monit
```

### Cloud VM Deployment (Platinum Tier)

```bash
# 1. Create VM (Oracle Cloud Free Tier recommended)
# 2. Clone repository
git clone <repo-url>
cd Personal_AI_Employee

# 3. Install dependencies
.venv/bin/python -m pip install -e .

# 4. Configure .env
cp .env.example .env
# Edit .env with production values

# 5. Start services
./scripts/start_all.sh

# 6. Set up health monitoring
./scripts/setup_cron.sh

# 7. Enable auto-start
pm2 save && pm2 startup
```

---

## Configuration Reference

### Environment Variables (.env)

| Variable | Purpose | Default |
|----------|---------|---------|
| `VAULT_PATH` | Path to Obsidian vault | `./vault` |
| `DRY_RUN` | Prevent real actions | `true` |
| `HEALTH_PORT` | Health server port | `8080` |
| `DEV_MODE` | Development mode | `false` |

### MCP Server Credentials

| Server | Required Variables |
|--------|-------------------|
| Email | `GMAIL_CREDENTIALS_PATH`, Gmail OAuth token |
| LinkedIn | `LINKEDIN_ACCESS_TOKEN` |
| Twitter | `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET` |
| Social (FB/IG) | `META_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID` |
| Odoo | `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_API_KEY` |

---

## Emergency Contacts

- **Health check failing**: `./scripts/health_check.sh --strict`
- **All services down**: `./scripts/start_all.sh`
- **Need to stop immediately**: `./scripts/stop_all.sh --force`
- **Data loss concern**: Check `vault/Logs/` for audit trail
- **Get help**: Review `AGENTS.md` and `requirements.md`
