---
name: create-plan
description: |
  Creates structured execution plans from action items in Needs_Action folder.
  Analyzes item content, determines required steps, identifies approval requirements,
  and generates actionable Plan.md files. Triggers when new items appear or user
  requests planning.
allowed-tools: [Read, Write, Glob, Grep, Edit]
---

# Create Plan - Professional Skill

Transforms action items into structured, executable plans with clear steps, dependencies, and approval requirements.

## When to Use

- New items appear in `vault/Needs_Action/`
- User commands: `/create-plan`, "plan this", "create a plan for X"
- After email/WhatsApp processing
- During Ralph Wiggum loop execution

## Before Implementation

| Source | Gather |
|--------|--------|
| **Needs_Action/** | Read unprocessed items |
| **Company_Handbook.md** | Approval thresholds, autonomy rules |
| **Business_Goals.md** | Current priorities, deadlines |
| **Done/** | Reference similar completed plans |

## Workflow

### Phase 1: Item Analysis

```
1. Read item from Needs_Action/
2. Parse frontmatter and content
3. Extract:
   - Item type (email, whatsapp, payment, file_drop)
   - Source metadata
   - Requested actions
   - Priority indicators
   - Deadline hints
```

### Phase 2: Plan Generation

```yaml
Plan Structure:
  header:
    id: PLAN_{timestamp}_{type}_{reference}
    created: {timestamp}
    status: pending|in_progress|pending_approval|completed
    priority: urgent|high|normal|low
    source: {original_item_path}

  objective:
    one_line_summary: "Clear statement of what needs to be accomplished"

  steps:
    - id: step_1
      action: "Specific action to take"
      type: read|write|send|approve|wait
      status: pending|in_progress|completed|blocked
      depends_on: []  # List of step IDs
      approval_required: true|false
      estimated_time: 5m|15m|1h|etc

  approvals:
    - step_id: step_3
      reason: "Why approval is needed"
      level: 3
      created: {approval_file_path}

  deadline:
    target: {calculated_deadline}
    reason: "Why this deadline"

  risk_assessment:
    level: low|medium|high
    factors: []
```

### Phase 3: Dependency Mapping

```
1. Identify sequential dependencies (A must complete before B)
2. Identify parallel opportunities (A and B can run together)
3. Identify external dependencies (waiting for responses)
4. Identify approval checkpoints (HITL required)
```

### Phase 4: File Creation

```
1. Create Plan.md in Plans/
2. Update source item status to "planned"
3. Create approval requests if needed
4. Update Dashboard.md with new plan
```

## Item Type Templates

### Email Item Plan

```markdown
---
id: PLAN_20260301_100000_EMAIL_client_a
created: 2026-03-01T10:00:00Z
status: pending
priority: high
source: Needs_Action/EMAIL_20260301_client_a.md
deadline: 2026-03-01T14:00:00Z
---

## Objective
Respond to client inquiry about invoice #1234 and confirm payment status.

## Steps

- [ ] **Step 1: Analyze Email** (5m)
  - Read original email content
  - Extract invoice details
  - Check payment records

- [ ] **Step 2: Verify Payment** (10m)
  - Search accounting records for invoice #1234
  - Confirm payment status
  - Document findings

- [ ] **Step 3: Draft Response** (10m)
  - Use template: invoice-confirmation
  - Fill in payment details
  - Save to Drafts/

- [ ] **Step 4: Create Approval Request** (5m) ⚠️ APPROVAL REQUIRED
  - Reason: Response to new contact
  - Level: 3
  - File: Pending_Approval/EMAIL_client_a_approval.md

- [ ] **Step 5: Send Response** (2m)
  - Depends on: Step 4 approval
  - Use email MCP
  - Move to Done/

## Dependencies
- Step 4 → Step 5 (approval required)

## Risk Assessment
- Level: Low
- Factors: New contact, verify invoice details before responding

## Notes
- Client is VIP according to Business_Goals.md
- Keep response professional and timely
```

### Payment Item Plan

```markdown
---
id: PLAN_20260301_100000_PAYMENT_vendor_b
created: 2026-03-01T10:00:00Z
status: pending
priority: high
source: Needs_Action/PAYMENT_20260301_vendor_b.md
deadline: 2026-03-01T16:00:00Z
---

## Objective
Process payment request from Vendor B for services rendered.

## Steps

- [ ] **Step 1: Verify Invoice** (10m)
  - Match invoice to purchase order
  - Verify line items
  - Check for duplicates

- [ ] **Step 2: Check Budget** (5m)
  - Verify budget availability
  - Check spending limits

- [ ] **Step 3: Create Approval Request** (5m) ⚠️ APPROVAL REQUIRED
  - Reason: Payment over $100
  - Level: 3
  - Amount: $500
  - File: Pending_Approval/PAYMENT_vendor_b_approval.md

- [ ] **Step 4: Execute Payment** (5m)
  - Depends on: Step 3 approval
  - Use payment MCP
  - Record transaction

- [ ] **Step 5: Send Confirmation** (5m)
  - Email vendor with payment details
  - Update accounting records

## Dependencies
- Step 3 → Step 4 (payment approval required)

## Risk Assessment
- Level: Medium
- Factors: Financial transaction, verify vendor details

## Financial Details
- Amount: $500.00
- Vendor: Vendor B LLC
- Invoice: INV-2024-0892
- Due Date: 2026-03-05
```

### WhatsApp Item Plan

```markdown
---
id: PLAN_20260301_100000_WHATSAPP_contact_c
created: 2026-03-01T10:00:00Z
status: pending
priority: urgent
source: Needs_Action/WHATSAPP_20260301_contact_c.md
deadline: 2026-03-01T11:00:00Z
---

## Objective
Respond to urgent WhatsApp message from Contact C about meeting location change.

## Steps

- [ ] **Step 1: Analyze Message** (2m)
  - Read message content
  - Extract key information
  - Identify urgency

- [ ] **Step 2: Check Calendar** (3m)
  - Verify meeting details
  - Check for conflicts

- [ ] **Step 3: Draft Response** (5m)
  - Acknowledge new location
  - Confirm attendance
  - Save draft

- [ ] **Step 4: Send Response** (2m)
  - Use WhatsApp MCP
  - Confirm delivery
  - Move to Done/

## Dependencies
- None (can execute immediately)

## Risk Assessment
- Level: Low
- Factors: Known contact, simple acknowledgment

## Notes
- Message marked URGENT by sender
- Respond within 1 hour
```

### File Drop Plan

```markdown
---
id: PLAN_20260301_100000_FILE_report_x
created: 2026-03-01T10:00:00Z
status: pending
priority: normal
source: Needs_Action/FILE_20260301_report_x.pdf
deadline: 2026-03-02T10:00:00Z
---

## Objective
Process dropped file report_x.pdf and determine required actions.

## Steps

- [ ] **Step 1: Analyze File** (10m)
  - Read file content
  - Identify file type
  - Extract metadata

- [ ] **Step 2: Categorize** (5m)
  - Determine file purpose
  - Identify required actions
  - Check against rules

- [ ] **Step 3: Route File** (5m)
  - Move to appropriate folder
  - Create action items if needed
  - Update records

## Dependencies
- None

## Risk Assessment
- Level: Low
- Factors: Unknown file type, scan for sensitive content

## Notes
- File dropped by filesystem watcher
- Original location: /drop/report_x.pdf
```

## Plan Status Transitions

```
pending → in_progress → pending_approval → completed
                         ↓
                       blocked
                         ↓
                       completed
```

### Status Definitions

| Status | Description | Next Actions |
|--------|-------------|--------------|
| `pending` | Plan created, not started | Execute Step 1 |
| `in_progress` | Steps being executed | Continue steps |
| `pending_approval` | Waiting for human approval | Wait for /Approved/ |
| `blocked` | External dependency blocking | Resolve blocker |
| `completed` | All steps done | Move to Done/ |

## Deadline Calculation

```python
def calculate_deadline(item, priority, company_hours):
    base_hours = {
        'urgent': 1,
        'high': 2,
        'normal': 24,
        'low': 48
    }

    base_deadline = now() + timedelta(hours=base_hours[priority])

    # Adjust for explicit deadline in item
    if item.has_explicit_deadline():
        deadline = min(base_deadline, item.explicit_deadline)

    # Adjust for business hours
    deadline = next_business_hour(deadline, company_hours)

    return deadline
```

## Dependency Types

```yaml
dependency_types:
  sequential:
    description: "Step B cannot start until Step A completes"
    symbol: "→"
    example: "Step 1 → Step 2"

  parallel:
    description: "Steps can run simultaneously"
    symbol: "∥"
    example: "Step 1 ∥ Step 2"

  conditional:
    description: "Step only needed if condition is true"
    symbol: "?"
    example: "Step 3 ? (if approval needed)"

  external:
    description: "Waiting for external party"
    symbol: "⏳"
    example: "⏳ Wait for client response"

  approval:
    description: "Waiting for human approval"
    symbol: "⚠️"
    example: "⚠️ Approval required"
```

## Approval Detection

Automatic approval requirements based on:

```yaml
approval_triggers:
  action_type:
    - send_email_to_new_contact
    - make_payment
    - delete_file
    - legal_response
    - social_media_reply

  amount_threshold:
    payment_over: 100

  sensitivity:
    - contains_credentials
    - contains_financial_info
    - contains_legal_content

  sender:
    - new_contact
    - legal_domain
```

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Plan.md | `Plans/PLAN_{timestamp}_{type}_{ref}.md` | Execution plan |
| Approval Request | `Pending_Approval/{type}_{ref}_approval.md` | HITL approval |
| Updated Item | `Needs_Action/{item}.md` (status updated) | Source item |
| Dashboard Entry | `Dashboard.md` | Status display |

## Error Handling

| Error | Recovery |
|-------|----------|
| Cannot parse item | Log error, create generic plan, flag for review |
| Missing dependencies | Create plan anyway, note missing items |
| Deadline conflict | Flag conflict, use earliest deadline |
| Circular dependencies | Detect and break cycle, notify human |

## Example Usage

```
User: /create-plan Needs_Action/EMAIL_20260301_client.md

Claude: Analyzing email item...

Detected:
- Type: email
- From: client@example.com
- Subject: Invoice inquiry
- Priority: high (invoice keyword)
- Autonomy Level: 2 (known contact)

Creating plan with 4 steps:
1. Analyze email (5m) - pending
2. Verify invoice details (10m) - pending
3. Draft response (10m) - pending
4. Send response (2m) - pending

Plan created: Plans/PLAN_20260301_EMAIL_client.md

No approval required - known contact, Level 2 autonomy.
Ready to execute when approved.
```

## References

| File | Purpose |
|------|---------|
| `references/plan-templates.md` | Additional plan templates |
| `references/dependency-patterns.md` | Complex dependency handling |
| `references/deadline-rules.md` | Deadline calculation rules |