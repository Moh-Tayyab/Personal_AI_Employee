---
name: process-email
description: |
  Analyzes incoming emails, determines priority and category, drafts appropriate
  responses, and creates actionable plans. Triggers when new email files appear
  in Needs_Action folder or user requests email processing.
allowed-tools: [Read, Write, Glob, Grep, Edit]
---

# Process Email - Professional Skill

Analyzes and processes incoming emails with full autonomy boundaries, approval workflows, and audit logging.

## When to Use

- New email files appear in `vault/Needs_Action/`
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

```
1. Scan Needs_Action/ for EMAIL_*.md files
2. Read Company_Handbook.md autonomy rules
3. Check Business_Goals.md for priority context
4. Sort emails by priority (urgent → high → normal → low)
```

### Phase 2: Analysis

For each email, extract and determine:

```yaml
Email Analysis:
  metadata:
    id: EMAIL_YYYYMMDD_HHMMSS_<id>
    from: sender_email
    subject: extracted_subject
    received: timestamp
    priority: urgent|high|normal|low

  classification:
    category: invoice|meeting|support|sales|personal|legal|spam
    requires_response: true|false
    response_deadline: <calculated from priority>

  autonomy_check:
    level: 1|2|3
    can_auto_respond: true|false
    requires_approval: true|false
    approval_reason: <if applicable>

  suggested_actions:
    - action_type: reply|forward|archive|create_task|request_approval
      details: <specifics>
```

### Phase 3: Action

| Autonomy Level | Action |
|----------------|--------|
| **Level 1** (Full Auto) | Process immediately, create Plan.md, move to Done/ |
| **Level 2** (Notify) | Draft response, create Plan.md, notify via Dashboard |
| **Level 3** (Approval) | Draft response, create approval request in Pending_Approval/ |

### Phase 4: Documentation

```
1. Create Plan.md in Plans/ with:
   - Objective
   - Categorized steps with checkboxes
   - Priority and deadline
   - Source reference

2. Update Dashboard.md with:
   - New email count
   - Urgent items flagged
   - Actions pending approval

3. Log to Logs/YYYY-MM-DD.json:
   - Email ID, action taken, timestamp, result
```

## Priority Determination

### Urgent Keywords (Immediate Attention)
- ASAP, critical, urgent, emergency, immediately
- payment overdue, late fee, account suspended
- legal notice, lawsuit, attorney

### High Priority Keywords (2-hour Response)
- invoice, receipt, payment due
- meeting tomorrow, call today
- deadline, due date

### Normal Priority (24-hour Response)
- Standard business correspondence
- Non-urgent requests
- FYI emails

### Low Priority (48-hour Response)
- Newsletters
- Marketing emails
- Non-urgent updates

## Category Detection

| Keywords | Category |
|----------|----------|
| invoice, payment, bill, receipt | `invoice` |
| meeting, schedule, call, zoom, calendar | `meeting` |
| help, issue, problem, bug, error | `support` |
| proposal, quote, interested, pricing | `sales` |
| personal, family, friend | `personal` |
| contract, legal, attorney, agreement | `legal` |
| unsubscribe, promotional, newsletter | `spam` |

## Response Drafting

### Response Templates by Category

**Invoice Category:**
```markdown
Subject: Re: [Original Subject]

Dear [Sender],

Thank you for your email regarding [invoice/payment].

[If confirming payment]: I confirm receipt of your invoice #[number]
for $[amount]. Payment will be processed by [date].

[If questioning]: I've received your invoice but have a question
regarding [specific item]. Could you please clarify?

Best regards,
[Signature]
```

**Meeting Category:**
```markdown
Subject: Re: [Original Subject]

Dear [Sender],

[If accepting]: I'm available for the meeting on [date] at [time].
Please send the calendar invite.

[If proposing alternative]: I'm not available at that time, but
could do [alternative date/time]. Would that work?

Best regards,
[Signature]
```

**Support Category:**
```markdown
Subject: Re: [Original Subject]

Dear [Sender],

Thank you for reaching out about [issue]. I understand this is
[frustrating/urgent/important].

[If can resolve]: Here's what I found: [solution]. Please let me
know if this resolves your issue.

[If need more info]: Could you provide more details about [specific aspect]?

Best regards,
[Signature]
```

## Approval Request Format

When autonomy level is 3, create approval request:

```markdown
# /vault/Pending_Approval/EMAIL_<id>_approval.md

---
type: approval_request
action: send_email
created: <timestamp>
expires: <24h from now>
priority: <priority>
status: pending
---

## Email Details
- **From:** <sender>
- **Subject:** <subject>
- **Category:** <category>
- **Reason for Approval:** <why Level 3>

## Proposed Response
<drafted response>

## Risk Assessment
- [ ] New contact (not in known contacts)
- [ ] Contains sensitive information
- [ ] Legal implications
- [ ] Financial commitment
- [ ] Other: <specify>

## To Approve
Move this file to /Approved/

## To Reject
Move this file to /Rejected/ and add feedback.
```

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