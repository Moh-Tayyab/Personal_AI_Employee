# Personal AI Employee - Professional Skills

> World-class skill architecture for the Personal AI Employee hackathon project.

## Overview

This directory contains production-grade skills that transform Claude Code into an autonomous Digital FTE (Full-Time Equivalent). Each skill is designed following the perception → reasoning → action pattern with built-in human-in-the-loop safety.

## Quick Start

```bash
# Install skills (from project root)
npx skills add ./skills/reasoning/process-email
npx skills add ./skills/reasoning/create-plan
npx skills add ./skills/utility/request-approval
npx skills add ./skills/action/execute-action

# Use a skill
/process-email
/create-plan
/request-approval
/execute-action
```

## Skill Architecture

```
skills/
├── ARCHITECTURE.md              # Full architecture documentation
├── README.md                    # This file
│
├── perception/                  # Watch incoming sources
│   └── watch-gmail/            # Monitor Gmail inbox
│       ├── SKILL.md
│       └── references/
│
├── reasoning/                   # Analyze and plan
│   ├── process-email/          # Email analysis & routing
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── email-categories.md
│   │       ├── response-templates.md
│   │       ├── priority-rules.md
│   │       └── autonomy-matrix.md
│   └── create-plan/            # Generate execution plans
│       └── SKILL.md
│
├── action/                      # Execute approved actions
│   ├── execute-action/         # MCP-based action execution
│   │   └── SKILL.md
│   ├── mcp-email/              # Email MCP handler
│   │   └── SKILL.md
│   ├── mcp-browser/            # Browser MCP handler
│   │   └── SKILL.md
│   └── mcp-social/             # Social media MCP handler
│       ├── SKILL.md
│       └── references/
│
├── orchestration/               # Coordinate and control
│   ├── orchestrator/           # Master coordination process
│   │   └── SKILL.md
│   └── ralph-loop/             # Persistent task completion
│       └── SKILL.md
│
├── intelligence/                # Generate insights
│   └── ceo-briefing/           # Weekly business summary
│       └── SKILL.md
│
└── utility/                     # Support functions
    └── request-approval/       # HITL approval workflow
        └── SKILL.md
```

## Skill Categories

### 1. Perception Skills (Watchers)

Monitor external sources and create action items.

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `watch-gmail` | Monitor Gmail for new messages | Continuous/Scheduled |
| `watch-whatsapp` | Monitor WhatsApp for urgent messages | Continuous |
| `watch-filesystem` | Monitor drop folders for new files | Event-based |

### 2. Reasoning Skills (Processors)

Analyze items and create actionable plans.

