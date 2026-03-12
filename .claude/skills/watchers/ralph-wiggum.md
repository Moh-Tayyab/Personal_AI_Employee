---
name: ralph-wiggum
description: Persistence plugin that keeps Claude working until tasks are complete. Implements the Ralph Wiggum loop pattern - blocks exit and re-injects prompts until completion.
---

# Ralph Wiggum Loop Plugin

## Overview

This plugin implements the **Ralph Wiggum pattern** - a stop hook that intercepts Claude's exit and feeds the prompt back until the task is complete.

## How It Works

1. Orchestrator creates state file with prompt
2. Claude works on task
3. Claude tries to exit
4. Stop hook checks: Is task file in /Done?
5. YES → Allow exit (complete)
6. NO → Block exit, re-inject prompt (loop continues)
7. Repeat until complete or max iterations

## Usage

```bash
# Start a Ralph loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## Completion Strategies

### 1. Promise-based (Simple)
Claude outputs `<promise>TASK_COMPLETE</promise>` when done.

### 2. File Movement (Advanced - Gold tier)
Stop hook detects when task file moves to /Done.
- More reliable (completion is natural part of workflow)
- Orchestrator creates state file programmatically

## Configuration

```yaml
ralph_wiggum:
  max_iterations: 10
  completion_promise: "TASK_COMPLETE"
  check_completion_file: true
  done_folder: "/vault/Done"
  retry_delay: 5
```

## Example Flow

```
┌─────────────────────────────────────┐
│  1. Orchestrator creates task file  │
│     /Needs_Action/task-001.md       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. Claude reads and processes      │
│     Creates Plan.md                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. Claude tries to exit            │
│     Stop hook intercepts            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. Check: Is task in /Done?        │
│     NO → Re-inject prompt           │
│     YES → Allow exit                │
└─────────────────────────────────────┘
```

## State File Format

```markdown
---
type: ralph_state
task_id: task-001
created: 2026-03-12T10:00:00Z
max_iterations: 10
current_iteration: 1
status: in_progress
---

# Task

Process all files in /Needs_Action

## Completion Criteria
- All files moved to /Done
- Dashboard.md updated
- Logs written

## Previous Attempts
[Iteration history goes here]
```

## Integration with Fix Ticket

The fix-ticket skill uses Ralph Wiggum loop for autonomous bug fixing:

```bash
# Start fix-ticket with Ralph loop
/fix-ticket process-all --ralph-loop --max-iterations 5
```

Each iteration:
1. Read bug report
2. Reproduce with Playwright
3. Implement fix
4. Verify
5. If not complete → loop continues

## Error Handling

### Max Iterations Reached
```markdown
---
type: ralph_error
reason: max_iterations_reached
iterations: 10
---

## Status
Task not completed after 10 iterations

## Last Attempt
[Output from last iteration]

## Recommendation
Human review required. Check /Logs/ for details.
```

### Task Impossible
If Claude determines task cannot be completed:
1. Write error report to /Logs/
2. Move task to /Needs_Action/human_review/
3. Exit loop

## Best Practices

1. **Set reasonable max_iterations**: 5-10 for most tasks
2. **Log each iteration**: Write to /Logs/ralph/
3. **Check progress**: Each iteration should make progress
4. **Fail gracefully**: Know when to escalate to human

## Monitoring

Check Ralph loop status:
```bash
cat /vault/Plans/ralph_state.md
```

View iteration logs:
```bash
cat /vault/Logs/ralph/2026-03-12.log
```

## Example Output

```
[Ralph Wiggum Loop] Starting iteration 1/10
[Ralph Wiggum Loop] Processing 3 files in /Needs_Action
[Ralph Wiggum Loop] Created Plan.md
[Ralph Wiggum Loop] Attempting task...
[Ralph Wiggum Loop] Task incomplete, re-injecting prompt
[Ralph Wiggum Loop] Starting iteration 2/10
[Ralph Wiggum Loop] Executing plan step 2/5
[Ralph Wiggum Loop] Moving completed file to /Done
[Ralph Wiggum Loop] Starting iteration 3/10
[Ralph Wiggum Loop] All files processed!
[Ralph Wiggum Loop] Task complete - allowing exit
```

---

*Plugin Version: 1.0*
*Last Updated: 2026-03-12*
