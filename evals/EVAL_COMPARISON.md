# Skill Evaluation Systems: Comparative Analysis

A comprehensive comparison between the Personal AI Employee eval framework and OpenAI's Eval Skills system.

**Document Purpose**: Understand design decisions, identify gaps, and establish best practices for skill evaluation.

---

## Executive Summary

| Aspect | OpenAI Approach | Personal AI Employee Approach |
|--------|-----------------|-------------------------------|
| **Primary Focus** | Agent skill testing with Codex | AI skill testing with Claude Code |
| **Execution Model** | `codex exec --json` | `python evals/runner.py` |
| **Trace Format** | JSONL event stream | JSON trace objects |
| **Prompt Sets** | CSV with `should_trigger` | CSV with `should_trigger` + `expected_outcome` |
| **Grading** | Deterministic + Rubric-based | Deterministic + Rubric-based |
| **Integration** | Built into Codex workflow | Standalone Python framework |

---

## 1. Architecture Comparison

### OpenAI's Architecture

```
Prompt (CSV) → codex exec --json → JSONL Trace → Checks → Score → Report
                    ↓
              Full-auto mode
              (file changes allowed)
```

**Key Components:**
- **Codex CLI**: Native command-line tool with `--json` flag for structured output
- **JSONL Stream**: Real-time event streaming (`item.started`, `item.completed`, `turn.completed`)
- **Output Schema**: JSON Schema constraints via `--output-schema` for rubric grading
- **Artifacts**: Automatic capture of file changes and command outputs

### Personal AI Employee Architecture

```
Prompt (CSV) → runner.py → Simulated/Real Execution → Checks → Score → Report
                          ↓
                    Claude Code invocation
                    (via subprocess/API)
```

**Key Components:**
- **Python Runner**: Custom evaluation orchestrator
- **JSON Traces**: Complete trace objects saved per prompt
- **Check Functions**: Python functions for deterministic validation
- **Schema Files**: JSON Schema for rubric-based grading

**Design Decision**: Our approach is more portable (no CLI dependency) but requires more implementation work for real execution.

---

## 2. Prompt Set Design

### OpenAI Format

```csv
id,should_trigger,prompt
test-01,true,"Create a demo app named `devday-demo` using the $setup-demo-app skill"
test-02,true,"Set up a minimal React demo app with Tailwind for quick UI experiments"
test-03,true,"Create a small demo app to showcase the Responses API"
test-04,false,"Add Tailwind styling to my existing React app"
```

**Characteristics:**
- Minimal columns (id, should_trigger, prompt)
- Focus on trigger detection
- Negative controls for false positive detection

### Personal AI Employee Format

```csv
id,should_trigger,prompt,expected_outcome,category
test-01,true,"Send an email to test@example.com with subject 'Test'",email_sent,explicit
test-02,true,"Draft a reply to the latest email",draft_created,implicit
test-05,false,"Write a Python script to process data",no_trigger,negative
```

**Characteristics:**
- Extended columns for outcome tracking
- Category column for report grouping
- Explicit outcome expectations

**Comparison:**
| Feature | OpenAI | Personal AI |
|---------|--------|-------------|
| Simplicity | ✅ Minimal | ⚠️ More complex |
| Outcome tracking | ❌ Manual | ✅ Built-in |
| Categorization | ❌ Manual | ✅ Automatic |
| Negative controls | ✅ Yes | ✅ Yes |

**Recommendation**: Both approaches are valid. OpenAI's is simpler for trigger-focused evals. Ours is better for outcome-focused evals.

---

## 3. Execution Models

### OpenAI: `codex exec`

```bash
codex exec --json --full-auto "<prompt>"
```

**Features:**
- `--json`: Emits JSONL to stdout (REQUIRED for evals)
- `--full-auto`: Allows file system changes without confirmation
- `--output-schema`: Constrains final response to JSON Schema
- **Real execution**: Actually performs the requested tasks

**JSONL Event Types:**
```json
{"type": "item.started", "item": {"type": "command_execution", "command": "npm install"}}
{"type": "item.completed", "item": {"type": "command_execution"}}
{"type": "turn.completed", "usage": {"input_tokens": 1500, "output_tokens": 800}}
```

### Personal AI Employee: `runner.py`

```bash
python evals/runner.py --skill mcp-email --prompt-set evals/prompt-sets/mcp-email.csv
```

**Features:**
- Custom Python orchestration
- Simulated execution (current state)
- Artifact capture to `evals/artifacts/`
- **Extensible**: Can integrate with real Claude Code execution

**Trace Format:**
```json
{
  "prompt": "Send an email...",
  "skill": "mcp-email",
  "timestamp": "2026-03-09T10:19:19",
  "events": [
    {"type": "skill.invoked", "skill": "mcp-email"},
    {"type": "command_execution", "command": "mcp-email send --to test@example.com"},
    {"type": "email.sent", "details": {"to": "test@example.com"}}
  ],
  "usage": {"input_tokens": 1500, "output_tokens": 800, "total_tokens": 2300}
}
```

