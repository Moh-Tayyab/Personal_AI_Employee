# Skill Evaluation Guide

Integrate evaluations into your skill creation workflow.

## Quick Start

When creating a new skill, follow this pattern:

```bash
# 1. Create skill
scripts/init_skill.py my-skill --path skills/

# 2. Create eval prompt set
touch evals/prompt-sets/my-skill.csv

# 3. Create check functions
touch evals/checks/my_skill_checks.py

# 4. Run evals during development
python evals/runner.py --skill my-skill --prompt-set evals/prompt-sets/my-skill.csv
```

## When to Create Evals

| Skill Type | Eval Priority | Focus Areas |
|------------|---------------|-------------|
| **Action skills** (MCP handlers) | HIGH | Command execution, file changes |
| **Reasoning skills** (analysis) | HIGH | Outcome accuracy, categorization |
| **Orchestration skills** | MEDIUM | Workflow completion, handoffs |
| **Perception skills** (watchers) | HIGH | Detection accuracy, false positives |
| **Intelligence skills** (briefings) | MEDIUM | Content quality, completeness |

## Evaluation-Driven Development (EDD) Workflow

### Step 1: Define Success Criteria

Before implementing the skill, define what success looks like:

```markdown
## Success Criteria

- Skill triggers on correct prompts (explicit and implicit)
- Skill does NOT trigger on unrelated prompts
- Expected artifacts are created
- Token usage stays under 5000 tokens
- Commands executed < 10 (no thrashing)
```

### Step 2: Create Prompt Set

Create `evals/prompt-sets/<skill-name>.csv`:

```csv
id,should_trigger,prompt,expected_outcome,category
explicit-01,true,"Send an email to test@example.com",email_sent,explicit
implicit-01,true,"Draft a reply to the latest message",draft_created,implicit
contextual-01,true,"Send a quick thanks to the team",email_sent,contextual
negative-01,false,"Write a Python script",no_trigger,negative
negative-02,false,"Create a presentation",no_trigger,negative
```

**Prompt Categories:**

| Category | Description | Count |
|----------|-------------|-------|
| **explicit** | Names skill directly | 2-3 |
| **implicit** | Describes task without naming skill | 3-4 |
| **contextual** | Adds domain context | 2-3 |
| **negative** | Should NOT trigger | 2-3 |

**Total**: 10-15 prompts for early value

### Step 3: Implement Check Functions

Create `evals/checks/<skill-name>_checks.py`:

```python
#!/usr/bin/env python3
"""Evaluation checks for <skill-name>."""

def check_expected_outcome(trace: dict, outcome: str) -> tuple[bool, str]:
    """Check if expected outcome was achieved."""
    events = trace.get('events', [])
    
    # Map outcomes to event types
    outcome_events = {
        'email_sent': 'email.sent',
        'draft_created': 'file.created',
        'search_completed': 'email.search',
    }
    
    expected_event = outcome_events.get(outcome)
    if not expected_event:
        return False, f"Unknown outcome: {outcome}"
    
    event_types = [e.get('type') for e in events]
    passed = expected_event in event_types
    
    return passed, f"Found event: {expected_event}" if passed else f"Missing event: {expected_event}"


# Register checks
CHECKS = {
    'email_sent': lambda trace: check_expected_outcome(trace, 'email_sent'),
    'draft_created': lambda trace: check_expected_outcome(trace, 'draft_created'),
    'search_completed': lambda trace: check_expected_outcome(trace, 'search_completed'),
}
```

### Step 4: Run Evals During Development

```bash
# Run full eval suite
python evals/runner.py --skill my-skill --prompt-set evals/prompt-sets/my-skill.csv

# View report
cat evals/reports/my-skill-report-*.md
```

### Step 5: Fix Failures → Add Tests

When you fix a bug manually:

1. **Identify the failure scenario**
2. **Add a prompt to the prompt set** that reproduces it
3. **Run evals** to verify the fix
4. **Commit** both the fix and the new test

This ensures regressions are caught early.

---

## Integration with Skill-Creator

