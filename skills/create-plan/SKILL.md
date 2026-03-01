---
name: create-plan
description: |
  Creates structured execution plans from action items in Needs_Action folder.
  Analyzes content, determines action type, extracts suggested actions, and generates
  Plan.md files with step-by-step instructions and approval requirements.
allowed-tools: [Read, Write, Glob, Grep, Edit]
model: sonnet
---

# Create Plan - Agent Skill

Generates structured, actionable execution plans from items in the Needs_Action folder with clear steps, priorities, and approval requirements.

## When to Use

- New items appear in `vault/Needs_Action/`
- User commands: `/create-plan`, "make a plan for", "plan this"
- After email or message processing
- When converting action items to executable plans

## Before Implementation

| Source | Gather |
|--------|--------|
| **Needs_Action/** | Read all unprocessed items |
| **Company_Handbook.md** | Autonomy levels, approval thresholds |
| **Business_Goals.md** | Current priorities, deadlines, resources |
| **Existing Plans/** | Check for duplicate or related plans |

## Workflow

### Phase 1: Discovery
1. Scan `Needs_Action/` for unprocessed items
2. Filter out items already with plans (check Plans/ for references)
3. Sort by priority if metadata available
4. Read relevant context from Company_Handbook.md

### Phase 2: Analysis
For each item, analyze:
- **Type:** email, whatsapp, file_drop, payment, invoice, meeting, general
- **Urgency:** Extract deadlines, time-sensitive keywords
- **Complexity:** Single action vs. multi-step workflow
- **Approval Required:** Based on autonomy matrix
- **Dependencies:** Other tasks or approvals needed

### Phase 3: Plan Generation
Create Plan.md with:
```yaml
---
plan_id: PLAN_<timestamp>_<source_type>_<id>
created: <timestamp>
source: <source_file>
priority: urgent|high|normal|low
status: pending
requires_approval: true|false
estimated_time: <duration>
---
```

### Phase 4: Documentation
1. Write Plan.md to `Plans/`
2. Update source item status to "planned"
3. Log plan creation to Dashboard.md

## Item Types Supported

| Type | Pattern | Special Handling |
|------|---------|------------------|
| **email** | `EMAIL_*.md` | Response drafting, contact check |
| **whatsapp** | `WHATSAPP_*.md` | Urgency detection, quick response |
| **file_drop** | `FILE_*.md` | Content analysis, routing |
| **payment** | `PAYMENT_*.md` | Amount threshold, approval routing |
| **invoice** | `INVOICE_*.md` | Amount check, due date extraction |
| **meeting** | `MEETING_*.md` | Calendar integration, conflicts |
| **general** | `TASK_*.md` | Standard task planning |

## Plan Template

```markdown
# Plan: <Objective>

## Overview
- **Source:** [Link to source item]
- **Priority:** <priority>
- **Status:** pending
- **Requires Approval:** Yes/No
- **Estimated Time:** <duration>

## Objective
<Clear statement of what needs to be accomplished>

## Steps
- [ ] Step 1: <action>
- [ ] Step 2: <action>
- [ ] Step 3: <action>

## Dependencies
- <List any blockers or prerequisites>

## Approval Requirements
- <If Level 3, list what needs approval>

## Success Criteria
- <How to verify completion>

## Notes
- <Additional context>
```

## Priority Calculation

| Factor | Points |
|--------|--------|
| Contains "urgent"/"ASAP"/"critical" | +3 |
| Contains "deadline"/"due"/"overdue" | +2 |
| Contains "payment"/"invoice" | +2 |
| From priority contact | +2 |
| Contains "FYI"/"newsletter" | -2 |

**Score → Priority:**
- 5+ points → URGENT
- 3-4 points → HIGH
- 1-2 points → NORMAL
- 0 or negative → LOW

## Error Handling

| Error | Recovery Action |
|-------|-----------------|
| Source file not found | Log error, skip, continue to next |
| Cannot determine type | Default to "general" type |
| Missing required fields | Create plan with placeholders, flag for review |
| Duplicate plan exists | Update existing plan instead of creating new |
| Write permission denied | Retry with backoff, alert if persistent |

## Security Considerations

### Never Do
- Create plans that bypass approval thresholds
- Include sensitive credentials in plans
- Auto-approve Level 3 actions

### Always Do
- Check autonomy level before setting approval_required
- Preserve original source content
- Log plan creation for audit trail

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Plan.md | `Plans/PLAN_<timestamp>_<type>_<id>.md` | Execution plan |
| Updated Source | `Needs_Action/<source>.md` | Status updated to "planned" |
| Dashboard | `Dashboard.md` | Plan count updated |

## Definition of Done

- [ ] All unprocessed items analyzed
- [ ] Plan.md created for each item
- [ ] Priority correctly assigned
- [ ] Approval requirements determined
- [ ] Source items updated with plan reference
- [ ] Dashboard updated

## Example Usage

```
User: /create-plan vault/Needs_Action/EMAIL_20260301_client.md

Claude: Analyzing EMAIL_20260301_client.md...

Detected:
- Type: email
- Category: invoice
- Priority: HIGH (invoice, payment due)
- Autonomy Level: 2 (known contact)
- Requires Approval: No

Creating plan...

Created: Plans/PLAN_20260301_EMAIL_client.md

Plan Summary:
- Objective: Respond to invoice inquiry from client
- Steps: 3 actions
- Estimated time: 15 minutes
- Status: Ready for execution
```

## References

| File | Purpose |
|------|---------|
| `references/plan-templates.md` | Templates by item type |
| `references/priority-matrix.md` | Priority calculation rules |
| `references/autonomy-matrix.md` | Approval requirement lookup |

---
*Version: 1.0.0 | Last Updated: 2026-03-01*