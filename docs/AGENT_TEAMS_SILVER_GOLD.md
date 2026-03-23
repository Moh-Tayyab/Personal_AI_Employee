# Agent Teams for Silver & Gold Tier Completion

## Overview

This guide explains how to use **Claude Agent Teams** to complete all Silver and Gold tier requirements for your Personal AI Employee.

Agent teams allow multiple specialized Claude instances to work together, each focusing on their domain of expertise while coordinating through the vault structure.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Teams Coordinator                       │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────────┐   ┌─────────────────┐
│   Email       │   │  Social Media     │   │  Accounting     │
│  Specialist   │   │    Manager        │   │   Specialist    │
│               │   │                   │   │                 │
│ - Process     │   │ - LinkedIn        │   │ - Odoo ERP      │
│   emails      │   │ - Twitter/X       │   │ - Invoices      │
│ - Draft       │   │ - Facebook        │   │ - Expenses      │
│   responses   │   │ - Content         │   │ - Validation    │
│ - Send via    │   │   creation        │   │ - Financial     │
│   Gmail MCP   │   │ - Scheduling      │   │   reports       │
└───────────────┘   └───────────────────┘   └─────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Vault Structure│
                    │  (Coordination) │
                    └─────────────────┘
```

---

## Agent Roles

### Silver Tier Agents

#### 1. Email Specialist
**Purpose:** Handle all email-related operations

**Responsibilities:**
- Process emails from `vault/Needs_Action/email/`
- Analyze email content and sentiment
- Draft appropriate responses
- Manage approval workflow for sensitive emails
- Send emails via Gmail MCP server
- Log all actions and move processed items to `Done/`

**Autonomy Level:** L2 - Draft only, send requires approval

**Approval Triggers:**
- Multiple recipients (>10)
- Sensitive keywords (partnership, investment, legal)
- Financial content

**Files:**
- Script: `scripts/agents/email_specialist.py`
- Logs: `vault/Logs/email_specialist.log`

---

#### 2. Social Media Manager
**Purpose:** Manage social media presence across platforms

**Responsibilities:**
- Create platform-optimized content
- Post to LinkedIn, Twitter, Facebook via MCP servers
- Schedule posts for optimal engagement times
- Monitor and respond to engagement
- Maintain brand voice consistency

**Autonomy Level:** L3 - Auto-post routine content

**Platform Specifications:**
| Platform | Optimal Length | Best Days | Best Times |
|----------|---------------|-----------|------------|
| LinkedIn | 150-300 words | Tue-Thu | 9AM, 12PM, 5PM |
| Twitter | 280 chars | Wed-Fri | 9AM, 12PM, 6PM |
| Facebook | 40-80 words | Thu-Sun | 9AM, 1PM, 3PM |

**Files:**
- Script: `scripts/agents/social_media_manager.py`
- Logs: `vault/Logs/social_media_manager.log`

---

### Gold Tier Agents

#### 3. Accounting Specialist
**Purpose:** Handle accounting operations via Odoo ERP

**Responsibilities:**
- Process invoices and expenses
- Create invoices in Odoo
- Validate invoices (based on amount thresholds)
- Manage customer/vendor contacts
- Categorize expenses
- Generate financial reports

**Autonomy Level:** L2 - Create drafts, validate requires approval for >$500

**Approval Thresholds:**
- Auto-validate: ≤ $100
- Create only: $100 - $500
- Approval required: > $500

**Files:**
- Script: `scripts/agents/accounting_specialist.py`
- Logs: `vault/Logs/accounting_specialist.log`

---

#### 4. Executive Reporter (CEO Briefing Generator)
**Purpose:** Generate weekly executive reports

**Responsibilities:**
- Collect weekly activity data from all sources
- Analyze KPIs and business metrics
- Generate comprehensive CEO briefings
- Identify bottlenecks and suggest improvements
- Save briefings to `vault/Briefings/`

**Autonomy Level:** L4 - Full autonomy for report generation

**Briefing Structure:**
1. Executive Summary
2. Revenue Summary (target vs actual)
3. Completed Tasks analysis
4. Pending Items
5. Bottlenecks identification
6. Activity logs summary
7. Actionable suggestions

**Files:**
- Script: `scripts/generate_briefing.py`

---

## Quick Start

### 1. List Available Tasks

```bash
# See what tasks are waiting in Needs_Action
./scripts/run_agent_teams.sh --list-tasks
```

### 2. Run in Dry-Run Mode (Recommended First)

```bash
# Run all agents in dry-run mode (no actual actions)
./scripts/run_agent_teams.sh --all --report
```

### 3. Run in Live Mode

```bash
# Run all agents with actual actions
./scripts/run_agent_teams.sh --all --live --report
```

### 4. Run Specific Agents

```bash
# Only process emails
./scripts/run_agent_teams.sh --email --report

