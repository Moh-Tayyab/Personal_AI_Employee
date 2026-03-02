# Parallel Processing - Agent Skill

---
name: parallel-process
description: |
  Processes multiple items in parallel using Agent tool for concurrent execution.
  Ideal for batch processing emails, notifications, or independent tasks.
  Uses isolation worktrees for safe parallel file operations.
allowed-tools: [Read, Write, Glob, Grep, Edit, Agent, Bash]
model: sonnet
---

# Parallel Processing - Agent Skill

Enables concurrent processing of multiple items using Claude Code's Agent tool for parallel execution.

## When to Use

- Multiple emails in Needs_Action/
- Batch processing similar items
- Independent tasks that can run simultaneously
- Time-sensitive bulk operations

## Before Implementation

| Source | Gather |
|--------|--------|
| **Needs_Action/** | List all items to process |
| **Company_Handbook.md** | Autonomy rules for each item type |
| **Available Agents** | Check agent availability |

## Workflow

### Phase 1: Discovery & Grouping
1. Scan Needs_Action/ for processable items
2. Group by type (email, social, etc.)
3. Identify dependencies between items
4. Separate independent items for parallel processing

### Phase 2: Agent Allocation

```python
# Pseudocode for agent allocation
items = scan_needs_action()
independent_items = filter(lambda x: not x.has_dependencies, items)

# Spawn agents for each independent item
for item in independent_items[:5]:  # Limit to 5 concurrent
    spawn_agent(
        task=f"process_{item.type}",
        context=item,
        tools=['Read', 'Write', 'Edit']
    )
```

### Phase 3: Parallel Execution

Use Agent tool to spawn concurrent processors:

```json
{
  "description": "Process email batch",
  "prompt": "Process all EMAIL_*.md files in Needs_Action/. For each: 1) Read file, 2) Classify priority, 3) Create Plan.md, 4) Move to In_Progress/",
  "subagent_type": "general-purpose",
  "run_in_background": true
}
```

## Agent Types

| Type | Use Case | Tools |
|------|----------|-------|
| **general-purpose** | Email processing, plan creation | Read, Write, Edit, Glob |
| **Explore** | Research, finding patterns | Read, Glob, Grep |
| **Plan** | Complex planning | Read, Write |

## Isolation Mode

For file operations, use worktree isolation:

```json
{
  "description": "Safe parallel processing",
  "prompt": "Process items without conflicts",
  "subagent_type": "general-purpose",
  "isolation": "worktree"
}
```

## Concurrency Limits

| Resource | Limit | Reason |
|----------|-------|--------|
| Concurrent agents | 5 | API rate limits |
| Background agents | 3 | Resource management |
| Items per batch | 10 | Memory constraints |

## Error Handling

| Error | Recovery |
|-------|----------|
| Agent timeout | Retry with smaller batch |
| File conflict | Use isolation worktree |
| Rate limit | Sequential fallback |

## Definition of Done

- [ ] All independent items identified
- [ ] Agents spawned for parallel processing
- [ ] Results collected and merged
- [ ] Conflicts resolved
- [ ] Audit log updated

## Example Usage

```
User: /parallel-process

Claude: Found 8 items in Needs_Action:
- 5 emails (independent)
- 2 social posts (independent)
- 1 legal document (dependent on email #3)

Spawning 5 agents for email processing...
Spawning 2 agents for social processing...

[Agent 1] Processing EMAIL_20260302_001.md
[Agent 2] Processing EMAIL_20260302_002.md
[Agent 3] Processing EMAIL_20260302_003.md
[Agent 4] Processing EMAIL_20260302_004.md
[Agent 5] Processing EMAIL_20260302_005.md
[Agent 6] Processing SOCIAL_20260302_001.md
[Agent 7] Processing SOCIAL_20260302_002.md

Waiting for results...

✅ EMAIL_001: Archived (newsletter)
✅ EMAIL_002: Draft response created
⚠️  EMAIL_003: Requires approval (new contact)
✅ EMAIL_004: Auto-responded
✅ EMAIL_005: Archived (spam)
✅ SOCIAL_001: Scheduled post
✅ SOCIAL_002: Requires approval (DM)

Holding legal document for sequential processing (depends on EMAIL_003).

Summary:
- 3 processed automatically
- 2 require approval
- 2 archived
- 1 pending sequential processing
```

---
*Version: 1.0.0 | Last Updated: 2026-03-02*