**Gap Analysis:**
| Capability | OpenAI | Personal AI | Priority |
|------------|--------|-------------|----------|
| Real execution | ✅ Native | ⚠️ Simulated | 🔴 HIGH |
| JSONL streaming | ✅ Built-in | ❌ Not implemented | 🟡 MEDIUM |
| Token tracking | ✅ Automatic | ⚠️ Manual | 🟡 MEDIUM |
| File change capture | ✅ Automatic | ⚠️ Manual | 🟡 MEDIUM |

**Next Step**: Integrate with actual Claude Code execution for real evals.

---

## 4. Grading Approaches

### 4.1 Deterministic Checks

#### OpenAI Implementation

```javascript
// Check: Did the agent run npm install?
function checkRanNpmInstall(events) {
  return events.some(
    (e) =>
      (e.type === "item.started" || e.type === "item.completed") &&
      e.item?.type === "command_execution" &&
      e.item.command.includes("npm install")
  );
}
```

**Characteristics:**
- JavaScript functions
- Operate on JSONL events
- Simple boolean return
- Focus on command execution

#### Personal AI Employee Implementation

```python
def check_email_sent(trace: dict) -> tuple[bool, str]:
    events = trace.get('events', [])
    for event in events:
        if event.get('type') == 'email.sent':
            return True, f"Email sent event found: {json.dumps(event.get('details', {}))}"
    return False, "No email sent event found in trace"
```

**Characteristics:**
- Python functions
- Operate on JSON trace objects
- Return tuple: (passed, evidence)
- Focus on domain-specific outcomes

**Comparison:**
| Aspect | OpenAI | Personal AI |
|--------|--------|-------------|
| Language | JavaScript | Python |
| Input format | JSONL events | JSON trace |
| Return value | Boolean | (Boolean, Evidence) |
| Evidence tracking | Manual | Built-in |
| Domain specificity | Generic | Skill-specific |

**Advantage**: Personal AI approach provides better explainability with built-in evidence.

---

### 4.2 Rubric-Based Grading

#### OpenAI Implementation

**Schema** (`evals/style-rubric.schema.json`):
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

**Execution**:
```bash
codex exec \
  "Evaluate the demo-app repository against these requirements..." \
  --output-schema ./evals/style-rubric.schema.json \
  -o ./evals/artifacts/test-01.style.json
```

#### Personal AI Employee Implementation

**Schema** (`evals/schemas/style-rubric.schema.json`):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Style Rubric Evaluation",
  "type": "object",
  "properties": {
    "overall_pass": { "type": "boolean" },
    "score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "checks": { ... }
  }
}
```

**Execution** (Planned):
```bash
claude-code --skill skill-creator \
  "Evaluate this email output against style guidelines" \
  --output-schema evals/schemas/style-rubric.schema.json
