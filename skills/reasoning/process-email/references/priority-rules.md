# Priority Determination Rules

## Priority Levels Overview

| Priority | Response Time | Color Code | Icon |
|----------|---------------|------------|------|
| URGENT | Immediate (within 1 hour) | Red | 🔴 |
| HIGH | Within 2 hours | Orange | 🟠 |
| NORMAL | Within 24 hours | Yellow | 🟡 |
| LOW | Within 48 hours | Green | 🟢 |

## Urgent Priority (Immediate Response Required)

### Automatic Urgent Triggers

These keywords/phrases ALWAYS set priority to URGENT:

```yaml
urgent_keywords:
  - "ASAP"
  - "as soon as possible"
  - "urgent"
  - "critical"
  - "emergency"
  - "immediately"
  - "right away"
  - "time sensitive"
  - "deadline today"
  - "overdue"
  - "late fee"
  - "account suspended"
  - "legal notice"
  - "cease and desist"
  - "attorney"
  - "lawsuit"
```

### Context-Based Urgent

Urgent based on context:

```yaml
urgent_contexts:
  - sender: boss@company.com
    subject_pattern: ".*urgent.*"

  - subject_pattern: ".*payment\\s+overdue.*"

  - body_pattern: ".*account\\s+will\\s+be\\s+(suspended|closed|terminated).*"

  - category: legal
    always_urgent: true

  - time_sensitivity:
      deadline_today: true
      deadline_tomorrow: true
      deadline_this_week: true
```

### Urgent Escalation Rules

```yaml
escalation:
  immediate:
    - Create Needs_Action item with URGENT flag
    - Update Dashboard.md with alert
    - Send notification (if configured)
    - Do NOT wait for batch processing

  after_30_minutes:
    - If no response started, escalate
    - Add to urgent queue again

  after_1_hour:
    - Alert human directly
    - Create separate escalation record
```

## High Priority (2-Hour Response)

### Automatic High Priority Triggers

```yaml
high_keywords:
  - "invoice"
  - "payment"
  - "quote"
  - "proposal"
  - "deadline"
  - "meeting tomorrow"
  - "call today"
  - "waiting for"
  - "following up"
  - "need by"
  - "important"
```

### Category-Based High Priority

```yaml
high_categories:
  - invoice:
      if_overdue: true
      if_amount_gt: 1000  # High value invoices

  - meeting:
      if_within_24h: true

  - support:
      if_premium_customer: true
      if_repeated_issue: true

  - sales:
      if_hot_lead: true
      if_proposal_pending: true
```

### Sender-Based High Priority

```yaml
priority_contacts:
  - email: boss@company.com
    default_priority: high

  - email: important_client@client.com
    default_priority: high

  - domain: "@keyclient.com"
    default_priority: high
```

## Normal Priority (24-Hour Response)

### Default Priority

Normal is the DEFAULT priority when:
- No urgent or high triggers match
- Sender is a known business contact
- Standard business correspondence

```yaml
normal_characteristics:
  categories:
    - standard inquiry
    - information request
    - routine update
    - scheduled communication

  senders:
    - known_contacts: true
    - business_partners: true
    - colleagues: true
```

### Normal Processing Rules

```yaml
processing:
  batch: true
  batch_times: ["09:00", "13:00", "17:00"]

  auto_actions:
    - categorize
    - draft_response_if_simple
    - create_plan
```

## Low Priority (48-Hour Response)

### Automatic Low Priority Triggers

```yaml
low_keywords:
  - "newsletter"
  - "unsubscribe"
  - "promotional"
  - "marketing"
  - "no reply necessary"
  - "FYI only"
  - "for your information"
```

### Category-Based Low Priority

```yaml
low_categories:
  - newsletter:
      auto_priority: low

  - marketing:
      auto_priority: low
      auto_archive_after: 7 days

  - notification:
      if_no_action_required: true
```

### Sender-Based Low Priority

```yaml
low_senders:
  - pattern: "newsletter@*"
    auto_priority: low

  - pattern: "noreply@*"
    auto_priority: low

  - pattern: "*@marketing.*"
    auto_priority: low
```

## Priority Override Rules

### Manual Override

Human can override priority via:

```yaml
override_methods:
  - edit Needs_Action file:
      priority: urgent

  - add tag to email:
      tags: ["priority:urgent"]

  - move to urgent folder:
      path: Needs_Action/Urgent/
```

### Automatic Upgrade

Priority can be upgraded (never downgraded) automatically:

```yaml
upgrade_rules:
  - if_response_not_sent:
      after_hours: 4
      upgrade_to: high

  - if_sender_follows_up:
      upgrade_to: high

  - if_related_to_urgent_item:
      upgrade_to: urgent
```

### Time-Based Priority Adjustment

```yaml
time_adjustments:
  - end_of_business_day:
      normal_becomes: high

  - before_weekend:
      normal_becomes: high

  - before_holiday:
      normal_becomes: high
```

## Priority Calculation Algorithm

```python
def calculate_priority(email, context):
    """
    Calculate email priority based on multiple factors.
    Returns: ('urgent', 'high', 'normal', 'low')
    """
    base_priority = 'normal'

    # Check for urgent triggers (highest priority)
    if has_urgent_keywords(email):
        return 'urgent'

    if email.category == 'legal':
        return 'urgent'

    if has_urgent_context(email, context):
        return 'urgent'

    # Check for high priority triggers
    if has_high_keywords(email):
        base_priority = 'high'

    # Apply sender-based priority
    sender_priority = get_sender_priority(email.from_address)
    if priority_value(sender_priority) > priority_value(base_priority):
        base_priority = sender_priority

    # Apply category-based priority
    category_priority = get_category_priority(email.category)
    if priority_value(category_priority) > priority_value(base_priority):
        base_priority = category_priority

    # Check for low priority indicators
    if has_low_keywords(email) and base_priority == 'normal':
        base_priority = 'low'

    # Apply time-based adjustment
    if has_deadline_today(email) and base_priority != 'urgent':
        base_priority = 'high'

    return base_priority
```

## Priority Display

### Dashboard Priority Badge

```markdown
🔴 URGENT: 3 items
🟠 HIGH: 5 items
🟡 NORMAL: 12 items
🟢 LOW: 8 items
```

### Plan.md Priority Section

```yaml
---
priority: high
response_deadline: 2026-03-01T14:00:00Z
priority_reason: Invoice overdue, payment required within 2 hours
escalation_after: 2026-03-01T16:00:00Z
---
```

## Response Deadline Calculation

```python
def calculate_deadline(priority, received_time, business_hours):
    """
    Calculate response deadline based on priority and business hours.
    """
    if priority == 'urgent':
        return received_time + timedelta(hours=1)

    if priority == 'high':
        return received_time + timedelta(hours=2)

    if priority == 'normal':
        # Next business day
        deadline = received_time + timedelta(hours=24)
        return next_business_day(deadline, business_hours)

    if priority == 'low':
        deadline = received_time + timedelta(hours=48)
        return next_business_day(deadline, business_hours)
```

## Business Hours Configuration

```yaml
# In Business_Goals.md or skill_settings.json
business_hours:
  timezone: "America/New_York"
  weekdays:
    monday: "09:00-17:00"
    tuesday: "09:00-17:00"
    wednesday: "09:00-17:00"
    thursday: "09:00-17:00"
    friday: "09:00-17:00"
  holidays:
    - "2026-01-01"  # New Year's Day
    - "2026-07-04"  # Independence Day
    # Add more holidays
```