---
name: ralph-loop
description: |
  Implements the Ralph Wiggum persistence pattern for autonomous task completion.
  Keeps Claude Code working on tasks until completion by preventing early exit
  and re-injecting the task prompt. Essential for autonomous AI Employee operation.
allowed-tools: [Read, Write, Glob, Grep, Edit, Bash]
---

# Ralph Loop - Professional Skill

Enables persistent, autonomous task execution by preventing early termination and continuously re-injecting the task until completion.

## When to Use

- Starting autonomous processing: `/ralph-loop "Process all emails"`
- Orchestrator-triggered processing
- Multi-step task execution
- Background batch operations

## The Ralph Wiggum Pattern

Named after the Simpsons character who says "I'm helping! I'm helping!" repeatedly, this pattern ensures Claude Code doesn't stop until the task is truly complete.

### Problem It Solves

```
Normal Claude Code:
1. Receives task
2. Works on task
3. Completes what it thinks is enough
4. Exits (task may be incomplete!)

Ralph Loop:
1. Receives task
2. Works on task
3. Tries to exit
4. Stop hook checks: Is task complete?
5. NO → Re-inject task, continue
6. YES → Allow exit
```

## Workflow

### Phase 1: Loop Initialization

```yaml
ralph_loop:
  task: "Process all items in Needs_Action"
  completion_check: "Needs_Action folder is empty"
  max_iterations: 10
  iteration_timeout: 300  # seconds
  state_file: ".ralph_state.json"
```

### Phase 2: Task Execution

```
Iteration 1:
1. Read task from state file
2. Execute task steps
3. Attempt to exit

Stop Hook:
1. Check completion condition
2. If complete → Allow exit
3. If incomplete → Inject continuation prompt
```

### Phase 3: Completion Detection

```python
def is_task_complete(state):
    # Method 1: Check completion promise
    if check_completion_promise():
        return True

    # Method 2: Check file movement
    if all_items_in_done():
        return True

    # Method 3: Check specific condition
    if state['completion_check']():
        return True

    # Method 4: Check max iterations
    if state['iterations'] >= state['max_iterations']:
        return True

    return False
```

## State File Format

```json
{
  "loop_id": "RALPH_20260301_100000",
  "created": "2026-03-01T10:00:00Z",
  "task": "Process all items in Needs_Action folder",
  "completion_promise": "TASK_COMPLETE",
  "completion_check": "folder_empty:Needs_Action",
  "max_iterations": 10,
  "current_iteration": 3,
  "iterations": [
    {
      "iteration": 1,
      "started": "2026-03-01T10:00:00Z",
      "ended": "2026-03-01T10:02:30Z",
      "actions": ["Processed EMAIL_client.md", "Created PLAN_001.md"],
      "result": "incomplete"
    },
    {
      "iteration": 2,
      "started": "2026-03-01T10:02:30Z",
      "ended": "2026-03-01T10:04:45Z",
      "actions": ["Processed WHATSAPP_contact.md", "Created approval request"],
      "result": "incomplete"
    }
  ],
  "status": "in_progress"
}
```

## Completion Strategies

### Strategy 1: Promise-Based (Simple)

Claude outputs a completion marker when done:

```markdown
<promise>TASK_COMPLETE</promise>
```

The stop hook detects this marker and allows exit.

### Strategy 2: File Movement (Recommended)

Check if task files have moved to Done/:

```python
def check_file_completion():
    needs_action = list_files("Needs_Action/*.md")
    in_progress = list_files("In_Progress/*.md")

    if not needs_action and not in_progress:
        return True  # All items processed

    return False
```

### Strategy 3: Custom Condition

Define a custom completion check:

```yaml
completion_check:
  type: "condition"
  condition: "Dashboard.md shows 0 pending items"
```

### Strategy 4: Timeout

Force completion after time limit:

```yaml
timeout:
  max_duration: 3600  # 1 hour
  action: "save_progress_and_exit"
```

## Hook Implementation

### Stop Hook Configuration

```json
// .claude/hooks/stop.json
{
  "hooks": [
    {
      "event": "stop",
      "command": "python .claude/hooks/ralph_stop.py",
      "timeout": 5000
    }
  ]
}
```

### Stop Hook Script

```python
#!/usr/bin/env python3
# .claude/hooks/ralph_stop.py

import json
import sys
from pathlib import Path

def main():
    # Read state
    state_file = Path(".ralph_state.json")
    if not state_file.exists():
        sys.exit(0)  # No active loop, allow exit

    state = json.loads(state_file.read_text())

    # Check completion
    if is_task_complete(state):
        # Task complete, allow exit
        state['status'] = 'completed'
        state_file.write_text(json.dumps(state, indent=2))
        sys.exit(0)

    # Check max iterations
    if state['current_iteration'] >= state['max_iterations']:
        state['status'] = 'max_iterations_reached'
        state_file.write_text(json.dumps(state, indent=2))
        sys.exit(0)

    # Task incomplete, continue
    state['current_iteration'] += 1
    state_file.write_text(json.dumps(state, indent=2))

    # Output continuation prompt
    continuation = f"""
Task incomplete. Continuing iteration {state['current_iteration']} of {state['max_iterations']}.

Original task: {state['task']}

Continue processing. When complete, output: <promise>TASK_COMPLETE</promise>
"""
    print(continuation)
    sys.exit(1)  # Non-zero prevents exit

def is_task_complete(state):
    # Check completion promise in last output
    # Check file movement
    # Check custom condition
    return False

if __name__ == "__main__":
    main()
```

