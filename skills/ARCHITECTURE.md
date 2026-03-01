# Personal AI Employee - Professional Skill Architecture

> World-class skill architecture for the Personal AI Employee hackathon project.

## Overview

This architecture defines a comprehensive, production-grade skill system that transforms Claude Code into an autonomous Digital FTE (Full-Time Equivalent). Skills are organized by workflow phases following the perception → reasoning → action pattern.

## Architecture Principles

### 1. Workflow-First Design
Skills align with the AI Employee's operational flow:
```
External Sources → Watchers → Obsidian Vault → Claude Code → MCP → Actions
```

### 2. Progressive Disclosure
Each skill follows a three-level information architecture:
- **SKILL.md** (<500 lines) - Core procedural knowledge
- **references/** - Domain expertise, patterns, examples
- **scripts/** - Executable procedures where deterministic behavior is required

### 3. Zero-Shot Domain Expert
Skills embed all necessary domain knowledge, requiring only user-specific context at runtime.

### 4. Human-in-the-Loop (HITL)
Sensitive operations require explicit approval through the vault folder system:
```
/Pending_Approval/ → /Approved/ or /Rejected/
```

## Skill Categories

### Category 1: Watcher Skills (Perception Layer)
Monitor external sources and create action items.

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `watch-gmail` | Monitor Gmail for new messages | Cron/continuous |
| `watch-whatsapp` | Monitor WhatsApp for urgent messages | Continuous |
| `watch-filesystem` | Monitor drop folders for new files | Event-based |
| `watch-finance` | Monitor bank transactions | Scheduled |

### Category 2: Processor Skills (Reasoning Layer)
Analyze items and create actionable plans.

| Skill | Purpose | Input | Output |
|-------|---------|-------|--------|
| `process-email` | Analyze and route emails | Needs_Action/*.md | Plan.md |
| `process-whatsapp` | Handle WhatsApp messages | Needs_Action/*.md | Plan.md |
| `process-payment` | Handle payment requests | Needs_Action/*.md | Plan.md |
| `create-plan` | Generate execution plans | Any action item | Plan.md |

### Category 3: Action Skills (Execution Layer)
Execute approved actions through MCP servers.

| Skill | Purpose | HITL Required |
|-------|---------|---------------|
| `send-email` | Send emails via Gmail MCP | For new contacts |
| `post-social` | Post to LinkedIn/Twitter | For new content |
| `make-payment` | Execute payments | Always |
| `schedule-event` | Create calendar events | No |

### Category 4: Orchestration Skills (Control Layer)
Coordinate multi-step workflows and maintain system health.

| Skill | Purpose |
|-------|---------|
| `ralph-loop` | Persistent task completion loop |
| `orchestrator` | Main coordination process |
| `watchdog` | Health monitoring and recovery |
| `vault-sync` | Cloud-local synchronization (Platinum) |

### Category 5: Intelligence Skills (Business Layer)
Generate insights and reports for decision-making.

| Skill | Purpose | Frequency |
|-------|---------|-----------|
| `ceo-briefing` | Weekly business summary | Weekly |
| `audit-subscriptions` | Find unused subscriptions | Monthly |
| `track-revenue` | Revenue tracking and alerts | Daily |
| `analyze-bottlenecks` | Identify process delays | Weekly |

### Category 6: Utility Skills (Support Layer)
Support functions used across other skills.

| Skill | Purpose |
|-------|---------|
| `request-approval` | Create approval files |
| `log-action` | Audit logging |
| `format-briefing` | Template formatting |
| `validate-vault` | Vault integrity checks |

## Directory Structure

```
skills/
├── ARCHITECTURE.md          # This file
├── README.md                # Skills overview
│
├── perception/              # Category 1: Watcher Skills
│   ├── watch-gmail/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── gmail-api.md
│   │   │   ├── error-handling.md
│   │   │   └── rate-limits.md
│   │   └── scripts/
│   │       └── gmail_watcher.py
│   ├── watch-whatsapp/
│   ├── watch-filesystem/
│   └── watch-finance/
│
├── reasoning/               # Category 2: Processor Skills
│   ├── process-email/
│   ├── process-whatsapp/
│   ├── process-payment/
│   └── create-plan/
│
├── action/                  # Category 3: Action Skills
│   ├── send-email/
│   ├── post-social/
│   ├── make-payment/
│   └── schedule-event/
│
├── orchestration/           # Category 4: Orchestration Skills
│   ├── ralph-loop/
│   ├── orchestrator/
│   ├── watchdog/
│   └── vault-sync/
│
├── intelligence/            # Category 5: Intelligence Skills
│   ├── ceo-briefing/
│   ├── audit-subscriptions/
│   ├── track-revenue/
│   └── analyze-bottlenecks/
│
└── utility/                 # Category 6: Utility Skills
    ├── request-approval/
    ├── log-action/
    ├── format-briefing/
    └── validate-vault/
```

## Skill Interaction Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PERCEPTION LAYER                            │
│  watch-gmail │ watch-whatsapp │ watch-filesystem │ watch-finance    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Creates files in /Needs_Action/
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         REASONING LAYER                             │
│     process-email │ process-whatsapp │ create-plan                  │
│                         │                                            │
│                         ▼                                            │
│              ┌─────────────────────┐                                │
│              │   /Pending_Approval │  ← HITL for sensitive actions  │
│              └──────────┬──────────┘                                │
│                         │ Human moves to /Approved/                  │
│                         ▼                                            │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          ACTION LAYER                               │
│     send-email │ post-social │ make-payment │ schedule-event        │
│              via MCP Servers (email-mcp, browser-mcp, etc.)          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Logs to /Logs/
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        INTELLIGENCE LAYER                           │
│     ceo-briefing │ audit-subscriptions │ track-revenue              │
│              Updates Dashboard.md, creates Briefings/               │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │   /Done/        │
                    └─────────────────┘
```

## Professional Skill Template

Every skill follows this structure:

```yaml
---
name: skill-name
description: |
  [What] Clear capability statement.
  [When] Triggers when users ask to X or Y happens.
allowed-tools: [Read, Write, Glob, Grep, Bash]  # Optional restriction
model: sonnet  # Optional model preference
---

# Skill Title

Brief description of what this skill does.

## When to Use

- Trigger condition 1
- Trigger condition 2
- User command: `/skill-name`

## Before Implementation

| Source | Gather |
|--------|--------|
| Codebase | Existing patterns, configurations |
| Conversation | User's specific requirements |
| Skill References | Domain patterns, best practices |
| User Guidelines | Company_Handbook.md rules |

## Workflow

1. Step one
2. Step two
3. Step three

## Error Handling

| Error | Recovery |
|-------|----------|
| Type A | Action 1 |
| Type B | Action 2 |

## Security Considerations

- Permission boundaries
- HITL requirements

## Output

Description of outputs and their locations.

## References

| File | Purpose |
|------|---------|
| references/domain.md | Domain expertise |
| references/patterns.md | Implementation patterns |
```

## Integration Points

### Vault Integration
All skills interact with the Obsidian vault:

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

### MCP Integration
Action skills use MCP servers:

| MCP Server | Skills Using |
|------------|--------------|
| email-mcp | send-email, process-email |
| browser-mcp | make-payment, post-social |
| calendar-mcp | schedule-event |
| filesystem | All skills (built-in) |

### Configuration
Skills read from:

```
vault/
├── Company_Handbook.md    # Rules and autonomy levels
├── Business_Goals.md      # Targets and KPIs
└── .config/
    └── skill_settings.json # Skill-specific configs
```

## Quality Metrics

Each skill includes:

| Metric | Measurement |
|--------|-------------|
| Success Rate | Actions completed / Actions attempted |
| HITL Rate | Actions requiring approval / Total actions |
| Error Rate | Errors / Total operations |
| Recovery Rate | Auto-recovered errors / Total errors |

## Version Control

Skills are versioned using semantic versioning:

```
skill-name/
├── SKILL.md          # v1.2.0
└── references/
    └── changelog.md  # Version history
```

## Testing

Each skill includes test scenarios:

```
skill-name/
└── tests/
    ├── test_success.md    # Happy path
    ├── test_error.md      # Error conditions
    └── test_hitl.md       # HITL scenarios
```

## Hackathon Tier Mapping

| Tier | Required Skills |
|------|-----------------|
| Bronze | watch-gmail, process-email, create-plan, request-approval |
| Silver | + watch-whatsapp, send-email, orchestrator, ralph-loop |
| Gold | + post-social, ceo-briefing, audit-subscriptions, watch-finance |
| Platinum | + vault-sync, watch-dog, make-payment |

---

*Architecture Version: 1.0.0*
*Last Updated: 2026-03-01*