### Using skill-creator to Create Evals

When creating a skill with `skill-creator` or `skill-creator-pro`:

```markdown
User: "Create a skill for processing emails"

skill-creator should:
1. Ask: "What are the key scenarios this skill should handle?"
2. Ask: "Are there any edge cases or common failures?"
3. Suggest: "Let's create eval prompts for each scenario"
4. Generate: evals/prompt-sets/process-email.csv
5. Generate: evals/checks/process_email_checks.py
```

### Recommended Skill-Creator Prompt

```markdown
Create a new skill for <domain> with:

1. SKILL.md with workflows
2. References for domain knowledge
3. Scripts for deterministic operations
4. **EVALS**:
   - evals/prompt-sets/<skill>.csv with 10-15 test prompts
   - evals/checks/<skill>_checks.py with outcome checks
   - evals/schemas/<skill>-outcome.schema.json for rubric grading
```

---

## Prompt Set Templates

### Template 1: Action Skill (MCP Handler)

```csv
id,should_trigger,prompt,expected_outcome,category
explicit-send-01,true,"Send an email to <recipient> with subject <subject>",email_sent,explicit
explicit-draft-01,true,"Draft an email response",draft_created,explicit
implicit-send-01,true,"Let <email> know about the meeting",email_sent,implicit
implicit-draft-01,true,"Prepare a reply but don't send yet",draft_created,implicit
contextual-01,true,"Send a quick thanks for the update",email_sent,contextual
contextual-02,true,"Forward this to the team with your thoughts",email_sent,contextual
negative-01,false,"Write a document",no_trigger,negative
negative-02,false,"Create a spreadsheet",no_trigger,negative
search-01,true,"Find emails about <topic> from last week",search_completed,explicit
```

### Template 2: Reasoning Skill (Analysis)

```csv
id,should_trigger,prompt,expected_outcome,category
explicit-01,true,"Analyze this email and determine priority",priority_assigned,explicit
implicit-01,true,"What should I focus on first?",priority_assigned,implicit
categorization-01,true,"Is this about billing or support?",category_assigned,explicit
negative-01,false,"Write code for me",no_trigger,negative
negative-02,false,"Design a logo",no_trigger,negative
```

### Template 3: Orchestration Skill

```csv
id,should_trigger,prompt,expected_outcome,category
explicit-01,true,"Process all items in Needs_Action",workflow_completed,explicit
implicit-01,true,"What needs my attention?",status_report,implicit
negative-01,false,"Send an email",no_trigger,negative
```

---

## Check Function Templates

### Template 1: File Creation Check

```python
def check_file_created(trace: dict, expected_path: str) -> tuple[bool, str]:
    """Check if expected file was created."""
    from pathlib import Path
    
    # Check trace for file creation event
    events = trace.get('events', [])
    for event in events:
        if event.get('type') == 'file.created':
            if expected_path in event.get('path', ''):
                return True, f"File created: {event.get('path')}"
    
    # Check filesystem
    if Path(expected_path).exists():
        return True, f"File exists: {expected_path}"
    
    return False, f"File not created: {expected_path}"
```

### Template 2: Command Execution Check

```python
def check_command_executed(trace: dict, expected_command: str) -> tuple[bool, str]:
    """Check if expected command was executed."""
    events = trace.get('events', [])
    
    for event in events:
        if event.get('type') == 'command_execution':
            command = event.get('command', '')
            if expected_command.lower() in command.lower():
                return True, f"Command executed: {command}"
    
    return False, f"Command not found: {expected_command}"
```

### Template 3: Content Check

```python
def check_content_contains(file_path: str, expected_text: str) -> tuple[bool, str]:
    """Check if file contains expected content."""
    from pathlib import Path
    
    if not Path(file_path).exists():
        return False, f"File not found: {file_path}"
    
    content = Path(file_path).read_text()
    if expected_text in content:
        return True, f"Content found: '{expected_text[:50]}...'"
    
    return False, f"Content not found: '{expected_text}'"
```

---

## Rubric Schema Templates

