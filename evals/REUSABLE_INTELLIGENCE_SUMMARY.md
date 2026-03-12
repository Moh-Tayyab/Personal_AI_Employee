# Reusable Intelligence: Skill Evaluation Framework

## Overview
This document summarizes the reusable intelligence established for the skill evaluation framework in the Personal AI Employee project. The framework combines both custom CSV-based evaluation and integration with the official Anthropic skill-creator system.

## Key Components

### 1. CSV-Based Evaluation System
- **Location**: `evals/`
- **Purpose**: Quick testing and development iteration
- **Format**: CSV prompt sets with Python check functions
- **Execution**: `python evals/runner.py --skill <skill-name> --prompt-set evals/prompt-sets/<skill>.csv`

#### Prompt Set Format
```csv
id,should_trigger,prompt,expected_outcome,category
test-01,true,"Send an email to test@example.com",email_sent,explicit
test-02,false,"Write a Python script",no_trigger,negative
```

### 2. Official Anthropic Evaluation System
- **Location**: `.claude/skills/skill-creator/`
- **Purpose**: Production benchmarking, A/B testing, qualitative review
- **Format**: JSON eval sets with subagent execution and web viewer
- **Execution**: Through Claude Code using skill-creator skill

#### Evaluation Categories
- **Explicit**: Names skill directly
- **Implicit**: Describes task without naming skill
- **Contextual**: Adds domain context
- **Negative**: Should NOT trigger

## Evaluation-Driven Development (EDD) Workflow

### Step 1: Define Success Criteria
- Skill triggers on correct prompts (explicit and implicit)
- Skill does NOT trigger on unrelated prompts
- Expected artifacts are created
- Token usage stays under limits
- Commands executed efficiently

### Step 2: Create Prompt Set
- 2-3 explicit prompts (names skill directly)
- 3-4 implicit prompts (describes task without naming skill)
- 2-3 contextual prompts (adds domain context)
- 2-3 negative prompts (should NOT trigger)
- Total: 10-15 prompts for early value

### Step 3: Implement Check Functions
- One check per function
- Descriptive function names
- Clear evidence messages
- Minimal dependencies

### Step 4: Run Evals During Development
```bash
python evals/runner.py --skill my-skill --prompt-set evals/prompt-sets/my-skill.csv
```

### Step 5: Fix Failures → Add Tests
- Identify the failure scenario
- Add a prompt to the prompt set that reproduces it
- Run evals to verify the fix
- Commit both the fix and the new test

## Best Practices

### For Development (Fast Iteration)
1. Use CSV-based evals for quick feedback
2. Start with 10 prompts minimum
3. Include prompt variations (explicit, implicit, negative)
4. Make failures explainable
5. Run evals early and often

### For Production (Benchmarking)
1. Use official skill-creator for comprehensive evals
2. Review results in web viewer
3. Combine qualitative + quantitative feedback
4. Document benchmark results

## Integration Points

### With Skill-Creator
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
4. EVALS:
   - evals/prompt-sets/<skill>.csv with 10-15 test prompts
   - evals/checks/<skill>_checks.py with outcome checks
   - evals/schemas/<skill>-outcome.schema.json for rubric grading
```

## Metrics and Thresholds

| Metric | Good Threshold |
|--------|----------------|
| Pass Rate | > 90% |
| Average Score | > 80/100 |
| Token Efficiency | > 90% |
| Command Efficiency | > 90% |

## Common Failure Patterns

| Pattern | Likely Cause | Fix |
|---------|--------------|-----|
| All negative tests fail | Skill triggers too easily | Tighten trigger conditions |
| Explicit pass, implicit fail | Skill needs better examples | Add implicit prompts to SKILL.md |
| Low token efficiency | Too much context loading | Use progressive disclosure |
| Low command efficiency | Thrashing, retry loops | Improve error handling |

## Reusable Templates

### Prompt Set Template: Action Skill
```csv
id,should_trigger,prompt,expected_outcome,category
explicit-send-01,true,"Send an email to <recipient> with subject <subject>",email_sent,explicit
explicit-draft-01,true,"Draft an email response",draft_created,explicit
implicit-send-01,true,"Let <email> know about the meeting",email_sent,implicit
implicit-draft-01,true,"Prepare a reply but don't send yet",draft_created,implicit
contextual-01,true,"Send a quick thanks for the update",email_sent,contextual
negative-01,false,"Write a document",no_trigger,negative
```

### Check Function Template: File Creation
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

## Key Insights

1. **Dual System Approach**: The framework provides both quick CSV-based evals for development and comprehensive official evals for production benchmarking.

2. **Evidence-First Design**: Every check includes explainable evidence, making failures easier to debug.

3. **Category-Based Reporting**: Results are grouped by prompt type (explicit, implicit, contextual, negative) for better insights.

4. **Modular Check Registry**: Easy to add new checks per skill type.

5. **Real vs. Simulated Execution**: Current system uses simulated execution for safety; real execution integration planned for future.

## Next Steps

1. Implement real execution mode with Claude Code CLI integration
2. Add build verification and runtime testing
3. Enhance rubric grading with LLM-assisted evaluation
4. Integrate with CI/CD for automated testing
5. Expand check libraries for more skill types

## References

- `evals/README.md` - Framework overview
- `evals/EVAL_COMPARISON.md` - OpenAI comparison
- `evals/SKILL_EVAL_GUIDE.md` - User guide
- `evals/INTERNAL_MECHANISMS.md` - Technical deep-dive
- `.claude/skills/skill-creator/SKILL.md` - Official skill documentation