# Only process social media
./scripts/run_agent_teams.sh --social --report

# Only process accounting
./scripts/run_agent_teams.sh --accounting --report
```

---

## Configuration

### Agent Teams Config File

Location: `config/agent_teams_config.json`

```json
{
  "teams": {
    "silver-tier-completion": {
      "name": "Silver Tier Completion Team",
      "members": [
        {
          "id": "email-specialist",
          "role": "Email Specialist",
          "autonomy_level": "L2"
        },
        {
          "id": "social-media-manager",
          "role": "Social Media Manager",
          "autonomy_level": "L3"
        }
      ]
    },
    "gold-tier-completion": {
      "name": "Gold Tier Completion Team",
      "members": [
        {
          "id": "accounting-specialist",
          "role": "Accounting Specialist",
          "autonomy_level": "L2"
        },
        {
          "id": "executive-reporter",
          "role": "Executive Reporter",
          "autonomy_level": "L4"
        }
      ]
    }
  }
}
```

### Environment Variables

Add to `.env`:

```bash
# Odoo Configuration (for Accounting Specialist)
ODOO_URL=http://your-odoo-server:8069
ODOO_DB=your_database
ODOO_USERNAME=admin
ODOO_API_KEY=your_api_key

# Approval Thresholds
PAYMENT_APPROVAL_THRESHOLD=500
EMAIL_APPROVAL_THRESHOLD=10
AUTO_APPROVE_LOW_PRIORITY_BUGS=true

# Notification Settings (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK
```

---

## Workflows

### Email Processing Workflow

```
1. Email arrives in vault/Needs_Action/email/
         │
         ▼
2. Email Specialist analyzes content
         │
         ▼
3. Determine if approval needed
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    ▼         ▼
4a. Create  4b. Draft/Send
    approval      email
    request       │
    │             │
    ▼             ▼
5. Human      5. Move to
    reviews     Done/
    │
    ▼
6. If approved,
   send email
```

### Social Media Posting Workflow

```
1. Task in vault/Needs_Action/
         │
         ▼
2. Social Media Manager reads requirements
         │
         ▼
3. Create platform-optimized content
         │
         ▼
4. Check if approval needed
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    ▼         ▼
4a. Create  4b. Publish
    approval  to platform
    request   │
    │         │
    ▼         ▼
5. Human    5. Log action
    reviews   │
    │         ▼
    ▼       6. Move to Done/
6. If approved,
   publish
```

### Invoice Processing Workflow

```
1. Invoice in vault/Needs_Action/
         │
         ▼
2. Accounting Specialist extracts details
         │
         ▼
3. Create invoice in Odoo
         │
         ▼
4. Check amount vs threshold
         │
    ┌────┴────┐
    │         │
  >$500     ≤$500
    │         │
    ▼         ▼
4a. Create  4b. Auto-validate
    approval  │
    request   │
    │         ▼
    ▼       5. Categorize
5. Human      expense
    reviews   │
    │         ▼
    ▼       6. Move to Done/
6. If approved,
   validate
```

---

## Monitoring and Reporting

### Check Agent Logs

```bash
# Email agent logs
tail -f vault/Logs/email_specialist.log

# Social media logs
tail -f vault/Logs/social_media_manager.log

# Accounting logs
tail -f vault/Logs/accounting_specialist.log