## Usage Patterns

### Pattern 1: Process All Items

```bash
# Start Ralph loop for email processing
/ralph-loop "Process all items in Needs_Action folder. For each item: read, analyze, create plan, execute. Move processed items to Done when complete."
```

### Pattern 2: Batch Processing

```bash
# Process items in batches
/ralph-loop --batch-size 5 --max-iterations 20 "Process emails in batches of 5"
```

### Pattern 3: Scheduled Loop

```python
# Orchestrator starts loop at scheduled times
def schedule_ralph_loop():
    schedule.every().day.at("09:00").do(
        start_ralph_loop,
        task="Process overnight emails and messages"
    )
    schedule.every().day.at("17:00").do(
        start_ralph_loop,
        task="Generate end-of-day summary"
    )
```

### Pattern 4: Triggered Loop

```python
# Start loop when items appear
def on_new_item(item):
    if count_items("Needs_Action") >= 5:
        start_ralph_loop(
            task="Process accumulated items",
            max_iterations=3
        )
```

## Loop Commands

```yaml
commands:
  start:
    description: "Start a new Ralph loop"
    usage: /ralph-loop "task description"
    options:
      --max-iterations: Maximum iterations (default: 10)
      --timeout: Maximum duration in seconds (default: 3600)
      --batch-size: Items per iteration (default: all)
      --dry-run: Simulate without executing

  status:
    description: "Check current loop status"
    usage: /ralph-loop status

  stop:
    description: "Stop current loop"
    usage: /ralph-loop stop

  resume:
    description: "Resume interrupted loop"
    usage: /ralph-loop resume
```

## Safety Mechanisms

### Iteration Limit

```yaml
safety:
  max_iterations: 10
  reason: "Prevent infinite loops from incomplete tasks"
  on_limit:
    action: "save_progress_and_exit"
    notify: true
```

### Timeout Protection

```yaml
safety:
  iteration_timeout: 300  # 5 minutes per iteration
  total_timeout: 3600     # 1 hour total
  on_timeout:
    action: "save_progress_and_exit"
    notify: true
```

### Progress Tracking

```yaml
progress_tracking:
  check_stuck:
    iterations_without_progress: 3
    action: "alert_human"

  min_actions_per_iteration: 1
  action: "log_warning"
```

### Error Recovery

```yaml
error_handling:
  on_error:
    retry: true
    max_retries: 2
    backoff: exponential

  on_critical_error:
    action: "stop_loop"
    save_state: true
    notify: true
```

## Integration with Orchestrator

```python
# orchestrator.py

class Orchestrator:
    def start_processing_cycle(self):
        # Check for items to process
        items = self.scan_needs_action()

        if not items:
            return "No items to process"

        # Start Ralph loop
        return self.start_ralph_loop(
            task="Process all items in Needs_Action",
            max_iterations=10,
            completion_check=lambda: len(self.scan_needs_action()) == 0
        )

    def on_loop_complete(self, state):
        # Log completion
        self.log_completion(state)

        # Update dashboard
        self.update_dashboard()

        # Check for next cycle
        if self.has_pending_items():
            self.schedule_next_cycle()
```

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| State File | `.ralph_state.json` | Loop state |
| Iteration Log | `Logs/ralph_loop.json` | Progress tracking |
| Completion Report | `Logs/loop_completion.md` | Summary report |

## Example Session

```
User: /ralph-loop "Process all emails in Needs_Action"

Starting Ralph Loop...
Task: Process all emails in Needs_Action
Max Iterations: 10
Completion: folder_empty:Needs_Action

--- Iteration 1 ---
Found 3 emails in Needs_Action
Processing EMAIL_client_a.md...
  → Created PLAN_001.md
  → Drafted response
Processing EMAIL_client_b.md...
  → Created approval request
Processing EMAIL_newsletter.md...
  → Archived (spam)
Iteration 1 complete. 1 item remaining (pending approval).

--- Iteration 2 ---
Checking completion...
1 approval pending. Not complete.
Processing Pending_Approval/EMAIL_client_b_approval.md...
  → Waiting for human approval
Iteration 2 complete. Still waiting.

--- Iteration 3 ---
Checking completion...
Needs_Action: empty ✓
In_Progress: empty ✓
Pending_Approval: 1 item (not counted as incomplete)

Loop status: WAITING_FOR_APPROVAL
Pausing loop. Will resume when approval is processed.

To resume: /ralph-loop resume
```

## References

| File | Purpose |
|------|---------|
| `references/stop-hook.md` | Stop hook implementation |
| `references/completion-strategies.md` | Completion detection methods |
| `references/safety-mechanisms.md` | Safety and error handling |