# 🚀 Personal AI Employee - Implementation Guide

## Complete Setup Instructions

This guide walks you through setting up your Personal AI Employee (Digital FTE) from scratch.

## Prerequisites Checklist

```bash
# 1. Node.js 18+ (for MCP servers and Playwright)
node -v  # Should show v18 or higher

# 2. Python 3.13+ (for watchers)
python3 --version  # Should show 3.13 or higher

# 3. Git (for version control)
git --version

# 4. Claude Code installed
claude --version
```

## Step 1: Install Dependencies

### Python Dependencies
```bash
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee/scripts
pip install -r requirements.txt
```

### Playwright Browsers
```bash
# Install Playwright CLI globally
npm install -g @playwright/cli@latest

# Install Chromium browser
playwright install chromium

# Or install Chrome (better for some sites)
npx playwright install chrome
```

### Verify Installation
```bash
# Test Playwright CLI
playwright-cli --help

# Test Python packages
python3 -c "from watchdog.observers import Observer; print('OK')"
```

## Step 2: Setup Environment

### Copy Environment File
```bash
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee
cp .env.example .env
```

### Edit .env (Optional for Bronze Tier)
For Bronze tier, you don't need any API keys. Just set:

```bash
VAULT_PATH=/home/muhammad_tayyab/hackathon/Personal_AI_Employee/vault
DEV_MODE=true
DRY_RUN=true
```

For Silver/Gold tier, add API keys as needed.

## Step 3: Initialize Vault

The vault structure is already created. Verify:

```bash
ls -la vault/
# Should show: Dashboard.md, Company_Handbook.md, Business_Goals.md
# And folders: Needs_Action/, Plans/, Done/, etc.
```

## Step 4: Configure Claude Code Skills

Skills are already in `.claude/skills/`. Verify:

```bash
ls -la .claude/skills/
# Should show: fix-ticket/, briefing/, watchers/, playwright-cli/
```

### Add Playwright MCP Server
```bash
# This was already done earlier
claude mcp list
# Should show: playwright
```

## Step 5: Start Watchers

### Option A: Start Orchestrator (Recommended)
```bash
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee/scripts/orchestrator
python3 orchestrator.py ../../vault
```

This starts:
- Filesystem Watcher
- Bug Watcher
- Auto-restart on crash
- Logging to /vault/Logs/

### Option B: Start Individual Watchers
```bash
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee/scripts/watchers

# Filesystem Watcher
python3 filesystem_watcher.py ../../vault &

# Bug Watcher
python3 bug_watcher.py ../../vault &
```

### Option C: Use PM2 (Production)
```bash
# Install PM2 globally
npm install -g pm2

# Start watchers with PM2
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee/scripts/watchers

pm2 start filesystem_watcher.py --interpreter python3 --name "fs-watcher" -- ../../vault
pm2 start bug_watcher.py --interpreter python3 --name "bug-watcher" -- ../../vault

# Save PM2 configuration (auto-start on reboot)
pm2 save
pm2 startup
```

## Step 6: Test the System

### Create Test Bug Report
```bash
cat > vault/Needs_Action/bugs/BUG-TEST-001.md << 'EOF'
---
type: bug_report
priority: P2
url: https://example.com
created: 2026-03-12T12:00:00Z
---

## Bug Description
Test bug report to verify system works

## Steps to Reproduce
1. Go to https://example.com
2. Click "More information" link
3. Check if navigation occurs

## Expected Behavior
Should navigate to example.com/more

## Actual Behavior
Testing the fix-ticket skill
EOF
```

### Trigger Claude
```bash
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee/vault
claude --prompt "Process the test bug report using /fix-ticket skill"
```

### Verify Processing
```bash
# Check if Plan was created
ls -la vault/Plans/

# Check Dashboard was updated
cat vault/Dashboard.md

# Check logs
cat vault/Logs/orchestrator/*.log
```

## Step 7: Setup Scheduled Tasks

### CEO Briefing (Weekly)
```bash
# Edit crontab
crontab -e

# Add line for Monday 7 AM briefing
0 7 * * 1 cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee/vault && claude --prompt "Generate weekly CEO briefing"
```

### Windows Task Scheduler
```powershell
# Open PowerShell as Administrator
$action = New-ScheduledTaskAction -Execute "claude" -Argument "--prompt 'Generate weekly CEO briefing'" -WorkingDirectory "C:\path\to\vault"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 7am
Register-ScheduledTask -TaskName "AI Employee CEO Briefing" -Action $action -Trigger $trigger -RunLevel Highest
```

## Step 8: Production Deployment

