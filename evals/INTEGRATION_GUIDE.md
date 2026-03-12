# Skill Evals: Integration Guide

This guide explains how to use evaluations with the **official Anthropic skill-creator** skill.

## Two Eval Systems Available

This project now has **two complementary eval systems**:

### 1. Simple CSV-Based Evals (Our Framework)
- **Location**: `evals/`
- **Best for**: Quick testing, development iteration
- **Format**: CSV prompt sets + Python check functions
- **Run**: `python3 evals/runner.py --skill mcp-email --prompt-set evals/prompt-sets/mcp-email.csv`

### 2. Official Anthropic Eval System (skill-creator)
- **Location**: `.claude/skills/skill-creator/`
- **Best for**: Production benchmarking, A/B testing, qualitative review
- **Format**: JSON eval sets + subagent execution + web viewer
- **Run**: Through Claude Code using skill-creator skill

---

## Quick Start: Using Official skill-creator Evals

### Step 1: Create Evals for Your Skill

**Option A: Use skill-creator within Claude Code** (Recommended)

```bash
# Start Claude Code
claude

# Then say:
"Use the skill-creator skill to create evals for my mcp-email skill"
```

The skill-creator will:
1. Interview you about success criteria
2. Create `evals/evals.json` with test prompts
3. Run evals with subagents (with-skill and baseline)
4. Grade results and launch the viewer

**Option B: Use the template we created**

```bash
# Evals already created at:
.claude/skills/skill-creator/evals/evals.json

# Edit to customize for your needs
```

**Option C: Create with our helper script**

```bash
# Create task eval set
python3 evals/anthropic_evals.py create --skill-name mcp-email --type task

# Create trigger eval set (for testing skill description)
python3 evals/anthropic_evals.py create --skill-name mcp-email --type trigger
```

### Step 2: Run Evals

**For Task Evals** (testing skill execution):

Use the skill-creator skill within Claude Code:

```bash
claude

# Say:
"I want to run evals on my mcp-email skill. Use the skill-creator skill to execute the test cases in evals/evals.json"
```

The skill-creator will:
1. Spawn subagents for each test case (with-skill and baseline)
2. Grade outputs against expectations
3. Generate `benchmark.json` with aggregated results
4. Launch the eval viewer

**For Trigger Evals** (testing skill description):

```bash
# Create trigger eval set first
python3 evals/anthropic_evals.py create --skill-name mcp-email --type trigger --output evals/trigger-evals.json

# Run trigger eval
python3 .claude/skills/skill-creator/scripts/run_eval.py \
  --eval-set evals/trigger-evals.json \
  --skill-path .claude/skills/skill-creator \
  --runs-per-query 3 \
  --verbose
```

### Step 3: Review Results

**Launch the eval viewer**:

```bash
# After task evals complete
python3 .claude/skills/skill-creator/eval-viewer/generate_review.py \
  mcp-email-workspace/iteration-1 \
  --skill-name "mcp-email" \
  --benchmark mcp-email-workspace/iteration-1/benchmark.json
```

This opens a web interface showing:
- Qualitative outputs (side-by-side comparison)
- Quantitative metrics (pass rates, timing, tokens)
- Grading results with evidence

---

## File Formats

### Official Anthropic Format: `evals/evals.json`

```json
{
  "skill_name": "mcp-email",
  "evals": [
    {
      "id": 1,
      "prompt": "Send an email to test@example.com",
      "expected_output": "Email sent successfully",
      "files": [],
      "expectations": [
        "The email was sent to test@example.com",
        "The subject line is correct"
      ]
    }
  ]
}
```

### Trigger Eval Format: `trigger-evals.json`

```json
{
  "skill_name": "mcp-email",
  "queries": [
    {
      "query": "Send an email to test@example.com",
      "should_trigger": true
    },
    {
      "query": "Write a Python script",
      "should_trigger": false
    }
  ]
}
```

### Our CSV Format: `evals/prompt-sets/mcp-email.csv`

