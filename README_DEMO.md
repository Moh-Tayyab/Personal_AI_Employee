# Personal AI Employee - Digital FTE

*Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

## Overview

The Personal AI Employee is a comprehensive system that acts as your digital full-time employee, proactively managing personal and business affairs using Claude Code as the executor and Obsidian as the management dashboard.

Unlike traditional chatbots that wait for your input, this system actively monitors your Gmail, WhatsApp, filesystems and more, making intelligent decisions based on your company handbook and business goals.

## Key Capabilities

### 🧠 Claude AI Reasoning Engine
- Uses Claude API for intelligent decision making
- Applies company rules from handbook automatically
- Makes context-aware decisions based on stored knowledge
- Implements Ralph Wiggum persistence loops for task completion

### 🗄️ Obsidian-Style Vault
- Local-first storage for maximum privacy
- Organized folder structure for workflow management
- Markdown-based for easy reading and editing
- Complete audit trail of all activities

### 👂 Intelligent Watchers
- Monitors Gmail via OAuth API
- Watches WhatsApp messages through Playwright automation
- Tracks filesystem changes for new files
- Triggers processing automatically without manual intervention

### 🔌 MCP Server Ecosystem
- **Email Server**: Send and search emails via Gmail API
- **LinkedIn Server**: Professional posting and profile management
- **Twitter Server**: Social media management
- **Odoo Server**: Accounting and ERP integration
- **Custom Servers**: Extend functionality for any service

### 🛡️ Human-in-the-Loop Approval
- Automatic routing based on defined autonomy levels
- Webhook notifications to Slack/Discord
- Simple file movement for approval workflow
- Maintains human oversight on sensitive operations

### 📊 CEO Briefing Generator
- Weekly business intelligence reports
- Revenue tracking and KPIs
- Bottleneck identification
- Proactive business suggestions

## Architecture

```
External Sources → Watchers → Obsidian Vault → Claude Code → MCP → Actions
                      ↓                           ↓
               HTTP Hooks (NEW)            Agent Teams (NEW)
                      ↓                           ↓
         External Webhooks / Dashboard    Coordinated Multi-Agent Workflows
```

## Setup

### Prerequisites
- Python 3.9+
- Claude API key
- Gmail OAuth credentials (for email functionality)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Personal_AI_Employee
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export ANTHROPIC_API_KEY="your-claude-api-key"
export GMAIL_TOKEN_PATH="./vault/secrets/gmail_token.json"
```

4. Configure your company handbook and business goals:
```bash
# Edit these files to match your preferences
vim vault/Company_Handbook.md
vim vault/Business_Goals.md
```

5. Start the system:
```bash
# Start all services
./scripts/start_all.sh

# Or start just the orchestrator
python orchestrator.py --vault ./vault --dry-run false
```

## Demo Scripts

This repository includes several demo scripts to showcase the system capabilities:

1. **Capability Showcase**:
```bash
python demo_showcase_caps.py
```

2. **Quick Start Demo** (simulates core workflow):
```bash
python demo_quick_start.py
```

3. **Full Interactive Demo**:
```bash
python demo_interactive.py
```

## Core Workflows

### Email Processing Flow
1. Gmail watcher detects new email
2. Email saved to `Needs_Action/` folder
3. Orchestrator triggers Claude analysis
4. Claude creates action plan in `Plans/` folder
5. If sensitive: move to `Pending_Approval/` with notification
6. If routine: execute automatically via MCP server
7. Result logged to `Done/` folder

### Social Media Posting Flow
1. AI identifies optimal posting opportunity
2. Creates content based on business goals
3. If pre-approved template: post automatically
4. If new content: submit for approval
5. Uses LinkedIn/Twitter MCP servers to post

### Invoice Processing Flow
1. Invoice email detected via watcher
2. Amount checked against approval thresholds
3. If <$500: pay automatically via MCP server
4. If >$500: route to approval queue with webhook notification
5. Track payment status and log results

## Tiers

### Bronze - Foundation (✅ 95% Complete)
- Obsidian vault structure
- Gmail, WhatsApp, filesystem watchers
- Claude API integration
- Basic orchestration

### Silver - Functional (✅ 85% Complete)
- MCP servers for email, LinkedIn, Twitter
- Human-in-the-loop approval workflow
- CEO briefing generator
- Dry-run safety mode

### Gold - Autonomous (✅ 75% Complete)
- Advanced AI reasoning and planning
- Multi-domain agent teams
- Proactive business intelligence
- Persistent task completion

### Platinum - Cloud + Local (✅ 85% Complete)
- Production deployment scripts
- Health monitoring
- Vault synchronization
- 24/7 operation capability

## The "Monday Morning CEO Briefing"

One standout feature is the "Monday Morning CEO Briefing" where the AI autonomously audits bank transactions and tasks to report revenue and bottlenecks, transforming the AI from a chatbot into a proactive business partner.

Example briefing:
```
# Monday Morning CEO Briefing - March 16, 2026

## 📊 Revenue Summary
- Weekly Revenue: $12,450 (↑ 12% from last week)
- Pipeline Value: $89,200

## ✅ Completed Tasks
- Responded to 23 client emails
- Posted 3 LinkedIn updates
- Processed 12 routine approvals

## ⚠️ Bottlenecks Identified
- Invoice #INV-2026-0315 delayed (awaiting client approval)
- LinkedIn ad campaign needs optimization
```

## Benefits

- **24/7 Operation**: Works while you sleep
- **Privacy First**: All data stays local to your machine
- **Intelligent**: Real AI reasoning, not just rule matching
- **Safe**: Human oversight for sensitive operations
- **Scalable**: Extend with custom MCP servers
- **Proactive**: CEO briefings and business insights
- **Flexible**: Adjust autonomy levels as needed

## The Ralph Wiggum Persistence Loop

Named after the "I meant to do that!" character, the system implements persistent loops that continue working until tasks are complete. If the AI encounters an obstacle, it will try alternative approaches rather than giving up, only asking for human help when truly stuck.

## Contributing

This system is designed to be extensible. You can add new MCP servers, watchers, and capabilities as needed. The architecture makes it easy to enhance functionality while maintaining safety and privacy.

## Security

- All personal data stored locally
- OAuth 2.0 for external service access
- Human approval for sensitive operations
- Audit trails for all actions
- Dry-run mode for testing

## Next Steps

1. Customize the `Company_Handbook.md` for your specific needs
2. Set up the required API keys and credentials
3. Run the demo scripts to see capabilities
4. Start with dry-run mode to observe behavior
5. Gradually increase autonomy as confidence grows
6. Add custom MCP servers for services you use

---

*Transform your AI from a chatbot into a proactive digital employee that manages your affairs autonomously while maintaining the oversight you need.*