### Run on Cloud VM (Platinum Tier)

#### 1. Deploy to Oracle Cloud Free VM
```bash
# SSH into VM
ssh user@your-vm-ip

# Clone repository
git clone https://github.com/your-username/Personal_AI_Employee.git
cd Personal_AI_Employee

# Install dependencies
pip install -r scripts/requirements.txt
npm install -g pm2

# Setup environment
cp .env.example .env
# Edit .env with production values

# Start with PM2
cd scripts/watchers
pm2 start filesystem_watcher.py --interpreter python3 --name "fs-watcher" -- ../../vault
pm2 start bug_watcher.py --interpreter python3 --name "bug-watcher" -- ../../vault
pm2 start ../orchestrator/orchestrator.py --interpreter python3 --name "orchestrator" -- ../../vault

# Save and startup
pm2 save
pm2 startup
```

#### 2. Setup Vault Sync (Git)
```bash
# On Local machine
cd vault
git init
git add *.md Needs_Action/ Plans/ Done/
git commit -m "Initial vault"
git remote add origin git@github.com:your-username/vault.git
git push -u origin main

# On Cloud VM
cd vault
git clone git@github.com:your-username/vault.git .
```

#### 3. Configure Work-Zone Specialization
```bash
# Cloud agent config
# .claude/settings.json on Cloud VM
{
  "permissions": {
    "allow": ["mcp__playwright__*"],
    "draft_only": true
  }
}

# Local agent has final approval and send permissions
```

## Step 9: Monitoring and Maintenance

### Check Watcher Status
```bash
# PM2 status
pm2 status

# View logs
pm2 logs fs-watcher
pm2 logs bug-watcher
pm2 logs orchestrator

# Check vault logs
tail -f vault/Logs/orchestrator/*.log
```

### Dashboard Health Check
```bash
# Should show recent updates
cat vault/Dashboard.md

# Check for stuck items in Needs_Action
ls -la vault/Needs_Action/

# Check approval queue
ls -la vault/Pending_Approval/
```

### Weekly Maintenance
```bash
# 1. Review logs
cd vault/Logs
# Check for errors

# 2. Archive old completed tasks
# Move Done/ files older than 30 days to archive

# 3. Update Business Goals
# Edit vault/Business_Goals.md with new targets

# 4. Review Company Handbook
# Add new rules based on learnings
```

## Troubleshooting

### Watchers Not Starting
```bash
# Check Python path
which python3

# Check permissions
chmod +x scripts/watchers/*.py

# Check dependencies
pip3 list | grep watchdog
```

### Claude Not Processing
```bash
# Test Claude connection
claude --prompt "Hello"

# Check working directory
cd vault
claude --prompt "List files"

# Check MCP servers
claude mcp list
```

### Playwright Not Working
```bash
# Reinstall browsers
playwright install chromium --force

# Check browser installation
ls -la ~/.cache/ms-playwright/

# Test directly
playwright-cli open https://example.com
```

### Permission Errors
```bash
# Fix vault permissions
chmod -R 755 vault/
chown -R $USER:$USER vault/
```

## Next Steps

### Bronze → Silver
1. Add Gmail Watcher (requires Google API setup)
2. Add WhatsApp Watcher (requires Playwright session)
3. Setup Email MCP server
4. Implement approval workflow

### Silver → Gold
1. Setup Odoo accounting integration
2. Add social media MCP servers
3. Implement CEO Briefing automation
4. Add Ralph Wiggum loop for persistence

### Gold → Platinum
1. Deploy to cloud VM
2. Setup vault sync (Git)
3. Implement work-zone specialization
4. Add multi-agent coordination

## Success Metrics

Track these metrics to measure your AI Employee's effectiveness:

| Metric | Bronze | Silver | Gold | Platinum |
|--------|--------|--------|------|----------|
| Tasks Automated | 10% | 40% | 70% | 90% |
| Response Time | <1 hour | <30 min | <15 min | <5 min |
| Bug Fix Time | Manual | <24 hours | <4 hours | <1 hour |
| CEO Briefing | Manual | Weekly | Auto | Real-time |

## Resources

- [Full Documentation](README.md)
- [Requirements Specification](requirments.md)
- [Company Handbook](vault/Company_Handbook.md)
- [Business Goals](vault/Business_Goals.md)

---

**Need Help?**

- Wednesday Research Meetings: 10 PM PKT
- YouTube: [@panaversity](https://www.youtube.com/@panaversity)
- Hackathon Submission: [Forms](https://forms.gle/JR9T1SJq5rmQyGkGA)

**Good luck with your Personal AI Employee! 🚀**