### Outcome Rubric

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Outcome Evaluation",
  "type": "object",
  "properties": {
    "outcome_achieved": { "type": "boolean" },
    "outcome_type": { "type": "string", "enum": ["email_sent", "draft_created", "other"] },
    "score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "pass": { "type": "boolean" },
          "evidence": { "type": "string" },
          "notes": { "type": "string" }
        },
        "required": ["id", "pass", "evidence", "notes"]
      }
    }
  },
  "required": ["outcome_achieved", "outcome_type", "score", "checks"]
}
```

### Style Rubric

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Style Evaluation",
  "type": "object",
  "properties": {
    "overall_pass": { "type": "boolean" },
    "score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "pass": { "type": "boolean" },
          "notes": { "type": "string" }
        },
        "required": ["id", "pass", "notes"]
      }
    }
  },
  "required": ["overall_pass", "score", "checks"]
}
```

---

## Report Interpretation

### Understanding Metrics

| Metric | What It Means | Good Threshold |
|--------|---------------|----------------|
| **Pass Rate** | % of prompts that passed all checks | > 90% |
| **Average Score** | Mean of all check scores | > 80/100 |
| **Token Efficiency** | % under token limit | > 90% |
| **Command Efficiency** | % under command limit | > 90% |

### Common Failure Patterns

| Pattern | Likely Cause | Fix |
|---------|--------------|-----|
| All negative tests fail | Skill triggers too easily | Tighten trigger conditions |
| Explicit pass, implicit fail | Skill needs better examples | Add implicit prompts to SKILL.md |
| Low token efficiency | Too much context loading | Use progressive disclosure |
| Low command efficiency | Thrashing, retry loops | Improve error handling |

---

## Best Practices

### 1. Start with 10 Prompts

```csv
# Minimum viable prompt set:
3 explicit (names skill)
3 implicit (describes task)
2 contextual (adds domain)
2 negative (should not trigger)
```

### 2. Make Checks Explainable

```python
# Bad: Boolean only
return passed

# Good: With evidence
return passed, f"Found {count} events matching {criteria}"
```

### 3. Run Evals Early and Often

```bash
# Before committing skill changes
python evals/runner.py --skill my-skill --prompt-set evals/prompt-sets/my-skill.csv
```

### 4. Grow Prompt Set Organically

- Add prompts for real user requests
- Add prompts for bugs you fix
- Add prompts for edge cases you discover

### 5. Keep Checks Maintainable

- One check per function
- Descriptive function names
- Clear evidence messages
- Minimal dependencies

---

## Advanced: Custom Check Types

### Build Verification

```python
def check_build_succeeds(artifact_dir: Path) -> tuple[bool, str]:
    """Run build command and verify success."""
    import subprocess
    
    result = subprocess.run(
        ['npm', 'run', 'build'],
        cwd=artifact_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        return True, "Build completed successfully"
    else:
        return False, f"Build failed: {result.stderr}"
```

### Runtime Smoke Test

```python
def check_server_responsive(host: str, port: int) -> tuple[bool, str]:
    """Check if server responds to health check."""
    import requests
    
    try:
        response = requests.get(f"http://{host}:{port}/health")
        if response.status_code == 200:
            return True, f"Server responsive: {response.status_code}"
        return False, f"Unexpected status: {response.status_code}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"
```

---

## Troubleshooting

### Problem: All Tests Fail

**Check:**
1. Is skill name correct in runner command?
2. Does prompt set CSV have correct headers?
3. Are check functions registered in CHECKS dict?

### Problem: False Positives on Negative Tests

**Solution:**
- Skill triggers too easily
- Add more negative tests
- Tighten skill description/triggers

### Problem: Evidence Messages Unclear

**Solution:**
- Add more context to evidence strings
- Include actual vs expected values
- Add trace snippets

---

## References

- `../README.md` - Eval framework overview
- `../EVAL_COMPARISON.md` - Comparison with OpenAI
- `../scripts/validate_skills.py` - Static validation
- `../../.claude/skills/skill-creator/SKILL.md` - Skill creation
