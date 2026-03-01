# Autonomy Decision Matrix

## Overview

The autonomy matrix determines what actions the AI Employee can take
without human approval, with notification, or with explicit approval.

## Autonomy Levels

| Level | Name | Description | Example Actions |
|-------|------|-------------|-----------------|
| 1 | Full Autonomy | Execute immediately, no notification | Read emails, archive spam, categorize |
| 2 | Notify | Execute and notify human | Respond to known contacts, schedule drafts |
| 3 | Requires Approval | Wait for human approval | Respond to new contacts, payments, legal |

## Decision Matrix

### By Action Type

```yaml
action_matrix:
  read_email:
    level: 1
    auto_execute: true
    notify: false

  categorize_email:
    level: 1
    auto_execute: true
    notify: false

  archive_email:
    level: 1
    auto_execute: true
    notify: false

  draft_response:
    level: 1
    auto_execute: true
    notify: false

  send_email:
    known_contact:
      level: 2
      auto_execute: true
      notify: true
      daily_limit: 5

    new_contact:
      level: 3
      auto_execute: false
      requires_approval: true

    bulk_email:
      level: 3
      auto_execute: false
      requires_approval: true

  forward_email:
    level: 2
    auto_execute: true
    notify: true

  delete_email:
    level: 3
    auto_execute: false
    requires_approval: true

  create_calendar_event:
    draft:
      level: 1
      auto_execute: true
      notify: false

    send_invite:
      level: 2
      auto_execute: true
      notify: true

  make_payment:
    under_50_recurring:
      level: 2
      auto_execute: true
      notify: true

    any_new_payee:
      level: 3
      auto_execute: false
      requires_approval: true

    over_100:
      level: 3
      auto_execute: false
      requires_approval: true

  post_social:
    scheduled_content:
      level: 2
      auto_execute: true
      notify: true

    reply:
      level: 3
      auto_execute: false
      requires_approval: true

    dm:
      level: 3
      auto_execute: false
      requires_approval: true
```

### By Email Category

```yaml
category_matrix:
  invoice:
    received:
      acknowledge:
        level: 1
      question:
        level: 2

    overdue:
      level: 2
      notify: true
      priority: high

    over_500:
      level: 3
      requires_approval: true

  meeting:
    accept_known:
      level: 2
      notify: true

    accept_new:
      level: 3
      requires_approval: true

    decline:
      level: 2
      notify: true

    reschedule:
      level: 2
      notify: true

  support:
    acknowledge:
      level: 1

    resolve_simple:
      level: 2
      notify: true

    escalate:
      level: 1

  sales:
    quote_request:
      level: 2
      notify: true

    demo_request:
      level: 2
      notify: true

    hot_lead:
      level: 3
      requires_approval: true

  legal:
    any:
      level: 3
      requires_approval: true
      always_review: true
      never_auto_respond: true

  personal:
    known_contact:
      level: 2

    new_contact:
      level: 3
      requires_approval: true

  spam:
    archive:
      level: 1

    unsubscribe:
      level: 2
      notify: true
```

### By Sender Relationship

```yaml
sender_matrix:
  known_contacts:
    # Contacts in the address book or previous correspondence
    definition: "Email in known_contacts.json or previous outbound emails"
    rules:
      send_email:
        level: 2
        daily_limit: 10

      schedule_meeting:
        level: 2

  new_contacts:
    # First-time senders
    definition: "No previous correspondence found"
    rules:
      respond:
        level: 3
        requires_approval: true

      add_to_contacts:
        level: 3
        requires_approval: true

  priority_contacts:
    # VIP contacts defined in Business_Goals.md
    definition: "Listed in priority_contacts section"
    rules:
      respond:
        level: 2

      escalate:
        level: 1  # Immediate attention

  blocked_senders:
    definition: "Listed in blocked_senders section"
    rules:
      auto_archive:
        level: 1
      never_respond:
        level: 1
```

### By Content Sensitivity

```yaml
sensitivity_matrix:
  contains_credentials:
    detection_patterns:
      - "password"
      - "api key"
      - "secret"
      - "token"
      - "credential"
    rules:
      level: 3
      requires_approval: true
      never_store: true
      alert_immediately: true

  contains_financial:
    detection_patterns:
      - "account number"
      - "routing number"
      - "credit card"
      - "ssn"
      - "social security"
    rules:
      level: 3
      requires_approval: true

  contains_legal:
    detection_patterns:
      - "confidential"
      - "privileged"
      - "attorney-client"
      - "without prejudice"
    rules:
      level: 3
      requires_approval: true

  contains_personal:
    detection_patterns:
      - "private"
      - "personal"
      - "family"
      - "medical"
    rules:
      level: 2
      notify: true
```

## Approval Request Template

When Level 3 is triggered:

```markdown
---
type: approval_request
created: {timestamp}
expires: {24h_from_now}
level: 3
action: {proposed_action}
---

## Approval Required

**Action:** {action_type}
**Reason:** {why_level_3}
**Risk Level:** {risk_assessment}

## Context
{email_or_item_summary}

## Proposed Action
{what_will_happen}

## Risk Factors
- [ ] New contact
- [ ] Financial implications
- [ ] Legal considerations
- [ ] Contains sensitive information
- [ ] Other: {specify}

## To Approve
Move to /Approved/

## To Reject
Move to /Rejected/ with feedback

## Timeout
If no action within 24 hours, this will be escalated.
```

## Daily Limits

```yaml
daily_limits:
  emails_to_known_contacts: 10
  emails_to_new_contacts: 3  # Requires approval each
  social_posts: 5
  calendar_events: 10

limit_exceeded:
  action: require_approval
  reason: "Daily limit exceeded for {action_type}"
```

## Notification Rules

```yaml
notifications:
  level_2_actions:
    - send_email
    - forward_email
    - schedule_event
    - social_post

  methods:
    dashboard: true  # Always update Dashboard.md
    urgent_alert: false

  level_3_actions:
    - approval_request
    - send to Pending_Approval

  urgent_notifications:
    - legal_email
    - overdue_payment
    - security_alert
    - account_suspension
```

## Exception Handling

```yaml
exceptions:
  emergency_override:
    # Only for true emergencies
    condition: "human explicitly requests override"
    action: "allow level 3 action with documentation"
    require_reason: true

  system_failure:
    condition: "approval system unavailable"
    action: "queue all level 3 actions, alert human"

  timeout:
    condition: "approval not received within 24 hours"
    action: "escalate to urgent queue, notify human"
```

## Audit Logging

All actions are logged regardless of level:

```json
{
  "timestamp": "2026-03-01T10:30:00Z",
  "action_id": "ACT_20260301_001",
  "action_type": "send_email",
  "autonomy_level": 2,
  "contact_type": "known",
  "from": "ai_employee@company.com",
  "to": "client@example.com",
  "subject": "Re: Invoice #123",
  "approved_by": null,
  "result": "sent",
  "duration_ms": 523
}
```

## Configuration Location

```yaml
# In vault/Company_Handbook.md or vault/.config/autonomy.yaml

autonomy_settings:
  default_level: 2  # Start conservative
  daily_limits: true
  approval_timeout_hours: 24
  escalation_enabled: true

  # Override specific actions
  overrides:
    send_email:
      default_level: 2
      new_contact_level: 3
```