```csv
id,should_trigger,prompt,expected_outcome,category
test-01,true,"Send an email to test@example.com",email_sent,explicit
test-02,false,"Write a Python script",no_trigger,negative
```

---

## Workspace Organization

Official skill-creator creates this structure:

```
mcp-email-workspace/
├── iteration-1/
│   ├── eval-0/
│   │   ├── with_skill/
│   │   │   ├── outputs/
│   │   │   ├── metrics.json
│   │   │   └── timing.json
│   │   ├── without_skill/
│   │   │   ├── outputs/
│   │   │   └── metrics.json
│   │   ├── grading.json
│   │   └── eval_metadata.json
│   ├── eval-1/
│   │   └── ...
│   ├── benchmark.json
│   └── benchmark.md
├── iteration-2/
│   └── ...
└── history.json
```

---

## Comparison: Two Eval Systems

| Feature | CSV-Based (Ours) | Official Anthropic |
|---------|------------------|-------------------|
| **Setup** | ✅ Simple (CSV file) | ⚠️ Complex (JSON + workspace) |
| **Execution** | ✅ Instant (simulated) | ⚠️ Slow (subagents) |
| **Real testing** | ❌ Simulated | ✅ Real Claude Code execution |
| **Baseline comparison** | ❌ No | ✅ With/without skill |
| **Qualitative review** | ❌ Markdown report | ✅ Web viewer |
| **Quantitative metrics** | ✅ Basic | ✅ Comprehensive |
| **Best for** | Development | Production benchmarking |

---

## Recommended Workflow

### During Development (Fast Iteration)

1. **Use CSV-based evals** for quick feedback:
   ```bash
   python3 evals/runner.py --skill mcp-email --prompt-set evals/prompt-sets/mcp-email.csv
   ```

2. **Fix issues** based on report

3. **Repeat** until stable

### Before Release (Production Benchmarking)

1. **Use official skill-creator** for comprehensive evals:
   ```bash
   claude
   "Run full evals on my skill with the skill-creator skill"
   ```

2. **Review results** in web viewer

3. **Iterate** based on qualitative + quantitative feedback

4. **Document** benchmark results

---

## Integration Script: `anthropic_evals.py`

This script bridges both systems:

```bash
# Create official eval set
python3 evals/anthropic_evals.py create --skill-name mcp-email --type task

# Create trigger eval set
python3 evals/anthropic_evals.py create --skill-name mcp-email --type trigger

# Convert our CSV to official JSON format
python3 evals/anthropic_evals.py convert \
  --csv evals/prompt-sets/mcp-email.csv \
  --output evals/mcp-email-official.json

# Run trigger eval
python3 evals/anthropic_evals.py trigger \
  --skill-path .claude/skills/skill-creator \
  --eval-set evals/trigger-evals.json
```

---

## Troubleshooting

### Problem: skill-creator skill not available

**Solution**: Ensure official skill-creator is installed:
```bash
# Check installation
ls .claude/skills/skill-creator/SKILL.md

# Reinstall if needed
npx skills add https://github.com/anthropics/skills --skill skill-creator
```

### Problem: Eval viewer not opening

**Solution**: Use static HTML mode:
```bash
python3 .claude/skills/skill-creator/eval-viewer/generate_review.py \
  mcp-email-workspace/iteration-1 \
  --skill-name "mcp-email" \
  --static mcp-email-review.html
```

### Problem: Benchmark shows 0% pass rate

**Solution**: Check grading assertions:
- Ensure expectations are verifiable
- Check grader can access outputs
- Review grading.json for errors

---

## References

- `evals/README.md` - CSV-based framework overview
- `evals/IMPLEMENTATION_SUMMARY.md` - Complete implementation summary
- `.claude/skills/skill-creator/SKILL.md` - Official skill documentation
- `.claude/skills/skill-creator/references/schemas.md` - JSON schema reference
- [Anthropic Skills Repo](https://github.com/anthropics/skills)

---

## Next Steps

1. **Try CSV-based evals** for quick testing
2. **Run official evals** with skill-creator for production benchmarking
3. **Compare results** from both systems
4. **Contribute** improvements to either system
