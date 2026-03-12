# Skill Evals: Internal Mechanisms

Deep dive into how the Personal AI Employee skill evaluation system works.

## Overview

The eval system provides automated testing of AI skills to verify:
- Correct trigger behavior (skill invokes when it should)
- Correct outcome achievement (skill does what it's supposed to)
- Efficiency (reasonable token/command usage)
- No false positives (skill doesn't trigger when it shouldn't)

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Evaluation Runner                           │
│                      (runner.py)                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Prompt Sets │  │   Executor   │  │   Check Functions     │  │
│  │   (CSV)     │→ │  (Simulated/ │→ │  (email_checks.py)    │  │
│  │             │  │   Real)      │  │                       │  │
│  └─────────────┘  └──────────────┘  └───────────────────────┘  │
│         ↓                ↓                      ↓               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Trace Objects (JSON)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│         ↓                                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Report Generator (Markdown)                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Evaluation Runner (`evals/runner.py`)

**Purpose**: Orchestrates the entire evaluation process.

**Key Classes**:
```python
class SkillEvaluator:
    """Main evaluator class."""
    
    def __init__(self, skill_name: str, vault_path: Path = None)
    def load_prompt_set(self, csv_path: str) -> list[dict]
    def execute_prompt(self, prompt: dict) -> dict
    def run_checks(self, execution_result: dict) -> dict
    def run_evaluation(self, prompt_set_path: str) -> dict
    def generate_report(self) -> Path
```

**Execution Flow**:
```python
# 1. Load prompts from CSV
prompts = self.load_prompt_set(csv_path)

# 2. For each prompt:
for prompt in prompts:
    # a. Execute prompt (simulate or real)
    execution = self.execute_prompt(prompt)
    
    # b. Run checks on execution trace
    check_result = self.run_checks(execution)
    
    # c. Collect results
    results.append(check_result)

# 3. Generate markdown report
report_path = self.generate_report()
```

### 2. Prompt Sets (`evals/prompt-sets/*.csv`)

**Format**:
```csv
id,should_trigger,prompt,expected_outcome,category
test-01,true,"Send an email to test@example.com",email_sent,explicit
test-02,false,"Write a Python script",no_trigger,negative
```

**Columns**:
| Column | Type | Purpose |
|--------|------|---------|
| `id` | string | Unique test identifier |
| `should_trigger` | boolean | Whether skill should activate |
| `prompt` | string | Test input to Claude Code |
| `expected_outcome` | string | Expected result type |
| `category` | string | Grouping for reports |

**Prompt Categories**:
- **explicit**: Names skill directly ("Use the mcp-email skill to...")
- **implicit**: Describes task without naming skill ("Send an email to...")
- **contextual**: Adds domain context ("Send a quick thanks to the team")
- **negative**: Should NOT trigger ("Write a Python script")

### 3. Check Functions (`evals/checks/*.py`)

**Purpose**: Deterministic validation of execution traces.

**Structure**:
```python
def check_email_sent(trace: dict) -> tuple[bool, str]:
    """
    Check if email was sent by examining trace events.
    
    Args:
        trace: Execution trace dictionary
        
    Returns:
        tuple: (passed: bool, evidence: str)
    """
    events = trace.get('events', [])
    
    for event in events:
        if event.get('type') == 'email.sent':
            return True, f"Email sent event found"
    
    return False, "No email sent event found"
```

**Check Registry**:
```python
CHECKS = {
    'email_sent': check_email_sent,
    'draft_created': check_draft_created,
    'search_completed': check_search_completed,
    'no_trigger': check_no_trigger,
}
```

**Built-in Checks**:
| Check | Purpose |
|-------|---------|
| `check_email_sent` | Verify email was sent |
| `check_draft_created` | Verify draft file created |
| `check_search_completed` | Verify email search completed |
| `check_no_trigger` | Verify skill correctly did NOT trigger |
| `check_skill_invoked` | Verify skill invocation status |
| `check_token_efficiency` | Verify token usage under limit |
| `check_command_count` | Verify command count under limit |

### 4. Trace Objects

**Format**:
```json
{
  "prompt": "Send an email to test@example.com",
  "skill": "mcp-email",
  "timestamp": "2026-03-09T10:19:19",
  "events": [
    {"type": "skill.invoked", "skill": "mcp-email"},
    {"type": "context.gathered", "details": {"source": "vault"}},
    {"type": "command_execution", "command": "mcp-email send --to test@example.com"},
    {"type": "email.sent", "details": {"to": "test@example.com", "subject": "Test"}}
  ],
  "usage": {
    "input_tokens": 1500,
    "output_tokens": 800,
    "total_tokens": 2300
  }
}
```

**Event Types**:
| Event Type | Description |
|------------|-------------|
| `skill.invoked` | Skill was triggered |
| `skill.completed` | Skill finished execution |
| `context.gathered` | Context loaded from vault/codebase |
| `command_execution` | MCP command or bash command run |
| `file.created` | File created in vault |
| `email.sent` | Email sent via MCP |
| `email.search` | Email search performed |

### 5. Report Generation

**Output**: Markdown file with:
- Summary statistics
- Results by category
- Detailed check results
- Evidence for each check

**Example**:
```markdown
# Evaluation Report: mcp-email

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | 10 |
| Passed | 9 |
| Failed | 1 |
| Pass Rate | 90.0% |

## Results by Category

### Explicit
| ID | Status | Score |
|----|--------|-------|
| test-01 | ✅ Pass | 100 |

## Detailed Results

### test-01: ✅ PASS

**Prompt:** Send an email to test@example.com

**Checks:**
- ✅ **skill_invocation**: Skill correctly invoked
- ✅ **outcome_achieved**: Expected outcome achieved
- ✅ **token_efficiency**: Under 5000 tokens
- ✅ **command_efficiency**: Under 10 commands
```

---

## Execution Modes

### Current Mode: Simulated

```python
def _simulate_execution(self, prompt: dict) -> list[dict]:
    """Simulate execution events for demonstration."""
    outcome = prompt['expected_outcome']
    
    if outcome == 'email_sent':
        return [
            {'type': 'skill.invoked', 'skill': self.skill_name},
            {'type': 'command_execution', 'command': 'mcp-email send'},
            {'type': 'email.sent', 'details': {'to': 'test@example.com'}}
        ]
```

**Limitations**:
- Does not actually run Claude Code
- Pre-defined event sequences
- No real file system changes
- No real token tracking

### Future Mode: Real Execution

```python
def execute_prompt(self, prompt: dict) -> dict:
    """Execute prompt with real Claude Code."""
    import subprocess
    
    # Run Claude Code with JSON output
    cmd = [
        'claude-code',
        '--skill', self.skill_name,
        '--json',
        prompt['prompt']
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    
    # Parse JSONL output
    trace = self._parse_jsonl(result.stdout)
    
    return {
        'prompt': prompt,
        'trace': trace,
        'artifact_path': self._save_trace(trace)
    }
```

**Requirements**:
- Claude Code CLI installed
- `--json` flag support
- JSONL parsing
- Real token tracking

---

## Check Execution Engine

### How Checks Run

```python
def run_checks(self, execution_result: dict) -> dict:
    """Run all applicable checks."""
    prompt = execution_result['prompt']
    trace = execution_result['trace']
    
    checks = []
    
    # 1. Check skill invocation
    invoked_check = self._check_invocation(trace, prompt['should_trigger'])
    checks.append(invoked_check)
    
    # 2. Check outcome (if should trigger)
    if prompt['should_trigger']:
        outcome_check = self._check_outcome(trace, prompt['expected_outcome'])
        checks.append(outcome_check)
    
    # 3. Check efficiency
    token_check = self._check_token_efficiency(trace)
    checks.append(token_check)
    
    command_check = self._check_command_count(trace)
    checks.append(command_check)
    
    # Calculate overall result
    all_passed = all(c['pass'] for c in checks)
    score = sum(c['pass'] for c in checks) / len(checks) * 100
    
    return {
        'prompt_id': prompt['id'],
        'checks': checks,
        'overall_pass': all_passed,
        'score': score
    }
```

### Check Result Format

```python
{
    'id': 'skill_invocation',
    'pass': True,
    'evidence': 'Skill invoked',
    'notes': 'Expected: invoke, Got: invoke'
}
```

---

## Data Flow

```
1. CSV Prompt Set
   ↓
2. Load into Python dicts
   ↓
3. For each prompt:
   a. Execute (simulate/real)
   b. Capture trace (JSON)
   c. Run checks
   d. Collect results
   ↓
4. Aggregate results
   ↓
5. Generate Markdown report
   ↓
6. Save to evals/reports/
```

---

## File Organization

```
evals/
├── README.md                    # Framework overview
├── EVAL_COMPARISON.md           # Comparison with OpenAI
├── SKILL_EVAL_GUIDE.md          # User guide
├── INTERNAL_MECHANISMS.md       # This file
├── runner.py                    # Main evaluator
├── prompt-sets/                 # CSV prompt sets
│   ├── mcp-email.csv
│   └── <skill-name>.csv
├── checks/                      # Check functions
│   ├── email_checks.py
│   ├── common_checks.py
│   └── <skill-name>_checks.py
├── schemas/                     # JSON schemas for rubrics
│   ├── style-rubric.schema.json
│   └── outcome-rubric.schema.json
├── artifacts/                   # Captured traces
│   ├── test-01.trace.json
│   └── <test-id>.trace.json
└── reports/                     # Generated reports
    ├── mcp-email-report-*.md
    └── <skill>-report-*.md
```

---

## Extending the System

### Adding New Check Types

**Step 1**: Create check function
```python
def check_build_succeeds(trace: dict, artifact_dir: Path) -> tuple[bool, str]:
    """Run build and verify success."""
    import subprocess
    
    result = subprocess.run(
        ['npm', 'run', 'build'],
        cwd=artifact_dir,
        capture_output=True
    )
    
    if result.returncode == 0:
        return True, "Build succeeded"
    else:
        return False, f"Build failed: {result.stderr}"
```

**Step 2**: Add to CHECKS registry
```python
CHECKS = {
    'email_sent': check_email_sent,
    'build_succeeds': check_build_succeeds,  # New
}
```

**Step 3**: Use in prompt set
```csv
id,should_trigger,prompt,expected_outcome
build-01,true,"Create a React app",build_succeeds
```

### Adding New Event Types

**Step 1**: Define event in skill execution
```python
# In skill implementation
trace['events'].append({
    'type': 'custom.event',
    'details': {'key': 'value'}
})
```

**Step 2**: Create check for event
```python
def check_custom_event(trace: dict) -> tuple[bool, str]:
    events = trace.get('events', [])
    for event in events:
        if event.get('type') == 'custom.event':
            return True, f"Custom event found"
    return False, "Custom event not found"
```

---

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Load prompt set | O(n) | n = number of prompts |
| Execute prompt | O(1) | Simulated, varies for real |
| Run checks | O(m) | m = number of checks |
| Generate report | O(n) | n = number of results |

### Memory Usage

| Component | Memory | Notes |
|-----------|--------|-------|
| Prompt set | ~1KB per 10 prompts | CSV format |
| Trace objects | ~5KB per execution | JSON format |
| Check results | ~500 bytes per check | Python dicts |
| Reports | ~10KB per skill | Markdown format |

---

## Security Considerations

### Current State (Simulated)

- No external API calls
- No file system modifications
- No credential access
- Safe for local testing

### Future State (Real Execution)

- **Sandboxing**: Run in isolated environment
- **Permissions**: Least-privilege file access
- **Rate limiting**: Prevent API abuse
- **Audit logging**: Track all actions
- **Secret management**: No credentials in traces

---

## Troubleshooting

### Problem: All Tests Show Same Result

**Cause**: Simulated execution uses same logic for all prompts.

**Solution**: Implement real execution or customize simulation per prompt type.

### Problem: Check Functions Not Found

**Cause**: Check file not in `evals/checks/` or not registered.

**Solution**:
1. Verify file exists: `ls evals/checks/<skill>_checks.py`
2. Verify CHECKS dict populated
3. Import check module in runner.py

### Problem: Report Not Generated

**Cause**: Error in report generation or directory missing.

**Solution**:
1. Verify `evals/reports/` directory exists
2. Check for exceptions in generate_report()
3. Verify write permissions

---

## Future Enhancements

### Planned Features

1. **Real Execution Mode**
   - Integrate with Claude Code CLI
   - Parse JSONL output
   - Track real token usage

2. **Build Verification**
   - Run build commands post-execution
   - Verify compilation success

3. **Runtime Testing**
   - Start dev servers
   - Run smoke tests with curl/Playwright

4. **File Change Detection**
   - Snapshot filesystem before
   - Compare after execution
   - Verify expected artifacts

5. **Rubric Grading**
   - LLM-assisted style evaluation
   - JSON schema-constrained output
   - Quality scoring

6. **CI/CD Integration**
   - Run evals on skill commit
   - Block merges on failing evals
   - Trend reports over time

---

## References

- `../README.md` - Framework overview
- `../EVAL_COMPARISON.md` - OpenAI comparison
- `../SKILL_EVAL_GUIDE.md` - User guide
- `../runner.py` - Implementation code
- `../../.claude/skills/skill-creator/SKILL.md` - Skill creation
