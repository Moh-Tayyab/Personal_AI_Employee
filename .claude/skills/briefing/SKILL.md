---
name: ceo-briefing
description: Generates weekly CEO Briefing - autonomous business audit with revenue, bottlenecks, completed tasks, and proactive suggestions.
allowed-tools: Glob, Grep, Read, Write
---

# CEO Briefing Generator

## Overview

Autonomous weekly business audit that generates the "Monday Morning CEO Briefing" - a comprehensive report on revenue, bottlenecks, completed tasks, and proactive suggestions.

## Schedule

Runs every Monday at 7:00 AM (or configurable time)

## Trigger

```bash
# Manual trigger
claude --prompt "Generate weekly CEO briefing"

# Scheduled (cron)
0 7 * * 1 claude --prompt "Generate weekly CEO briefing" --cwd /path/to/vault
```

## Data Sources

| Source | Location | Purpose |
|--------|----------|---------|
| Business Goals | /vault/Business_Goals.md | Revenue targets, metrics |
| Completed Tasks | /vault/Done/*.md | Task completion data |
| Accounting | /vault/Accounting/*.md | Transactions, revenue |
| Logs | /vault/Logs/*.json | Action history |
| Calendar | /vault/Calendar/*.md | Upcoming deadlines |

## Briefing Structure

```markdown
# Monday Morning CEO Briefing

## Executive Summary
[One paragraph overview of the week]

## Revenue
- **This Week**: $X,XXX
- **MTD**: $X,XXX (XX% of $X0,000 target)
- **Trend**: On track / Behind / Ahead

## Completed Tasks
- [x] Task 1
- [x] Task 2
- [x] Task 3

## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| Task X | 2 days | 5 days | +3 days |

## Proactive Suggestions

### Cost Optimization
- Subscription audit findings
- Unused software recommendations

### Upcoming Deadlines
- Project deadlines in next 30 days
- Payment due dates
- Meeting schedules

## Key Metrics
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Response time | <24h | 12h | ✅ |
| Payment rate | >90% | 95% | ✅ |

## Action Items for CEO
- [ ] Approve subscription cancellation
- [ ] Review bottleneck analysis
- [ ] Priority decisions needed
```

## Analysis Logic

### Revenue Calculation
```python
def calculate_revenue(accounting_folder):
    total = 0
    for file in accounting_folder.glob('*.md'):
        content = file.read_text()
        # Parse payment amounts
        for line in content.split('\n'):
            if 'payment received' in line.lower():
                # Extract amount
                match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', line)
                if match:
                    total += float(match.group(1).replace(',', ''))
    return total
```

### Bottleneck Detection
```python
def detect_bottlenecks(done_folder):
    bottlenecks = []
    for file in done_folder.glob('*.md'):
        content = file.read_text()
        # Parse created and completed dates
        created = extract_date(content, 'created:')
        completed = extract_date(content, 'completed:')
        
        if created and completed:
            duration = (completed - created).days
            if duration > expected_duration:
                bottlenecks.append({
                    'task': file.stem,
                    'expected': expected_duration,
                    'actual': duration,
                    'delay': duration - expected_duration
                })
    return bottlenecks
```

### Subscription Audit
```python
def audit_subscriptions(transactions, logins):
    subscriptions = {
        'notion.so': {'name': 'Notion', 'cost': 15},
        'slack.com': {'name': 'Slack', 'cost': 10},
        'adobe.com': {'name': 'Adobe CC', 'cost': 55},
    }
    
    recommendations = []
    for domain, info in subscriptions.items():
        if domain not in logins:
            recommendations.append({
                'name': info['name'],
                'cost': info['cost'],
                'reason': 'No login in 30 days',
                'action': 'Cancel subscription'
            })
    return recommendations
```

## Metrics Tracked

| Metric | Calculation | Target |
|--------|-------------|--------|
| Revenue MTD | Sum of payments | $10,000 |
| Task Completion Rate | Done / Total | >80% |
| Avg Response Time | Avg time to first response | <24h |
| Invoice Payment Rate | Paid / Sent invoices | >90% |
| Software Costs | Sum of subscriptions | <$500/mo |

## Proactive Suggestions

### Cost Optimization
- Flag subscriptions with no activity
- Identify duplicate tools
- Alert on price increases >20%

### Process Improvements
- Highlight recurring bottlenecks
- Suggest automation opportunities
- Recommend task prioritization

### Revenue Opportunities
- Follow up on overdue invoices
- Identify upsell opportunities
- Track lead conversion

## Output Files

### Primary Briefing
`/vault/Briefings/YYYY-MM-DD_Monday_Briefing.md`

### Executive Summary (for quick reading)
`/vault/Briefings/YYYY-MM-DD_Executive_Summary.md`

### Action Items
`/vault/Needs_Action/briefing/ACTIONS_YYYY-MM-DD.md`

## Example Briefing

```markdown
---
generated: 2026-03-10T07:00:00Z
period: 2026-03-03 to 2026-03-09
week: 10
---

# Monday Morning CEO Briefing

## Executive Summary
Strong week with revenue ahead of target. Two bottlenecks identified in client onboarding. One cost-saving opportunity found.

## Revenue
- **This Week**: $2,450
- **MTD**: $4,500 (45% of $10,000 target)
- **Trend**: On track to exceed target

### Revenue Breakdown
| Source | Amount | % of Total |
|--------|--------|------------|
| Client A | $1,500 | 61% |
| Client B | $950 | 39% |

## Completed Tasks (12 total)

### High Priority
- [x] Client A invoice sent and paid
- [x] Project Alpha milestone 2 delivered
- [x] Bug fix: Homepage button (BUG-001)

### Normal Priority
- [x] Weekly social media posts scheduled
- [x] Team meeting notes documented
- [x] Code review for feature branch

## Bottlenecks

| Task | Expected | Actual | Delay | Root Cause |
|------|----------|--------|-------|------------|
| Client B proposal | 2 days | 5 days | +3 days | Waiting for requirements |
| Bug fix BUG-003 | 4 hours | 2 days | +20 hours | Complex reproduction |

### Bottleneck Analysis
- Client B proposal delayed due to missing requirements from client
- Recommendation: Add requirements checklist to proposal process

## Proactive Suggestions

### Cost Optimization 💰
- **Notion**: No team activity in 45 days. Cost: $15/month.
  - **Recommendation**: Cancel subscription
  - **Action**: Move to /Pending_Approval for review

- **Slack**: Only 2 active users. Cost: $50/month.
  - **Recommendation**: Downgrade to free tier
  - **Savings**: $50/month = $600/year

### Upcoming Deadlines 📅
- **Project Alpha**: Final delivery Jan 15 (9 days) - ON TRACK
- **Quarterly Tax Prep**: Due Jan 31 (25 days) - NOT STARTED
- **Client C Milestone**: Due Jan 20 (14 days) - AT RISK

### Follow-ups Needed
- Client B: Invoice #1234 overdue by 15 days ($1,500)
- Client D: Proposal sent 7 days ago, no response

## Key Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Client response time | <24h | 8h | ✅ Excellent |
| Invoice payment rate | >90% | 85% | ⚠️ Needs attention |
| Bug fix time (avg) | <4h | 6h | ⚠️ Slightly over |
| Task completion rate | >80% | 92% | ✅ Excellent |
| Software costs | <$500 | $340 | ✅ Under budget |

## Action Items for CEO

### Requires Approval
- [ ] Cancel Notion subscription ($15/mo savings)
- [ ] Downgrade Slack to free tier ($50/mo savings)
- [ ] Send follow-up to Client B for overdue invoice

### For Your Review
- [ ] Bottleneck analysis for Client B proposal process
- [ ] Quarterly tax prep - need accountant meeting
- [ ] Client C at-risk milestone - intervention needed?

### FYI
- Revenue on track to exceed monthly target
- Team productivity at 92% completion rate
- Two cost-saving opportunities identified ($65/mo)

---

*Briefing generated by AI Employee v1.0*
*Next briefing: March 17, 2026*
```

## Integration

### With Watchers
Watchers create files that get counted in briefing:
- Bug reports → Completed bugs count
- Emails → Response time metrics
- WhatsApp → Client communication tracking

### With Fix Ticket
Bug fixes completed by fix-ticket skill are counted:
- Bugs fixed this week
- Average fix time
- Regression rate

### With Approval Workflow
Cost optimization suggestions created as approval files:
- Move to /Pending_Approval to action
- Move to /Rejected to dismiss

## Customization

### Modify Targets
Edit `/vault/Business_Goals.md`:
```yaml
revenue_target: 10000
response_time_target: 24h
task_completion_target: 80%
```

### Add Custom Metrics
Add to briefing generation script:
```python
custom_metrics = {
    'Customer satisfaction': calculate_csat(),
    'Code quality score': calculate_quality_score(),
}
```

## Scheduling

### Linux/Mac (cron)
```bash
# Every Monday at 7 AM
0 7 * * 1 cd /path/to/vault && claude --prompt "Generate weekly CEO briefing"
```

### Windows (Task Scheduler)
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "claude" -Argument "--prompt 'Generate weekly CEO briefing'"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 7am
Register-ScheduledTask -TaskName "CEO Briefing" -Action $action -Trigger $trigger
```

---

*Skill Version: 1.0*
*Last Updated: 2026-03-12*
