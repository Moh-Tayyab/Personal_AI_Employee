---
name: process-email
description: |
  Analyzes incoming emails from Needs_Action folder, determines priority and category,
  drafts appropriate responses, and creates actionable plans. Triggers when new email
  files appear in vault/Needs_Action/ or user requests email processing.
allowed-tools: [Read, Write, Glob, Grep, Edit]
model: sonnet
---

# Process Email - Agent Skill

Analyzes and processes incoming emails with full autonomy boundaries, approval workflows, and audit logging.

## When to Use

- New email files appear in `vault/Needs_Action/` (pattern: `EMAIL_*.md`)
- User commands: `/process-email`, "check my emails", "process inbox"
- Orchestrator triggers after Gmail watcher detection
- Scheduled email processing (morning batch)

## Before Implementation

| Source | Gather |
|--------|--------|
| **Vault** | Check `Needs_Action/` for EMAIL_*.md files |
| **Company_Handbook.md** | Communication standards, autonomy levels, approval thresholds |
| **Business_Goals.md** | Priority contacts, key projects |
| **Existing Patterns** | Check `Done/` for similar processed emails |

## Workflow

### Phase 1: Discovery
1. Scan `Needs_Action/` for `EMAIL_*.md` files
2. Read `Company_Handbook.md` autonomy rules
3. Check `Business_Goals.md` for priority context
4. Sort emails by priority (urgent → high → normal → low)

### Phase 2: Analysis
For each email, extract and determine:
- **Metadata:** id, sender, subject, timestamp, priority
- **Classification:** category, requires_response, response_deadline
- **Autonomy Check:** level (1|2|3), can_auto_respond, requires_approval
- **Suggested Actions:** reply, forward, archive, create_task, request_approval

### Phase 3: Action
| Autonomy Level | Action |
|----------------|--------|
| **Level 1** (Full Auto) | Process immediately, create Plan.md, move to Done/ |
| **Level 2** (Notify) | Draft response, create Plan.md, notify via Dashboard |
| **Level 3** (Approval) | Draft response, create approval request in Pending_Approval/ |

### Phase 4: Documentation
1. Create Plan.md in `Plans/` with objective, steps, priority, deadline
2. Update Dashboard.md with new email count, urgent items, actions pending
3. Log to `Logs/YYYY-MM-DD.json`

## Priority Determination

| Priority | Response Time | Triggers |
|----------|---------------|----------|
| **URGENT** | Immediate | ASAP, critical, emergency, legal notice, lawsuit |
| **HIGH** | 2 hours | Invoice, payment, meeting tomorrow, deadline |
| **NORMAL** | 24 hours | Standard business correspondence |
| **LOW** | 48 hours | Newsletters, marketing, FYI emails |

## Category Detection

| Keywords | Category |
|----------|----------|
| invoice, payment, bill, receipt | `invoice` |
| meeting, schedule, call, zoom | `meeting` |
| help, issue, problem, bug, error | `support` |
| proposal, quote, interested, pricing | `sales` |
| personal, family, friend | `personal` |
| contract, legal, attorney, agreement | `legal` |
| unsubscribe, promotional, newsletter | `spam` |

## Error Handling

| Error | Recovery Action |
|-------|-----------------|
| Email file malformed | Log error, skip file, create Needs_Action item |
| Company_Handbook.md missing | Use default autonomy rules, log warning |
| Cannot determine priority | Default to "normal", flag for review |
| Draft generation fails | Create placeholder, flag for manual review |
| File move fails | Retry 3 times with backoff, then alert |

## Security Considerations

### Never Do
- Send emails without approval when Level 3
- Auto-respond to legal matters
- Share credentials or sensitive data
- Bypass approval thresholds

### Always Do
- Log all actions to audit log
- Check sender against known contacts
- Validate email attachments
- Preserve original email content

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Plan.md | `Plans/PLAN_<timestamp>_EMAIL_<id>.md` | Execution plan |
| Approval Request | `Pending_Approval/EMAIL_<id>_approval.md` | HITL approval |
| Draft Response | `Drafts/DRAFT_response_<id>.md` | Response draft |
| Processed Email | `Done/EMAIL_<id>.md` | Completed item |
| Audit Log | `Logs/<date>.json` | Action logging |

## Definition of Done

- [ ] All emails in Needs_Action/ processed
- [ ] Plan.md created for each email requiring action
- [ ] Approval requests created for Level 3 items
- [ ] Dashboard.md updated with status
- [ ] Actions logged to Logs/
- [ ] Processed emails moved to Done/

## Example Usage

```
User: /process-email

Claude: I found 3 new emails in Needs_Action:

1. EMAIL_20260301_080000_client_a.md - Invoice inquiry (HIGH)
2. EMAIL_20260301_081500_newsletter.md - Newsletter (LOW)
3. EMAIL_20260301_083000_legal.md - Legal notice (URGENT)

Processing in priority order...

[URGENT] Legal notice - Creating approval request (Level 3)
[HIGH] Invoice inquiry - Drafting response (Level 2)
[LOW] Newsletter - Archiving (Level 1)

Created:
- Plans/PLAN_20260301_EMAIL_legal.md
- Pending_Approval/EMAIL_legal_approval.md
- Drafts/DRAFT_response_client_a.md
- Done/EMAIL_newsletter.md
```

## References

| File | Purpose |
|------|---------|
| `references/email-categories.md` | Detailed category detection rules |
| `references/response-templates.md` | Full response template library |
| `references/priority-rules.md` | Comprehensive priority determination |
| `references/autonomy-matrix.md` | Full autonomy decision matrix |

---
*Version: 1.0.0 | Last Updated: 2026-03-01*