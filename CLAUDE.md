# Personal AI Employee - Project Context

This is a Personal AI Employee project - a Digital FTE (Full-Time Equivalent) that autonomously manages personal and business affairs using Claude Code, Obsidian, and MCP servers.

## Project Summary

A local-first, autonomous AI agent that:
- Monitors email, WhatsApp, and files via Python watchers
- Uses Claude Code as the reasoning engine
- Stores everything in an Obsidian Markdown vault
- Executes actions through MCP (Model Context Protocol) servers
- Requires human approval for sensitive operations
- **NEW**: Exposes HTTP endpoints for external integrations and webhooks
- **NEW**: Supports agent teams for coordinated multi-domain workflows
- **NEW**: Kiro for Claude Code integration for spec-driven development

## Kiro for Claude Code Integration

This project is configured with **Kiro for Claude Code** VSCode extension for spec-driven development.

### Kiro Directory Structure
```
.claude/
├── specs/                      # Feature specifications
│   └── email-notification-system/
│       ├── requirements.md     # What to build
│       ├── design.md           # How to build
│       └── tasks.md            # Implementation steps
├── agents/kfc/                 # Built-in workflow agents
│   ├── spec-requirements.md    # Requirements specialist
│   ├── spec-design.md          # Design specialist
│   ├── spec-tasks.md           # Task planning specialist
│   ├── spec-judge.md           # Quality assurance agent
│   ├── spec-impl.md            # Implementation specialist
│   ├── spec-test.md            # Testing specialist
│   └── spec-system-prompt-loader.md  # Workflow coordinator
├── steering/                   # AI guidance documents
│   ├── product.md              # Product vision and principles
│   ├── tech.md                 # Technical standards
│   └── structure.md            # Code organization
└── settings/
    └── kfc-settings.json       # Kiro configuration
```

### Kiro Workflow

1. **Create Spec with Sub-Agents** (Recommended):
   - Click Kiro for CC icon in VSCode activity bar
   - Click "New Spec with Agents" button (✨)
   - Enter feature description
   - Specialized agents work in parallel:
     - Requirements Agent → Defines WHAT to build
     - Design Agent → Architect HOW to build
     - Tasks Agent → Breaks into implementation steps
     - Judge Agent → Reviews and approves each phase

2. **Traditional Method**:
   - Click "+" in SPEC view
   - Generate requirements → design → tasks sequentially
   - Review at each step

3. **Implementation**:
   - Execute tasks from `tasks.md` one by one
   - Update task status as work progresses
   - Test agent validates completion

### Kiro Commands
```bash
# View spec status
ls .claude/specs/

# View agent configurations
cat .claude/agents/kfc/*.md

# View steering documents
cat .claude/steering/*.md

# Check Kiro settings
cat .claude/settings/kfc-settings.json
```

### Sub-Agent Roles

| Agent | Responsibility |
|-------|---------------|
| Requirements | User stories, functional/non-functional requirements |
| Design | Architecture, data models, API contracts |
| Tasks | Implementation breakdown, dependencies, estimates |
| Judge | Quality review, approval/rejection decisions |
| Implementation | Code execution, following design |
| Test | Validation, test coverage, sign-off |
| System Prompt Loader | Workflow coordination, context management |

## Groq Integration (Fast Inference)

This project integrates **Groq** for ultra-fast inference (500+ tokens/sec), ideal for:
- Email classification before Claude Code processing
- High-volume text categorization
- Sentiment analysis and keyword extraction
- Quick pre-processing to reduce Claude API costs

### Configuration

**Environment Variables** (in `.env`):
```bash
GROQ_API_KEY=gsk_xxx  # Your Groq API key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

### Usage

**Python API**:
```python
from utils.groq_client import GroqClient, classify_email, detect_urgency

client = GroqClient()

# Classify email
category = classify_email("URGENT: Server down!")  # Returns: "urgent"

# Detect urgency
urgency = detect_urgency("Need this ASAP!")  # Returns: "high"

# Custom classification
result = client.classify_text(
    "Invoice #123 attached",
    categories=["invoice", "normal", "spam"]
)

# Summarize
summary = client.summarize(long_text, max_length=50)

# Extract keywords
keywords = client.extract_keywords(email_body, max_keywords=5)
```

### Hybrid Workflow (Groq + Claude)

```
Email → Groq (classify) → If urgent → Claude Code (reasoning) → Action
                         If normal → Log only
```

**Example**:
```python
from utils.groq_client import classify_email
from orchestrator import process_with_claude

# Fast pre-classification with Groq
category = classify_email(email_text)

# Only use Claude for important items
if category in ["urgent", "invoice"]:
    process_with_claude(email)  # Expensive but powerful
else:
    log_only(email)  # Skip Claude, save costs
```

### Cost Optimization

| Task | Use Groq | Use Claude |
|------|----------|------------|
| Email classification | ✅ | ❌ |
| Keyword extraction | ✅ | ❌ |
| Simple summarization | ✅ | ❌ |
| Complex reasoning | ❌ | ✅ |
| Code generation | ❌ | ✅ |
| Multi-step planning | ❌ | ✅ |

## Architecture

```
External Sources → Watchers → Obsidian Vault → Claude Code → MCP → Actions
                      ↓                           ↓
               HTTP Hooks (NEW)            Agent Teams (NEW)
                      ↓                           ↓
         External Webhooks / Dashboard    Coordinated Multi-Agent Workflows
