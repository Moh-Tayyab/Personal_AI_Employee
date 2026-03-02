# /interactive-approval - Interactive Approval with Markdown Preview

---
name: interactive-approval
description: |
  Uses AskUserQuestion with markdown preview for real-time approval decisions.
  Displays formatted request details, shows context, and allows immediate
  approve/reject without moving files manually. Integrates with hooks for
  external notifications.
allowed-tools: [Read, Write, Glob, Grep, Edit, AskUserQuestion, Bash]
model: sonnet
---

# Interactive Approval - Agent Skill

Enables real-time approval decisions with rich markdown preview, eliminating the need to manually move files between folders.

## When to Use

- User wants quick approval without file management
- High-priority items needing immediate response
- Mobile-friendly approval workflow
- External webhook-triggered approvals

## Before Implementation

| Source | Gather |
|--------|--------|
| **Pending_Approval/** | List all pending requests |
| **Company_Handbook.md** | Approval rules and thresholds |
| **Approved/ & Rejected/** | Recent precedent decisions |

## Workflow

### Phase 1: Discovery
1. Scan `Pending_Approval/` for pending requests
2. Prioritize by urgency and age
3. Group similar requests for batch approval

### Phase 2: Presentation (Markdown Preview)
Use AskUserQuestion with markdown preview showing:

```markdown
## Approval Request: Send Email

**To:** client@example.com
**Subject:** Project Proposal Follow-up
**Priority:** HIGH
**Age:** 2 hours

### Email Content Preview
> Dear Client,
>
> Following up on our discussion about the project proposal...
>
> [Click to expand full content]

### Context
- This is a new contact (first communication)
- No financial commitment
- Standard business proposal follow-up

### Risk Assessment
- New contact: ⚠️ Yes
- Financial: ✅ None
- Legal: ✅ None
- Urgency: Medium

**Risk Score:** 4/10 → Level 3
```

### Phase 3: Decision
Present options:
1. **Approve** - Execute immediately
2. **Reject** - With optional reason
3. **Defer** - Schedule for later review
4. **Modify** - Request changes before approval

## AskUserQuestion Format

```json
{
  "questions": [
    {
      "question": "Approve sending email to new@client.com?",
      "header": "Approval",
      "multiSelect": false,
      "options": [
        {
          "label": "Approve",
          "description": "Execute this action immediately",
          "markdown": "See full email content and context above"
        },
        {
          "label": "Reject",
          "description": "Decline this action with reason"
        },
        {
          "label": "Defer",
          "description": "Schedule for later review (24h)"
        },
        {
          "label": "Modify",
          "description": "Request changes before approval"
        }
      ]
    }
  ]
}
```

## Batch Approvals

For multiple similar requests, offer batch processing:

```json
{
  "questions": [
    {
      "question": "3 similar email approvals pending. Process together?",
      "header": "Batch",
      "multiSelect": false,
      "options": [
        {
          "label": "Approve All",
          "description": "Execute all 3 requests"
        },
        {
          "label": "Review Individually",
          "description": "Process one at a time"
        },
        {
          "label": "Reject All",
          "description": "Decline all pending requests"
        }
      ]
    }
  ]
}
```

## Post-Decision Actions

| Decision | Action |
|----------|--------|
| **Approve** | Move to Approved/, trigger execution via MCP |
| **Reject** | Move to Rejected/, log reason |
| **Defer** | Schedule reminder, move to Deferred/ |
| **Modify** | Create modification request, notify originator |

## HTTP Hook Integration

When HTTP hooks are enabled:

```bash
# Approval triggers webhook
POST /webhook/approval
{
  "action": "approve",
  "item_id": "APPROVAL_20260302_email_client",
  "approved_by": "human",
  "timestamp": "2026-03-02T10:30:00Z"
}

# Webhook notification sent
POST https://hooks.slack.com/services/...
{
  "attachments": [{
    "color": "good",
    "text": "✅ Approved: Email to client@example.com"
  }]
}
```

## Security Considerations

### Always Verify
- User identity before approval
- Request hasn't expired
- No conflicting approvals exist

### Never Allow
- Self-approval of own requests
- Approval bypass for financial > $500
- Batch approval of mixed risk levels

## Definition of Done

- [ ] All pending requests presented with context
- [ ] User decision recorded
- [ ] File moved to appropriate folder
- [ ] Execution triggered for approvals
- [ ] Notification sent via configured webhooks
- [ ] Audit log updated

## Example Usage

```
User: /interactive-approval

Claude: I found 2 pending approval requests:

**1. Send Email to new@client.com** (HIGH priority, 2h old)
**2. Create Invoice for Acme Corp** (URGENT, 30m old)

Which would you like to review first?

[Shows markdown preview of #2 with AskUserQuestion]

┌─────────────────────────────────────────────────┐
│ Approval Required: Create Invoice               │
│                                                 │
│ **Client:** Acme Corp                           │
│ **Amount:** $1,500                              │
│ **Due:** 2026-03-15                             │
│ **Items:**                                      │
│ - Consulting: 10 hours @ $150/hr              │
│ - Software License: $0 (included)              │
│                                                 │
│ ⚠️ Payment requires approval (>$50)            │
│                                                 │
│ [Approve] [Reject] [Defer] [Modify]            │
└─────────────────────────────────────────────────┘

User: [Approve]

Claude: ✅ Invoice creation approved.
Created: Done/APPROVAL_invoice_acme_20260302.md
Executing via MCP: Creating invoice in Odoo...
Invoice #INV-2026-0042 created successfully.

Notification sent to Slack webhook.
```

## References

| File | Purpose |
|------|---------|
| `hooks/server.py` | HTTP endpoint for external approvals |
| `hooks/handlers.py` | Webhook notification handlers |
| `vault/secrets/webhooks.json` | Webhook URLs |

---
*Version: 1.0.0 | Last Updated: 2026-03-02*