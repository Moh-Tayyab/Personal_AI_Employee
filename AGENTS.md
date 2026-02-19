# Personal AI Employee - Technical Specification

## Overview

A **Digital FTE (Full-Time Equivalent)** is an AI agent that operates as a autonomous employee, managing personal and business affairs 24/7. Built with Claude Code as the reasoning engine and Obsidian as the management dashboard.

## Core Concept

The Personal AI Employee solves the "lazy agent" problem through:
- **Watchers**: Python scripts that monitor external sources and wake the agent
- **Ralph Wiggum Loop**: Persistence pattern that keeps the agent working until tasks complete
- **Human-in-the-Loop**: File-based approval system for sensitive actions

## Architecture

```
External Sources → Watchers → Obsidian Vault → Claude Code → MCP Servers → Actions
```

### Components

| Layer | Component | Purpose |
|-------|-----------|---------|
| Perception | Watchers | Monitor Gmail, WhatsApp, files |
| Memory/GUI | Obsidian Vault | Local Markdown database |
| Reasoning | Claude Code | Analysis and planning |
| Action | MCP Servers | External integrations |

## Vault Structure

```
vault/
├── Dashboard.md           # Real-time status
├── Company_Handbook.md    # AI behavior rules
├── Business_Goals.md     # Objectives and KPIs
├── Needs_Action/         # Items requiring attention
├── Plans/                # Generated plan files
├── Done/                 # Completed tasks
├── Pending_Approval/     # Awaiting human approval
├── Approved/             # Ready for execution
├── Rejected/             # Rejected items
├── Logs/                 # Activity audit logs
└── Briefings/            # CEO reports
```

## Tiers

### Bronze - Foundation
- Obsidian vault with Dashboard and Handbook
- One working watcher (Gmail or filesystem)
- Claude Code integration with vault

### Silver - Functional Assistant
- Multiple watchers (Gmail + WhatsApp + Files)
- Plan.md generation for each task
- Email MCP server
- Human-in-the-loop approval workflow

### Gold - Autonomous Employee
- Odoo accounting integration
- LinkedIn, Twitter, Facebook MCPs
- Weekly CEO Briefing generation
- Error recovery and logging

### Platinum - Cloud + Local
- Cloud VM for 24/7 operation
- Work-zone specialization (Cloud vs Local)
- Git-based vault sync
- Agent coordination via file handoffs

## Technology Stack

| Component | Technology |
|-----------|------------|
| Reasoning | Claude Code |
| Database | Obsidian (Markdown) |
| Watchers | Python 3.13+ |
| Automation | MCP Servers |
| Process Manager | PM2 |
| Cloud | Oracle Cloud / AWS |

## Security

- **Local-first**: Data stays on your machine
- **Human-in-the-loop**: Sensitive actions require approval
- **Secrets excluded**: Credentials never sync to cloud
- **Audit logging**: All actions tracked

## Example: End-to-End Flow

1. **Detection**: WhatsApp Watcher detects "invoice" keyword
2. **Creation**: Creates action file in Needs_Action/
3. **Planning**: Orchestrator creates Plan.md
4. **Reasoning**: Claude analyzes and determines action
5. **Approval**: Creates approval request in Pending_Approval/
6. **Execution**: User moves to Approved/ folder
7. **Action**: Orchestrator triggers MCP to send email
8. **Logging**: Action logged to Logs/

## Key Patterns

### Claim-by-Move
First agent to move item from Needs_Action to In_Progress owns it.

### Single-Writer
Only Local agent writes to Dashboard.md.

### Approval File
Sensitive actions create markdown files requiring manual move to Approved/.

## References

- [Claude Code](https://claude.com/product/claude-code)
- [Obsidian](https://obsidian.md)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Panaversity Hackathon](https://agentfactory.panaversity.org)
