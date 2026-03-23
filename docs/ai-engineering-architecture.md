# AI Engineering Architecture

This repository is configured as a hybrid AI coding environment.

## Roles and Orchestration

- Claude Code is the primary orchestrator.
- Codex CLI is a secondary coding agent invoked for focused sub-tasks.
- MCP servers provide tool integrations.
- `.claude/skills` define workflows and delegation rules.

## Execution Flow

1. Claude receives a task and decomposes it across roles.
2. Claude invokes MCP tools for external actions.
3. Claude delegates complex sub-tasks to Codex with `codex exec "<task>"`.
4. Codex returns a report or suggested changes.
5. Claude integrates changes, runs tests, and finalizes outputs.

## MCP Integration

Configuration lives in `.mcp.json`. Servers include:

- Codex MCP server for subagent execution
- Playwright MCP server for browser automation
- Git MCP server for repository actions
- Web search MCP server for research

Adjust the `command` and `args` fields to match local installations.

Validate MCP setup with:

```bash
scripts/validate_mcp.sh
```

## Skills

- `.claude/skills/codex`: Delegation guidance for Codex CLI usage
- `.claude/skills/fix-ticket`: End-to-end bug fix workflow

## Hooks

`.claude/hooks/code_review.sh` calls Codex to review git diffs and produce a summary.