```

## Key Files

- `orchestrator.py` - Main coordinator that triggers Claude and processes items
- `watchers/` - Python scripts that monitor Gmail, files, WhatsApp
- `mcp/` - MCP servers for email, social media, Odoo accounting
- `hooks/` - HTTP webhook server for external integrations (NEW)
- `skills/` - Claude Code agent skills for specialized tasks
- `vault/` - Obsidian vault with all data and rules

## Vault Structure

```
vault/
├── Dashboard.md           # System status
├── Company_Handbook.md  # AI rules and autonomy levels
├── Business_Goals.md    # Revenue targets, KPIs
├── Needs_Action/        # Items requiring processing
├── Plans/               # Generated plan files
├── Done/                # Completed tasks
├── Pending_Approval/    # Items needing human approval
├── Approved/            # Approved items ready for execution
├── Logs/                # Daily activity logs
└── Briefings/           # CEO briefing reports
```

## Commands

```bash
# Start all services (recommended)
./scripts/start_all.sh

# Start HTTP hook server only
./scripts/start_hooks.sh --port 8080 --vault ./vault

# File watcher
python watchers/filesystem_watcher.py --vault ./vault --watch-path ./drop

# Orchestrator
python orchestrator.py --vault ./vault --dry-run

# Generate CEO Briefing
python scripts/generate_briefing.py --vault ./vault

# Vault sync (Platinum)
python scripts/vault_sync.py --vault ./vault --mode pull

# Stop all services
./scripts/stop_all.sh
```

## HTTP Endpoints (NEW)

The hook server provides REST endpoints for external integration:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/status` | GET | System status (items, counts) |
| `/pending` | GET | List pending approvals |
| `/dashboard` | GET | Dashboard data for web UI |
| `/webhook/email` | POST | Receive email webhooks |
| `/webhook/approval` | POST | Approval callbacks |
| `/webhook/github` | POST | GitHub webhook integration |
| `/trigger/process` | POST | Trigger processing manually |
| `/teams/create` | POST | Create new agent team |
| `/teams/list` | GET | List active teams |
| `/teams/{id}/tasks` | GET | Get team task list |
| `/teams/{id}/members` | GET | Get team members |

Example usage:
```bash
# Get system status
curl http://localhost:8080/status

# Approve via webhook
curl -X POST http://localhost:8080/webhook/approval \
  -H "Content-Type: application/json" \
  -d '{"action": "approve", "item_id": "EMAIL_001"}'

# Trigger processing
curl -X POST http://localhost:8080/trigger/process
```

## Tiers Status (Updated 2026-03-10)

1. **Bronze** - 80% Complete (watchers, vault, ✅ Claude API integration)
2. **Silver** - 70% Complete (✅ email send/search, MCP servers, approval workflow)
3. **Gold** - 60% Complete (Odoo, social media, CEO briefings, needs testing)
4. **Platinum** - 80% Complete (cloud deployment, PM2, health monitoring)

**Critical Updates:**
- ✅ Orchestrator now calls Claude API (was rule-based)
- ✅ Email MCP server now sends via Gmail API (was stub)
- ✅ Email search now works via Gmail API (was not implemented)
- ✅ Approval notifications via webhooks (Slack/Discord)

See [TIER_AUDIT.md](TIER_AUDIT.md) for detailed audit.

## Key Patterns

- **Human-in-the-Loop**: Sensitive actions require moving files to Approved/
- **Claim-by-Move**: First agent to claim an item owns it
- **Ralph Wiggum Loop**: Claude keeps working until task is complete
- **Parallel Processing**: Use Agent tool for concurrent task execution (NEW)
- **Interactive Approval**: AskUserQuestion with markdown preview for decisions (NEW)
- **Agent Teams**: Coordinate multiple Claude instances for complex multi-domain workflows (NEW)
- **Team Task Lists**: Shared task coordination with dependencies and ownership (NEW)
- **Quality Gates**: Automated validation before teammates go idle (NEW)

## Agent Skills (NEW)

Available skills in `.claude/commands/` and `skills/`:

| Skill | Purpose |
|-------|---------|
| `/process-emails` | Process emails from Needs_Action |
| `/process-whatsapp` | Process WhatsApp messages |
| `/create-plan` | Generate Plan.md for items |
| `/request-approval` | Create approval requests |
| `/execute-action` | Execute approved actions |
| `/generate-briefing` | Create CEO briefing |
| `/interactive-approval` | Real-time approval with preview (NEW) |
| `/parallel-process` | Concurrent processing (NEW) |

## Webhook Configuration

Configure external webhooks in `vault/secrets/webhooks.json`:

```json
{
  "webhooks": {
    "slack": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    "discord": "https://discord.com/api/webhooks/YOUR/WEBHOOK"
  }
}
```

Webhooks are triggered for:
- New approval requests
- Approval/rejection results
- Error notifications
