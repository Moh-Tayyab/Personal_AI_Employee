# Process Email - Claude Agent Skill

This skill processes incoming emails from the Needs_Action folder, drafts appropriate responses, and creates follow-up tasks.

## When to Use

- When new emails appear in the vault's Needs_Action folder
- When the user asks to "process emails" or "check email"

## How It Works

1. Reads all email files from Needs_Action folder
2. Analyzes each email against Company_Handbook.md rules
3. Determines priority and category
4. Drafts response (if needed)
5. Creates Plan.md with actionable steps
6. Moves completed emails to Done

## Requirements

- Vault must have Company_Handbook.md with communication rules
- Needs_Action folder must exist with email .md files

## Actions Taken

- Creates Plan.md files in Plans/ folder
- Creates approval requests for sensitive emails
- Generates draft responses
- Updates Dashboard.md with activity

## Example Usage

```
/process-email
```

Or triggered by the Orchestrator when new emails are detected.
