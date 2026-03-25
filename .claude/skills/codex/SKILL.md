---
name: codex
description: Delegate complex engineering work from Claude to Codex CLI when tasks need a secondary coding agent, large refactors, architecture analysis, performance optimization, broad repo scans, or parallel investigation. Use when a dedicated coding subagent should execute `codex exec "<task>"` and return a written result.
---

# Codex Delegation

## Delegate to Codex

- Use Codex when the task benefits from a second agent running focused analysis or making isolated edits.
- Prefer Codex for large refactors, architecture reviews, performance investigations, or multi-file change planning.
- Keep the prompt specific and bounded; include file paths, goals, constraints, and acceptance criteria.

## Delegation Pattern

1. Summarize the task in 3-6 bullet points.
2. Specify expected outputs (report, patch, commands to run).
3. Ask for risks and test recommendations.
4. Run: `codex exec "<task>"`
5. Review Codex output and integrate changes or feedback.

## Use Cases

- Large refactors spanning multiple modules.
- Architecture analysis and dependency mapping.
- Performance profiling and optimization planning.

## Output Expectations

Codex should return:

- Clear findings or a proposed diff.
- Test plan or validation steps.
- Any blockers or assumptions.
