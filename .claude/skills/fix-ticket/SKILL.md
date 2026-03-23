---
name: fix-ticket
description: End-to-end bug fix workflow for tickets and incident reports. Use when a ticket requires reproduction (often via Playwright), root cause analysis, implementation, tests, Codex review, and committing changes.
---

# Fix Ticket Workflow

## Inputs

- Bug report or ticket content (file path or pasted text)
- Target environment and reproduction steps (if known)
- Expected behavior and acceptance criteria

## Workflow

1. Read the ticket and summarize the failure and scope.
2. Reproduce the issue.
3. Use Playwright when UI/browser steps are required.
4. Identify root cause with code and logs.
5. Research solution options and pick the lowest-risk fix.
6. Implement the fix with minimal changes.
7. Run relevant tests or targeted scripts.
8. Ask Codex to review the diff and highlight risks.
9. Commit changes with a clear message.

## Playwright Guidance

- Prefer deterministic selectors and stable flows.
- Save traces or screenshots on failure.

## Codex Review Prompt

Use:

`codex exec "Review this git diff and suggest improvements. Focus on correctness, tests, and regressions."`

## Exit Criteria

- Repro steps pass or issue no longer occurs.
- Tests related to the area pass.
- Codex review findings addressed or documented.
