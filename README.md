# Personal AI Employee

> Autonomous digital worker built with Qwen Code and an Obsidian vault. Monitors communication channels, processes tasks through AI reasoning, and executes actions via MCP servers — with human approval gates for sensitive operations.

## Current Status

- **Tier:** Gold (Autonomous Employee)
- **Validation Score:** ✅ 94% (48/51 checks passed)
- **AI Engine:** Groq (Llama 3.3 70B) + Gemini Fallback
- **Accounting:** Odoo Online (Connected, Invoicing Active)
- **Key Achievement:** Successfully created and posted $5,000 invoice autonomously.

See [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) for the full engineering analysis.

## Overview

The Personal AI Employee implements a **Digital Full-Time Equivalent (FTE)** — an autonomous agent system that:

- Monitors Gmail, WhatsApp, and filesystems for new items requiring attention
- Processes incoming tasks through AI reasoning with structured action plans
- Executes actions through MCP servers (email, social media, accounting)
- Requires human approval for sensitive actions (payments, outbound communication)
- Maintains a complete audit trail of all decisions and actions
- Generates weekly CEO briefings with revenue, bottlenecks, and suggestions

### Architecture

The system follows a four-layer design:

1. **Perception** — Python Watcher scripts poll external sources (Gmail API, WhatsApp Web, filesystem) and create action files in the vault
2. **Memory** — An Obsidian vault serves as the local-first knowledge base with structured folders for workflow state
3. **Reasoning** — The Orchestrator coordinates AI analysis (via Qwen Code or multi-provider fallback) with a Ralph Wiggum persistence loop for multi-step tasks
4. **Action** — Seven MCP servers expose 49 tools for external system integration (email, social media, accounting, file operations, approval workflows)

See [ARCHITECTURE.md](ARCHITECTURE.md) for the complete system design and [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) for daily operations.

## Quick Start

### Prerequisites

- Python 3.12+ with venv
- Node.js 18+ (for PM2 process management, optional)

### Installation

```bash
# Clone and set up the project
cd Personal_AI_Employee

# Create virtual environment and install dependencies
python3 -m venv .venv
.venv/bin/pip install -e .

# Copy and configure environment
cp .env.example .env
# Edit .env with your API credentials (see .env.example for required keys)
```

### Verify Installation

```bash
# Run the test suite
.venv/bin/python -m pytest tests/ -q

# Run a health check
./scripts/health_check.sh
```

### Running the System

```bash
# Start all services (PM2 required: npm install -g pm2)
./scripts/start_all.sh

# Or preview what would start without actually starting
./scripts/start_all.sh --dry-run

# Check service status
./scripts/status_all.sh

# Set up scheduled tasks (cron)
./scripts/setup_cron.sh --dry-run   # preview
./scripts/setup_cron.sh             # install
```

### Running Demos

```bash
# Silver Tier: email processing flow
./scripts/silver_tier_demo.sh

# Gold Tier: social media + accounting + CEO briefing
./scripts/gold_tier_demo.sh
```

All demos run in `DRY_RUN=true` mode by default — no real emails are sent, no posts are published, no invoices are created.

## Project Structure

```
Personal_AI_Employee/
├── vault/                          # Obsidian vault (local knowledge base)
│   ├── Dashboard.md                # Real-time system status
│   ├── Company_Handbook.md         # AI behavior rules and boundaries
│   ├── Business_Goals.md           # Objectives and KPIs
│   ├── Needs_Action/               # Items requiring AI attention
│   ├── In_Progress/                # Items being actively processed
│   ├── Pending_Approval/           # Items awaiting human decision
│   ├── Approved/                   # Human-approved, ready for execution
│   ├── Done/                       # Completed tasks (audit trail)
│   ├── Plans/                      # AI-generated action plans
│   ├── Logs/                       # Daily JSON audit logs
│   └── Briefings/                  # Weekly CEO reports
│
├── mcp/                            # MCP servers (7 servers, 49 tools)
│   ├── email/server.py             # Gmail: send, search, mark read (5 tools)
│   ├── filesystem/server.py        # Vault file operations (8 tools)
│   ├── approval/server.py          # Approval workflow management (7 tools)
│   ├── linkedin/server.py          # LinkedIn posting with images (5 tools)
│   ├── twitter/server.py           # Twitter/X posts and threads (6 tools)
│   ├── social/server.py            # Facebook/Instagram cross-platform (8 tools)
│   └── odoo/server.py              # Odoo accounting integration (10 tools)
│
├── watchers/                       # Perception layer
│   ├── base_watcher.py             # Abstract base class for all watchers
│   ├── gmail_watcher.py            # Gmail API polling
│   ├── whatsapp_watcher.py         # WhatsApp Web monitoring
│   └── filesystem_watcher.py       # Drop directory monitoring
│
├── scripts/                        # Operations and utilities
│   ├── start_all.sh                # Start services via PM2
│   ├── stop_all.sh                 # Stop services
│   ├── status_all.sh               # System status report
│   ├── reset_all.sh                # Clean state management
│   ├── logs_all.sh                 # Unified log viewing
│   ├── health_check.sh             # Comprehensive health validation
│   ├── setup_cron.sh               # Install scheduled cron tasks
│   ├── cron/                       # Scheduled task scripts
│   ├── orchestrator.py             # Main coordinator
│   ├── generate_ceo_briefing.py    # Weekly CEO briefing generator
│   ├── health_server.py            # HTTP health monitoring server
│   └── error_recovery_integration.py  # Circuit breaker decorators
│
├── tests/                          # Integration tests (272 tests)
├── ecosystem.config.js             # PM2 process definitions
├── orchestrator.py                 # Entry point
├── ARCHITECTURE.md                 # System architecture documentation
├── CHANGELOG.md                    # Implementation history
├── OPERATIONS_RUNBOOK.md           # Daily operations guide
└── README.md                       # This file
```