# All logs (last 50 lines each)
find vault/Logs -name "*.log" -exec tail -50 {} \;
```

### View Generated Reports

```bash
# List recent reports
ls -lt vault/Logs/*report*.md | head -10

# View latest email report
cat vault/Logs/email_report_*.md | tail -50

# View latest social media report
cat vault/Logs/social_report_*.md | tail -50

# View latest accounting report
cat vault/Logs/accounting_report_*.md | tail -50
```

### Check Task Status

```bash
# Pending approvals
ls -la vault/Pending_Approval/

# Completed tasks
ls -la vault/Done/

# Active team status
cat vault/Teams/Active/*.md 2>/dev/null || echo "No active teams"
```

---

## Troubleshooting

### Agent Not Processing Tasks

**Symptoms:** Tasks remain in `Needs_Action/` after running

**Solutions:**
1. Check if agent script exists:
   ```bash
   ls -la scripts/agents/
   ```

2. Verify Python environment:
   ```bash
   source .venv/bin/activate
   python -c "import sys; print(sys.executable)"
   ```

3. Run agent manually with verbose output:
   ```bash
   python scripts/agents/email_specialist.py --vault ./vault --dry-run
   ```

### MCP Server Connection Failed

**Symptoms:** Error connecting to Gmail, LinkedIn, Odoo, etc.

**Solutions:**
1. Verify MCP server exists:
   ```bash
   ls -la mcp/email/
   ls -la mcp/linkedin/
   ls -la mcp/odoo/
   ```

2. Check authentication:
   ```bash
   # Gmail
   ls -la vault/secrets/gmail_token.json
   
   # LinkedIn
   ls -la vault/secrets/linkedin_session/
   ```

3. Re-authenticate if needed:
   ```bash
   python scripts/fix_gmail_token.py
   ```

### Approval Workflow Stuck

**Symptoms:** Items remain in `Pending_Approval/` indefinitely

**Solutions:**
1. Review pending items:
   ```bash
   ls -la vault/Pending_Approval/
   cat vault/Pending_Approval/*/APPROVAL_*.md
   ```

2. Manually approve by moving file:
   ```bash
   mv vault/Pending_Approval/Emails/APPROVAL_* vault/Approved/Emails/
   ```

3. Run orchestrator to process approved items:
   ```bash
   python orchestrator.py --vault ./vault
   ```

---

## Best Practices

### When to Use Agent Teams

✅ **Use Agent Teams when:**
- Multiple domains need attention (email + social + accounting)
- 5+ independent tasks to process
- Complex workflows requiring different expertise
- Need parallel processing for efficiency

❌ **Don't use Agent Teams when:**
- Single domain task (only email or only social)
- Sequential tasks (each step depends on previous)
- Simple tasks (<15 minutes total)
- Multiple agents would edit same files

### Approval Guidelines

**Auto-approve (L3-L4 autonomy):**
- Routine email responses (single recipient)
- Regular social media posts (not announcements)
- Expenses ≤ $100

**Require approval (L1-L2 autonomy):**
- Partnership inquiries
- Major announcements
- Expenses > $500
- Legal/financial commitments

### Logging Best Practices

1. **Log everything:** Every action should be logged
2. **Structured logs:** Use JSON for programmatic access
3. **Daily rotation:** New log file each day
4. **Include context:** Timestamp, agent, task, result

---

## Advanced Usage

### Custom Agent Creation

To create a new specialized agent:

1. Create script in `scripts/agents/`:
   ```python
   # scripts/agents/research_analyst.py
   class ResearchAnalystAgent:
       def __init__(self, vault_path, dry_run=True):
           # Initialize
           
       def process_research_task(self, file_path):
           # Process task
   ```

2. Add to `run_agent_teams.sh`:
   ```bash
   # Add new option
   --research)
       RUN_RESEARCH=true
       shift
       ;;
   
   # Add execution block
   if $RUN_ALL || $RUN_RESEARCH; then
       python3 "$SCRIPT_DIR/agents/research_analyst.py" ...
   fi
   ```

3. Update `config/agent_teams_config.json`

### Scheduling Agent Runs

Add to crontab for automated processing:

```bash
# Run email agent every hour
0 * * * * cd /path/to/project && ./scripts/run_agent_teams.sh --email

# Run social media agent at 9 AM, 12 PM, 5 PM
0 9,12,17 * * * cd /path/to/project && ./scripts/run_agent_teams.sh --social

# Run all agents every 4 hours
0 */4 * * * cd /path/to/project && ./scripts/run_agent_teams.sh --all

# Generate CEO briefing every Monday at 8 AM
0 8 * * 1 cd /path/to/project && python scripts/generate_briefing.py
```

---

## Success Criteria

### Silver Tier Completion

✅ **Email Specialist:**
- [ ] All emails in `Needs_Action/` processed
- [ ] Responses drafted or sent
- [ ] Approval workflow functioning
- [ ] Logs created for each action

✅ **Social Media Manager:**
- [ ] All social tasks processed
- [ ] Content created for each platform
- [ ] Posts published (or drafts created)
- [ ] Platform optimization applied

### Gold Tier Completion

✅ **Accounting Specialist:**
- [ ] All invoices processed
- [ ] Invoices created in Odoo
- [ ] Approval workflow for high-value items
- [ ] Expenses categorized correctly

✅ **Executive Reporter:**
- [ ] Weekly CEO briefing generated
- [ ] KPIs calculated and reported
- [ ] Bottlenecks identified
- [ ] Actionable suggestions provided

---

## Next Steps

After completing Silver and Gold tiers:

1. **Review reports** in `vault/Logs/`
2. **Process pending approvals** in `vault/Pending_Approval/`
3. **Verify completed tasks** in `vault/Done/`
4. **Generate final status report:**
   ```bash
   python scripts/complete_silver_gold_tiers.py --vault ./vault --report
   ```

---

## Support

- **Documentation:** `docs/AGENT_TEAMS_GUIDE.md`
- **Configuration:** `config/agent_teams_config.json`
- **Scripts:** `scripts/agents/`, `scripts/run_agent_teams.sh`
- **Logs:** `vault/Logs/`

---

**🎯 Goal:** Transform your Personal AI Employee from a single agent into a coordinated workforce capable of handling complex, multi-domain business operations efficiently and reliably.