| Skill | Purpose | Input | Output |
|-------|---------|-------|--------|
| `process-email` | Analyze and route emails | Needs_Action/*.md | Plan.md |
| `create-plan` | Generate execution plans | Action items | Plan.md |

### 3. Action Skills (Executors)

Execute approved actions through MCP servers.

| Skill | Purpose | HITL Required |
|-------|---------|---------------|
| `execute-action` | Execute via MCP | Based on autonomy level |
| `mcp-email` | Handle email operations | For new contacts |
| `mcp-browser` | Browser automation, payments | Always for payments |
| `mcp-social` | Social media posting | For new content |

### 4. Orchestration Skills (Control)

Coordinate multi-step workflows and maintain system health.

| Skill | Purpose |
|-------|---------|
| `orchestrator` | Master coordination process |
| `ralph-loop` | Persistent task completion |

### 5. Intelligence Skills (Insights)

Generate reports and business intelligence.

| Skill | Purpose | Frequency |
|-------|---------|-----------|
| `ceo-briefing` | Weekly business summary | Weekly |

### 6. Utility Skills (Support)

Support functions used across other skills.

| Skill | Purpose |
|-------|---------|
| `request-approval` | Create HITL approval requests |

## Hackathon Tier Coverage

| Tier | Required Skills | Status |
|------|-----------------|--------|
| **Bronze** | watch-gmail, process-email, create-plan, request-approval | ✅ Complete |
| **Silver** | + watch-whatsapp, execute-action, orchestrator, ralph-loop | ✅ Complete |
| **Gold** | + ceo-briefing, audit-subscriptions, social-post | ✅ Complete |
| **Platinum** | + vault-sync, advanced orchestration | 📋 Pending |

## Workflow Example

```
1. Gmail Watcher detects new email
   └── Creates: Needs_Action/EMAIL_20260301_client.md

2. Orchestrator triggers processing
   └── Calls: /process-email

3. process-email analyzes
   └── Determines: High priority, Level 2 autonomy
   └── Creates: Plans/PLAN_20260301_EMAIL_client.md
   └── Creates: Drafts/DRAFT_response_client.md

4. For Level 3 actions (new contact)
   └── Calls: /request-approval
   └── Creates: Pending_Approval/EMAIL_client_approval.md

5. Human reviews and approves
   └── Moves to: Approved/

6. execute-action sends email
   └── Calls: email MCP
   └── Moves to: Done/

7. Dashboard updated
   └── All actions logged
```

## Professional Skill Features

Every skill includes:

| Feature | Description |
|---------|-------------|
| **Error Recovery** | Retry logic, graceful degradation, fallback strategies |
| **Audit Logging** | Full action logging for compliance |
| **Security** | Credential handling, permission boundaries, HITL enforcement |
| **Documentation** | Inline help, usage examples, troubleshooting |
| **References** | Detailed domain knowledge in separate files |

## Skill Quality Standards

Each skill is validated against:

```yaml
validation_criteria:
  structure:
    - SKILL.md exists and < 500 lines
    - YAML frontmatter complete
    - References in separate files
    - Clear workflow documented

  content:
    - When to use section
    - Before implementation checklist
    - Error handling table
    - Output artifacts listed

  technical:
    - Allowed tools specified
    - MCP integrations documented
    - Rate limits considered
    - Retry logic included

  documentation:
    - Usage examples provided
    - Edge cases covered
    - References linked
```

## Running Skills

### Manual Trigger

```bash
# Process emails
/process-email

# Create plan for specific item
/create-plan Needs_Action/EMAIL_20260301_client.md

# Request approval
/request-approval --action send_email --to client@example.com

# Execute approved actions
/execute-action
```

### Automated (Orchestrator)

```bash
# Start orchestrator
python orchestrator.py start

# Check status
python orchestrator.py status

# Process once
python orchestrator.py --once
```

## Configuration

Skills read configuration from:

```
vault/
├── Company_Handbook.md    # Rules, autonomy levels, approval thresholds
├── Business_Goals.md      # Targets, priorities, contacts
└── .config/
    ├── skill_settings.json
    ├── gmail_watcher.yaml
    └── orchestrator.yaml
```

## Vault Integration

Skills interact with vault folders:

```
vault/
├── Needs_Action/      ← Watcher skills write here
├── Plans/             ← Processor skills write here
├── Pending_Approval/  ← Sensitive actions await here
├── Approved/          ← Human-approved actions
├── Done/              ← Completed items
├── Logs/              ← Audit logs (JSON)
├── Briefings/         ← CEO briefings
└── Dashboard.md       ← Real-time status
```

## MCP Integration

Action skills use MCP servers:

| MCP Server | Skills Using |
|------------|--------------|
| email-mcp | execute-action, mcp-email |
| browser-mcp | execute-action, mcp-browser |
| linkedin-mcp | mcp-social |
| twitter-mcp | mcp-social |
| social-mcp | mcp-social |
| calendar-mcp | execute-action (calendar) |
| filesystem | All skills (built-in) |

## Validation

Run skill validation:

```bash
# Validate all skills
python scripts/validate_skills.py

# Validate specific skill
python scripts/validate_skills.py skills/reasoning/process-email

# Generate validation report
python scripts/validate_skills.py --report
```

## Contributing

To add a new skill:

1. Follow the directory structure
2. Create SKILL.md with required sections
3. Add references/ for detailed content
4. Run validation
5. Update this README

## References

- [Architecture Documentation](ARCHITECTURE.md)
- [Hackathon Requirements](../requirments.md)
- [Claude Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [skills.sh Ecosystem](https://skills.sh/)

---

*Version: 1.0.0*
*Last Updated: 2026-03-01*