---
name: request-approval
description: |
  Creates structured approval requests for actions requiring human-in-the-loop
  review. Routes requests to Pending_Approval folder with full context,
  risk assessment, and timeout handling. Triggers when Level 3 actions
  are detected or user requests approval workflow.
allowed-tools: [Read, Write, Glob, Grep, Edit]
---

# Request Approval - Professional Skill

Manages the Human-in-the-Loop (HITL) workflow by creating, routing, and tracking approval requests for sensitive actions.

## When to Use

- Level 3 autonomy actions detected (payments, new contacts, legal, etc.)
- User commands: `/request-approval`, "need approval for X"
- Plan steps marked with `⚠️ APPROVAL REQUIRED`
- Explicit human approval required by Company_Handbook.md

## Before Implementation

| Source | Gather |
|--------|--------|
| **Company_Handbook.md** | Approval thresholds, autonomy levels |
| **Pending_Approval/** | Check for existing similar requests |
| **Approved/** | Reference past approvals for patterns |
| **Rejected/** | Learn from past rejections |

## Workflow

### Phase 1: Assess Approval Need

```
1. Determine action type
2. Check autonomy level requirements
3. Identify risk factors
4. Calculate urgency
5. Set expiration time
```

### Phase 2: Create Approval Request

```yaml
Approval Request Structure:
  header:
    type: approval_request
    id: APPROVAL_{timestamp}_{action_type}_{ref}
    created: {timestamp}
    expires: {24h_default_or_custom}
    priority: urgent|high|normal
    status: pending

  action:
    type: send_email|make_payment|post_social|delete_file|etc
    summary: "One-line action description"
    details: {full_action_context}

  risk_assessment:
    level: low|medium|high|critical
    factors:
      - "Factor 1: explanation"
      - "Factor 2: explanation"
    mitigations:
      - "Mitigation 1"
      - "Mitigation 2"

  context:
    source_item: {path_to_original_item}
    plan_reference: {path_to_plan}
    related_approvals: []

  approval:
    required_from: human
    deadline: {expiration}
    timeout_action: escalate|auto_reject|remind

  instructions:
    approve: "Move this file to /Approved/"
    reject: "Move this file to /Rejected/ and add feedback"
    modify: "Edit this file and move to /Approved/"
```

### Phase 3: Write and Notify

```
1. Write approval file to Pending_Approval/
2. Update Dashboard.md with pending approval count
3. Create notification entry in Logs/notifications.json
4. (If urgent) Create urgent alert in Needs_Action/
```

## Approval Request Templates

### Email Approval

```markdown
---
type: approval_request
id: APPROVAL_20260301_100000_EMAIL_client
created: 2026-03-01T10:00:00Z
expires: 2026-03-02T10:00:00Z
priority: high
status: pending
action_type: send_email
---

# Approval Required: Send Email

## Action Summary
Send email response to new contact: client@example.com

## Email Details
| Field | Value |
|-------|-------|
| **To** | client@example.com |
| **Subject** | Re: Invoice Inquiry #1234 |
| **Category** | Invoice |
| **Autonomy Level** | 3 (New Contact) |

## Proposed Response

> Dear Client,
>
> Thank you for your inquiry about Invoice #1234.
>
> After checking our records, I can confirm that payment was received
> on February 28, 2026. The invoice is now marked as paid.
>
> Please let me know if you need any additional information.
>
> Best regards,
> [AI Employee Signature]

## Risk Assessment

| Factor | Level | Details |
|--------|-------|---------|
| New Contact | ⚠️ Medium | First correspondence with this address |
| Content Verified | ✅ Low | Invoice details confirmed in records |
| Tone Appropriate | ✅ Low | Professional, matches Company Handbook |
| No Sensitive Data | ✅ Low | No credentials or financial details |

**Overall Risk: MEDIUM**

## Why Approval Is Needed
- Recipient is not in known contacts list
- Company_Handbook.md requires approval for new contact emails

## Related Context
- Source: Needs_Action/EMAIL_20260301_client.md
- Plan: Plans/PLAN_20260301_EMAIL_client.md

---

## To Approve
Move this file to: `/Approved/`

## To Reject
Move this file to: `/Rejected/`
Add feedback below:
```
[Add rejection reason here]
```

## Timeout
This request will auto-escalate in **24 hours** if no action is taken.
```

### Payment Approval

```markdown
---
type: approval_request
id: APPROVAL_20260301_100000_PAYMENT_vendor
created: 2026-03-01T10:00:00Z
expires: 2026-03-01T18:00:00Z
priority: high
status: pending
action_type: make_payment
---

# Approval Required: Make Payment

## Action Summary
Process payment of $500.00 to Vendor B LLC

## Payment Details
| Field | Value |
|-------|-------|
| **Amount** | $500.00 |
| **Recipient** | Vendor B LLC |
| **Invoice** | INV-2024-0892 |
| **Due Date** | March 5, 2026 |
| **Method** | Bank Transfer |
| **Account** | XXXX-1234 |

## Invoice Summary
- Services: Monthly retainer - February 2026
- Period: February 1-28, 2026
- Previous Payments: On time
- Relationship: 2 years

## Risk Assessment

| Factor | Level | Details |
|--------|-------|---------|
| Amount | ⚠️ Medium | Exceeds $100 threshold |
| Vendor | ✅ Low | Known vendor, 2-year relationship |
| Budget | ✅ Low | Within allocated budget |
| Due Date | ⚠️ Medium | Due in 4 days |

**Overall Risk: MEDIUM**

## Why Approval Is Needed
- Payment amount ($500) exceeds auto-approve threshold ($100)
- All payments require Level 3 approval per Company_Handbook.md

## Verification Checklist
- [x] Invoice matches purchase order
- [x] No duplicate payments
- [x] Budget available
- [x] Vendor details verified

---

## To Approve
Move this file to: `/Approved/`

## To Reject
Move this file to: `/Rejected/`
Add feedback below:
```
[Add rejection reason here]
```

## Timeout
This request will **expire in 8 hours** due to payment urgency.
```

### Social Media Approval

```markdown
---
type: approval_request
id: APPROVAL_20260301_100000_SOCIAL_linkedin
created: 2026-03-01T10:00:00Z
expires: 2026-03-02T10:00:00Z
priority: normal
status: pending
action_type: post_social
---

# Approval Required: Social Media Post

## Action Summary
Post to LinkedIn: Company update about new product launch

## Post Details
| Platform | LinkedIn |
|----------|----------|
| Type | Company Update |
| Schedule | March 2, 2026 at 10:00 AM EST |
| Visibility | Public |

## Proposed Content

> 🚀 Exciting News!
>
> We're thrilled to announce the launch of our new product line!
> After months of development, we're ready to share what we've been
> working on.
>
> Stay tuned for more details next week!
>
> #ProductLaunch #Innovation #CompanyUpdate

## Risk Assessment

| Factor | Level | Details |
|--------|-------|---------|
| Content | ✅ Low | Professional, positive message |
| Timing | ✅ Low | Scheduled, not reactive |
| Visibility | ⚠️ Medium | Public post, permanent |
| Brand Alignment | ✅ Low | Aligns with company messaging |

**Overall Risk: LOW-MEDIUM**

## Why Approval Is Needed
- All social media posts require approval per Company_Handbook.md
- Public post represents company brand

---

## To Approve
Move this file to: `/Approved/`

## To Modify & Approve
Edit the content above, then move to: `/Approved/`

## To Reject
Move this file to: `/Rejected/`
Add feedback below:
```
[Add rejection reason here]
```
```

### Delete File Approval

```markdown
---
type: approval_request
id: APPROVAL_20260301_100000_DELETE_old_files
created: 2026-03-01T10:00:00Z
expires: 2026-03-03T10:00:00Z
priority: normal
status: pending
action_type: delete_file
---

# Approval Required: Delete Files

## Action Summary
Delete 15 files older than 1 year from Archive/ folder

## Files to Delete

| File | Size | Last Modified | Reason |
|------|------|---------------|--------|
| old_report_2024.pdf | 2.3 MB | 2024-01-15 | Retention policy |
| backup_2024_q1.zip | 45 MB | 2024-03-31 | Retention policy |
| ... (13 more) | | | |

## Total: 78.5 MB

## Risk Assessment

| Factor | Level | Details |
|--------|-------|---------|
| Irreversible | ⚠️ High | Cannot undo deletion |
| Retention Policy | ✅ Low | Complies with 1-year policy |
| No Active References | ✅ Low | No links to these files |

**Overall Risk: MEDIUM**

## Why Approval Is Needed
- File deletion is irreversible
- Company_Handbook.md requires approval for delete operations

## Mitigation
Files will be moved to Trash/ folder for 7 days before permanent deletion.

---

## To Approve
Move this file to: `/Approved/`

## To Reject
Move this file to: `/Rejected/`
```

## Expiration Handling

```yaml
expiration_rules:
  default: 24 hours

  by_priority:
    urgent: 4 hours
    high: 8 hours
    normal: 24 hours
    low: 48 hours

  by_action:
    payment: 8 hours  # Payments are time-sensitive
    email: 24 hours
    social_media: 48 hours
    file_operation: 72 hours

  timeout_actions:
    - action: remind
      when: 50% of time elapsed
    - action: escalate
      when: 75% of time elapsed
    - action: auto_reject
      when: 100% elapsed (for low priority only)
```

## Status Tracking

```yaml
approval_lifecycle:
  pending:
    - created in Pending_Approval/
    - waiting for human action

  approved:
    - moved to Approved/
    - action can proceed
    - logged with approver timestamp

  rejected:
    - moved to Rejected/
    - feedback added
    - original item updated with rejection reason

  expired:
    - no action within timeout
    - escalated or auto-rejected
    - logged as expired
```

## Audit Trail

Every approval request creates an audit entry:

```json
{
  "approval_id": "APPROVAL_20260301_100000_EMAIL_client",
  "created": "2026-03-01T10:00:00Z",
  "action_type": "send_email",
  "risk_level": "medium",
  "status": "pending",
  "expires": "2026-03-02T10:00:00Z",
  "reminders_sent": [],
  "events": [
    {
      "timestamp": "2026-03-01T10:00:00Z",
      "event": "created",
      "details": "Approval request created"
    }
  ]
}
```

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Approval Request | `Pending_Approval/{id}.md` | Human review |
| Dashboard Update | `Dashboard.md` | Pending count |
| Audit Log | `Logs/approvals.json` | Compliance trail |
| Notification | `Logs/notifications.json` | Alert record |

## References

| File | Purpose |
|------|---------|
| `references/approval-thresholds.md` | Detailed threshold rules |
| `references/risk-assessment.md` | Risk scoring methodology |
| `references/expiration-rules.md` | Timeout configurations |