## MCP Server Capabilities

| Server | Tools | Key Capabilities |
|--------|-------|-----------------|
| **Email** | 5 | Send, search, retrieve, mark read, send from vault item |
| **Filesystem** | 8 | List, read, write, delete, move files, vault status |
| **Approval** | 7 | List pending, approve/reject, request info, statistics |
| **LinkedIn** | 5 | Post text, post with image, business updates, profile |
| **Twitter** | 6 | Post tweet, thread, timeline, search, business update |
| **Social** | 8 | Facebook post, Instagram post, cross-platform, insights |
| **Odoo** | 10 | Invoice CRUD, payments, customers, financial summary |

All servers support `DRY_RUN=true` (default) which returns what would happen without executing external actions. Set `DRY_RUN=false` in `.env` for live operation.

## Workflow

### Item Lifecycle

```
Needs_Action → Plan → AI Analysis → Pending_Approval → Approved → MCP Execution → Done
```

1. A Watcher detects a new item (email, message, file) and creates a markdown file in `Needs_Action/`
2. The Orchestrator picks it up, creates an action plan in `Plans/`
3. AI analyzes the item against the Company Handbook and Business Goals
4. If external action is needed, an approval request is created in `Pending_Approval/`
5. A human reviews and moves the file to `Approved/` (or `Rejected/`)
6. The Orchestrator executes the approved action through the appropriate MCP server
7. The item is moved to `Done/` with full audit logging

### Error Recovery

The system implements circuit breakers for each external service (Gmail, Odoo, LinkedIn, Twitter, Qwen API). After a configurable threshold of consecutive failures, the circuit opens and blocks further calls until a recovery timeout elapses. During outages, graceful degradation strategies queue actions locally for later processing.

Five error categories drive different handling strategies:

| Category | Detection | Handling |
|----------|-----------|----------|
| Transient | Timeouts, 503, rate limits | Retry with exponential backoff |
| Authentication | 401, 403, token expiry | Alert human, no retry |
| Data | Corrupt files, parse errors | Quarantine item, alert human |
| System | Disk full, crashes | Alert human, no retry |
| Logic | Everything else | Manual review |

## Scheduled Tasks

| Task | Frequency | Script |
|------|-----------|--------|
| Process Needs_Action | Every 5 minutes | `scripts/cron/process_needs_action.sh` |
| Daily Briefing | 8:00 AM | `scripts/cron/daily_briefing.sh` |
| Weekly CEO Briefing | Monday 7:00 AM | `scripts/cron/weekly_ceo_briefing.sh` |
| Health Check | Every hour | `scripts/cron/health_check.sh` |

Install with `./scripts/setup_cron.sh`. Preview with `./scripts/setup_cron.sh --dry-run`.

## Health Monitoring

The system runs an HTTP health server on `http://127.0.0.1:8080` with these endpoints:

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Basic liveness check |
| `GET /health/ready` | Readiness: orchestrator running, vault accessible, circuit breakers healthy |
| `GET /health/live` | Process alive check |
| `GET /health/status` | Full system status report (JSON) |
| `GET /health/watchers` | Watcher status summary |
| `GET /health/circuit-breakers` | Circuit breaker states |

For CLI validation, run `./scripts/health_check.sh` which checks 21 conditions across health server, vault integrity, disk space, Python environment, MCP server syntax, and log file integrity.

## Testing

```bash
# Run full test suite
.venv/bin/python -m pytest tests/ -v

# Run specific test group
.venv/bin/python -m pytest tests/test_integration.py -v
.venv/bin/python -m pytest tests/test_error_recovery_resilience.py -v

# Run with coverage
.venv/bin/python -m pytest tests/ --cov=.
```

**272 tests, 100% pass rate.** Test coverage includes watcher integration, all 49 MCP tools, end-to-end item lifecycles, Ralph Wiggum loop strategies, error recovery chains, and health server HTTP endpoints.

## Security

- **Local-first**: All data stays on your machine; only API calls leave the system
- **Dry-run default**: `DRY_RUN=true` prevents all external actions until explicitly disabled
- **Human-in-the-loop**: Sensitive actions (payments, outbound email, social posts) require manual approval
- **Secrets excluded**: `.env`, `credentials/`, and `vault/secrets/` are gitignored
- **Audit trail**: Every action is logged with timestamps, context, and outcomes

## Configuration

Edit `vault/Company_Handbook.md` to define AI behavior rules, and `vault/Business_Goals.md` to set objectives and KPI thresholds. The Orchestrator reads these files during item processing to determine appropriate actions.

See `.env.example` for all configurable environment variables.

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture, data flows, error recovery design
- [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) — Daily operations, troubleshooting, deployment
- [CHANGELOG.md](CHANGELOG.md) — Implementation history
- [AGENTS.md](AGENTS.md) — Technical specification
- [requirements.md](requirements.md) — Hackathon requirements and tier definitions

## License

MIT