```

**Comparison**: Nearly identical approach. Both use JSON Schema for structured grading.

---

## 5. Evaluation Categories

### OpenAI Categories

| Category | Description | Example Check |
|----------|-------------|---------------|
| **Outcome goals** | Did the task complete? | Does the app run? |
| **Process goals** | Did agent follow steps? | Did it run `npm install`? |
| **Style goals** | Does output follow conventions? | TypeScript components? |
| **Efficiency goals** | Did it avoid thrashing? | Token count, command count |

### Personal AI Employee Categories

| Category | Description | Example Check |
|----------|-------------|---------------|
| **Skill invocation** | Did skill trigger correctly? | Should trigger vs shouldn't |
| **Outcome achievement** | Did it achieve expected result? | Email sent, draft created |
| **Token efficiency** | Was token usage reasonable? | Under 5000 tokens |
| **Command efficiency** | Did it avoid thrashing? | Under 10 commands |

**Mapping**:
| OpenAI | Personal AI | Notes |
|--------|-------------|-------|
| Outcome goals | Outcome achievement | Direct mapping |
| Process goals | Command efficiency | Similar intent |
| Style goals | (Future) | Need rubric implementation |
| Efficiency goals | Token + Command efficiency | Split into two |

**Gap**: Style goals need implementation via rubric grading.

---

## 6. Extended Checks Comparison

| Check Type | OpenAI | Personal AI | Implementation Status |
|------------|--------|-------------|----------------------|
| **Command execution** | ✅ Parse JSONL | ✅ Parse trace | ✅ Implemented |
| **File existence** | ✅ `existsSync()` | ✅ `Path.exists()` | ✅ Implemented |
| **Build verification** | ✅ Run `npm run build` | ❌ Not implemented | 🔴 TODO |
| **Runtime smoke test** | ✅ `curl` / Playwright | ❌ Not implemented | 🔴 TODO |
| **Token budget** | ✅ Track `usage.*` | ✅ Track `usage.*` | ✅ Implemented |
| **Command count** | ✅ Count events | ✅ Count events | ✅ Implemented |
| **Repo cleanliness** | ✅ `git status` | ❌ Not implemented | 🟡 Optional |
| **Sandbox regression** | ✅ Permission check | ❌ Not implemented | 🟡 Optional |

---

## 7. Best Practices Alignment

### OpenAI Best Practices

1. ✅ Start small (10-20 prompts)
2. ✅ Ground evals in behavior (JSONL traces)
3. ✅ Make failures explainable
4. ✅ Let real failures drive coverage
5. ✅ Use least permissions
6. ✅ Track over time (stable schema)

### Personal AI Employee Best Practices

1. ✅ Start small (10 prompts in demo)
2. ✅ Ground evals in behavior (trace objects)
3. ✅ Make failures explainable (evidence field)
4. ⚠️ Let real failures drive coverage (TODO)
5. ⚠️ Use least permissions (TODO)
6. ✅ Track over time (timestamped reports)

**Alignment**: 4/6 fully implemented, 2/6 in progress.

---

## 8. Key Differences Summary

| Aspect | OpenAI Advantage | Personal AI Advantage |
|--------|------------------|----------------------|
| **Execution** | Native CLI integration | Portable, no dependencies |
| **Trace Format** | Real-time JSONL streaming | Complete JSON snapshots |
| **Evidence** | Manual tracking | Built-in evidence in checks |
| **Outcome Tracking** | Manual | Built-in `expected_outcome` |
| **Categorization** | Manual | Built-in categories |
| **Rubric Grading** | Native `--output-schema` | Schema files (manual invocation) |
| **Integration** | Tight Codex integration | Flexible, extensible |

---

## 9. Recommendations for Personal AI Employee

### Immediate Priorities (HIGH)

1. **Real Execution Integration**
   ```bash
   # Replace simulation with actual Claude Code execution
   claude-code --skill <skill> --json "<prompt>"
   ```

2. **JSONL Streaming Support**
   - Parse real-time events during execution
   - Enable streaming to trace files

3. **Build/Runtime Checks**
   - Add post-execution validation
   - Run build commands, smoke tests

### Medium Priorities (MEDIUM)

4. **Enhanced Rubric Grading**
   - Integrate with Claude Code for schema-constrained evaluation
   - Create more rubric templates

5. **File Change Capture**
   - Track files created/modified during execution
   - Compare against expected artifacts

### Lower Priorities (LOW)

6. **Git Integration**
   - Verify repo cleanliness
   - Track git status changes

7. **Sandbox Testing**
   - Permission verification
   - Security regression detection

---

## 10. Unique Personal AI Employee Features

These features go beyond OpenAI's approach:

### 10.1 Category-Based Reporting

```csv
id,should_trigger,prompt,expected_outcome,category
test-01,true,"Send email...",email_sent,explicit
test-07,true,"Send quick email...",email_sent,contextual
```

**Benefit**: Reports grouped by prompt type (explicit, implicit, contextual, negative).

### 10.2 Evidence-First Check Design

```python
return {
    'pass': passed,
    'evidence': f"Email sent event found: {details}",
    'notes': f"Check '{check_name}' executed successfully"
}
```

**Benefit**: Every check result includes explainable evidence.

### 10.3 Modular Check Registry

```python
CHECKS = {
    'email_sent': check_email_sent,
    'draft_created': check_draft_created,
    ...
}
```

**Benefit**: Easy to add new checks per skill type.

---

## 11. Implementation Roadmap

### Phase 1: Foundation (COMPLETE ✅)

- [x] Directory structure
- [x] Prompt set format (CSV)
- [x] Check functions (Python)
- [x] Rubric schemas (JSON)
- [x] Runner script
- [x] Report generation

### Phase 2: Real Execution (TODO 🔴)

- [ ] Integrate with Claude Code CLI
- [ ] Capture real JSONL traces
- [ ] Handle file system changes
- [ ] Track token usage from real execution

### Phase 3: Advanced Features (TODO 🟡)

- [ ] Build verification
- [ ] Runtime smoke tests
- [ ] File change detection
- [ ] Enhanced rubric grading

### Phase 4: Integration (TODO 🟡)

- [ ] Integrate with skill-creator workflow
- [ ] Add eval templates to skill initialization
- [ ] Automated eval running on skill creation

---

## 12. Conclusion

### What We've Learned

1. **OpenAI's approach is mature** - Built for production agent testing with tight CLI integration
2. **Our approach is flexible** - More portable, easier to extend
3. **Core patterns align** - Both use prompt sets, deterministic checks, rubric grading
4. **Key gap is execution** - We simulate, OpenAI executes

### Strategic Advantages

| Personal AI Employee Strength | How to Leverage |
|-------------------------------|-----------------|
| Evidence-first design | Make explainability a core feature |
| Category-based reporting | Better insights into failure patterns |
| Modular check system | Easier to add domain-specific checks |
| Python implementation | Easier to integrate with existing tools |

### Next Steps

1. **Implement real execution** (highest priority)
2. **Add more check types** (build, runtime, file changes)
3. **Integrate with skill-creator** (SDD workflow)
4. **Document internal mechanisms** (Scenario 3)

---

## References

- [OpenAI Eval Skills Blog](https://developers.openai.com/blog/eval-skills/)
- `../evals/README.md` - Personal AI Employee eval framework
- `../.claude/skills/skill-creator/SKILL.md` - Skill creation guidance
- `../scripts/validate_skills.py` - Static skill validation
