# Skill Evaluation Framework

Evaluation system for testing AI skill behavior, inspired by OpenAI's eval framework.

## Overview

This framework provides systematic testing of skills to verify:
- **Skill invocation** - Does the skill trigger correctly?
- **Process goals** - Does it follow the right steps?
- **Outcome goals** - Does it produce correct results?
- **Style goals** - Does output follow conventions?
- **Efficiency goals** - Is it efficient with tokens/commands?

## Directory Structure

```
evals/
├── README.md                 # This file
├── prompt-sets/              # CSV files with test prompts
│   ├── mcp-email.csv
│   └── process-email.csv
├── checks/                   # Python check functions
│   ├── email_checks.py
│   └── common_checks.py
├── schemas/                  # JSON schemas for rubric grading
│   ├── style-rubric.schema.json
│   └── outcome-rubric.schema.json
├── artifacts/                # Captured traces and outputs
│   └── test-01.trace.json
├── reports/                  # Generated evaluation reports
│   └── mcp-email-report.md
└── runner.py                 # Main eval execution script
```

## Quick Start

### 1. Create a Prompt Set (CSV)

```csv
id,should_trigger,prompt,expected_outcome
test-01,true,"Send an email to test@example.com with subject 'Hello'",email_sent
test-02,true,"Draft a reply to the latest email",draft_created
test-03,false,"Write a Python script",no_trigger
```

### 2. Run Evaluations

```bash
python evals/runner.py --skill mcp-email --prompt-set evals/prompt-sets/mcp-email.csv
```

### 3. View Results

```bash
cat evals/reports/mcp-email-report.md
```

## Evaluation Types

### Deterministic Checks

Fast, explainable checks that parse execution traces:

```python
def check_email_sent(trace):
    """Verify email was sent by checking trace events."""
    return any(
        e.get('type') == 'email.sent'
        for e in trace.get('events', [])
    )
```

### Rubric-Based Grading

Qualitative evaluation using LLM with JSON schema:

```json
{
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
        }
      }
    }
  }
}
```

## Prompt Set Format

| Column | Description | Example |
|--------|-------------|---------|
| `id` | Unique test identifier | `test-01` |
| `should_trigger` | Whether skill should activate | `true` / `false` |
| `prompt` | Test prompt (quoted) | `"Send an email..."` |
| `expected_outcome` | Expected result type | `email_sent` |
| `context` (optional) | Additional context | `vault:Needs_Action` |

## Writing Good Evals

### 1. Start Small
- 10-20 prompts for early value
- Focus on critical paths first

### 2. Include Prompt Variations
- **Explicit invocation**: "Use the mcp-email skill to send..."
- **Implicit invocation**: "Send an email to..."
- **Negative controls**: Prompts that should NOT trigger

### 3. Make Failures Explainable
- Every check should identify WHY it failed
- Include trace snippets in reports

### 4. Test Real Workflows
- Use actual user prompts from history
- Test edge cases and variations

## Integration with Skill Creation

When creating a new skill with `skill-creator`:

1. **Define success criteria** during skill design
2. **Create prompt set** alongside SKILL.md
3. **Write checks** for deterministic validation
4. **Run evals** before packaging skill

## Best Practices

1. **Ground evals in behavior** - Use traces for deterministic checks
2. **Let failures drive coverage** - Turn manual fixes into tests
3. **Track over time** - Save reports for regression detection
4. **Use least permissions** - Especially when automating evals

## References

- [OpenAI Eval Skills Blog](https://developers.openai.com/blog/eval-skills/)
- `../.claude/skills/skill-creator/SKILL.md`
- `../scripts/validate_skills.py`
