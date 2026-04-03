# Architecture Documentation — Personal AI Employee

## System Overview

The Personal AI Employee is an autonomous digital worker that monitors external sources, processes incoming items through AI reasoning, and executes actions via MCP servers — all while keeping a human in the loop for sensitive decisions.

### Design Principles

1. **Local-First**: All data stays on your machine; only API calls leave
2. **File-Based Communication**: Components communicate by moving markdown files between folders
3. **Dry-Run Default**: All external actions are simulated unless `DRY_RUN=false`
4. **Circuit Breakers**: Failing services are isolated to prevent cascading failures
5. **Audit Trail**: Every action is logged with timestamps and context

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                         │
│   Gmail API  │  WhatsApp Web  │  File System  │  Odoo ERP  │
│   LinkedIn   │  Twitter API   │  Meta Graph   │  Bank API  │
└────────┬────────────┬──────────────┬──────────────┬─────────┘
         │            │              │              │
         ▼            ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│  PERCEPTION LAYER — Watchers (Python scripts, 24/7)         │
│                                                             │
│  GmailWatcher ─── polls Gmail API every 120s               │
│  WhatsAppWatcher ─ polls WhatsApp Web every 30s            │
│  FilesystemWatcher ── watches drop/ directory (watchdog)   │
│                                                             │
│  All watchers follow BaseWatcher pattern:                  │
│  check_for_updates() → create_action_file() → log_action() │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ (creates .md files)
┌─────────────────────────────────────────────────────────────┐
│  MEMORY LAYER — Obsidian Vault (Local Markdown Database)    │
│                                                             │
│  /Needs_Action/     ← Items requiring AI attention          │
│  /In_Progress/      ← Items being processed by AI           │
│  /Pending_Approval/ ← Items awaiting human decision         │
│  /Approved/         ← Human-approved, ready for execution   │
│  /Done/             ← Completed tasks (audit trail)         │
│  /Rejected/         ← Rejected items                        │
│  /Plans/            ← AI-generated action plans             │
│  /Logs/             ← Daily JSON audit logs                 │
│  /Briefings/        ← CEO weekly reports                    │
│                                                             │
│  Dashboard.md       ← Real-time status (auto-updated)       │
│  Company_Handbook.md ← Rules of engagement                  │
│  Business_Goals.md  ← Objectives and KPIs                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ (reads files, writes plans)
┌─────────────────────────────────────────────────────────────┐
│  REASONING LAYER — Orchestrator + Qwen Code                 │
│                                                             │
│  Orchestrator (orchestrator.py):                           │
│  ├─ check_needs_action()      → finds new items            │
│  ├─ create_plan()             → generates action plan       │
│  ├─ trigger_ai()              → calls Qwen for analysis     │
│  ├─ process_approved_item()   → executes approved actions   │
│  ├─ move_to_in_progress()     → tracks active work          │
│  ├─ move_to_done()            → archives completed work     │
│  ├─ _update_dashboard()       → updates Dashboard.md        │
│  └─ run()                     → main loop (30s cycle)       │
│                                                             │
│  Multi-Provider AI System:                                  │
│  ├─ Gemini (Google) — general tasks                        │
│  ├─ Anthropic (Claude) — reasoning                         │
│  ├─ OpenRouter — fallback provider                         │
│  └─ Rule-based fallback — when all APIs fail               │
│                                                             │
│  Ralph Wiggum Loop:                                         │
│  Persistence pattern that keeps AI working until complete   │
│  Completion strategies: file movement, promise detection,   │
│  empty folder detection                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ (calls MCP servers)
┌─────────────────────────────────────────────────────────────┐
│  ACTION LAYER — MCP Servers (Model Context Protocol)        │
│                                                             │
│  7 MCP Servers, 49 Tools total:                            │
│                                                             │
│  Email MCP (5 tools):                                      │
│    send_email, search_emails, get_email,                   │
│    mark_email_as_read, send_email_from_vault               │
│                                                             │
│  Filesystem MCP (8 tools):                                 │
│    list_files, read_file, write_file, delete_file,          │
│    create_directory, file_exists, move_file, get_vault_status│
│                                                             │
│  Approval MCP (7 tools):                                   │
│    list_pending_approvals, get_approval_item, approve_item, │
│    reject_item, request_more_info, get_approval_stats,      │
│    move_to_pending_approval                                │
│                                                             │
│  LinkedIn MCP (5 tools):                                   │
│    linkedin_status, post_to_linkedin, post_business_update, │
│    post_with_image, get_linkedin_profile                   │
│                                                             │
│  Twitter MCP (6 tools):                                    │
│    twitter_status, post_tweet, post_thread, get_timeline,  │
│    search_tweets, post_business_update                     │
│                                                             │
│  Social MCP (8 tools):                                     │
│    social_status, post_to_facebook, post_to_instagram,      │
│    post_cross_platform, get_facebook_insights,             │
│    get_instagram_insights, list_pages, list_instagram_accounts│
│                                                             │
│  Odoo MCP (10 tools):                                      │
│    odoo_status, create_invoice, list_invoices,             │
│    post_invoice, create_payment, list_payments,            │
│    create_customer, list_customers, get_financial_summary, │
│    get_account_moves                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ (human approval gate)
┌─────────────────────────────────────────────────────────────┐
│  HUMAN-IN-THE-LOOP — Approval Workflow                      │
│                                                             │
│  1. AI creates approval request in /Pending_Approval/       │
│  2. Human reviews request (moves to Approved or Rejected)   │
│  3. If Approved → Orchestrator executes via MCP             │
│  4. If Rejected → Item logged, skipped                      │
│  5. All decisions logged to /Logs/                          │
│                                                             │
│  Approval thresholds (configurable in .env):               │
│  - Payments: >$50 require approval                          │
│  - New contacts: require approval                           │
│  - Social posts: require approval                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Error Recovery & Resilience

### Circuit Breaker Pattern

Each external service has a circuit breaker that opens after repeated failures:

| Service | Failure Threshold | Recovery Timeout |
|---------|------------------|------------------|
| Qwen API | 5 failures | 60 seconds |
| Gmail | 3 failures | 30 seconds |
| Odoo | 5 failures | 60 seconds |
| LinkedIn | 3 failures | 30 seconds |
| Twitter | 3 failures | 30 seconds |
| Facebook | 3 failures | 30 seconds |

**States**: `closed` (healthy) → `open` (blocking) → `half-open` (testing)

### Error Categorization

| Category | Detection | Handling |
|----------|-----------|----------|
| **Transient** | timeout, 503, rate limit | Retry with exponential backoff |
| **Authentication** | 401, 403, token expired | Alert human, no retry |
| **Data** | corrupt, invalid, parse error | Quarantine item, alert human |
| **System** | disk full, crash, segfault | Alert human, no retry |
| **Logic** | Everything else | Manual review required |

### Graceful Degradation

When a service fails, the system degrades gracefully:

- **Odoo down** → Queue accounting actions locally
- **Gmail down** → Queue emails locally
- **LinkedIn/Twitter down** → Save drafts locally
- **Qwen API down** → Use rule-based fallback processing

---

## Health Monitoring

### Health Server (HTTP API)

Runs on `http://127.0.0.1:8080` with endpoints:

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /health` | Basic liveness | `{"status": "healthy"}` |
| `GET /health/ready` | Readiness check | Checks orchestrator, vault, circuit breakers |
| `GET /health/live` | Process alive check | `{"status": "alive"}` |
| `GET /health/status` | Full system status | Complete JSON report |
| `GET /health/watchers` | Watcher status | Watcher states |
| `GET /health/circuit-breakers` | Circuit breaker states | All breaker states |

### Health Check Script

`scripts/health_check.sh` validates:
- Health server responds with valid JSON
- All 9 vault directories exist
- No stale In_Progress items (>24h)
- Disk space under 90%
- Python environment intact
- All 7 MCP server scripts syntax-valid
- Log file integrity (valid JSON)

---

## Scheduling & Operations

### Cron Schedule

| Task | Schedule | Script |
|------|----------|--------|
| Process Needs_Action | Every 5 minutes | `scripts/cron/process_needs_action.sh` |
| Daily Briefing | 8:00 AM daily | `scripts/cron/daily_briefing.sh` |
| Weekly CEO Briefing | Monday 7:00 AM | `scripts/cron/weekly_ceo_briefing.sh` |
| Health Check | Every hour | `scripts/cron/health_check.sh` |

### Operations Scripts

| Script | Purpose | Key Flags |
|--------|---------|-----------|
| `start_all.sh` | Start all services | `--dry-run`, `--no-pm2` |
| `stop_all.sh` | Stop all services | `--force` |
| `status_all.sh` | System status | `--json` |
| `reset_all.sh` | Clean state | `--all`, `--dry-run` |
| `logs_all.sh` | Unified log viewing | `--pm2`, `--cron`, `--vault`, `--grep` |
| `health_check.sh` | Health validation | `--strict`, `--json` |
| `setup_cron.sh` | Install cron jobs | `--remove`, `--dry-run` |

### PM2 Process Management

`ecosystem.config.js` manages 3 persistent services:
- **ai-orchestrator** (500MB max, 10s kill timeout)
- **gmail-watcher** (300MB max, 5s restart delay)
- **filesystem-watcher** (300MB max, 5s restart delay)

---

## Data Flow Examples

### Email Processing Flow

```
Gmail API → GmailWatcher → Needs_Action/EMAIL_001.md
    ↓
Orchestrator detects new item
    ↓
create_plan() → Plans/PLAN_001.md
    ↓
trigger_ai() → Qwen analyzes email
    ↓
Qwen determines: "Reply needed, requires approval"
    ↓
Pending_Approval/APPROVAL_001.md created
    ↓
Human reviews → moves to Approved/
    ↓
Orchestrator executes: process_approved_item()
    ↓
Email MCP → send_email(to, subject, body)
    ↓
Move to Done/ + log action
```

### Social Media Posting Flow

```
Human or AI creates post content
    ↓
Approved/SOCIAL_linkedin_001.md created
    ↓
Orchestrator detects approved item
    ↓
process_approved_item() → routes to LinkedIn MCP
    ↓
LinkedIn MCP → post_to_linkedin(content, visibility)
    ↓
If DRY_RUN=true → returns preview only
If DRY_RUN=false → posts to LinkedIn API
    ↓
Move to Done/ + log post details
```

### Error Recovery Flow

```
API call fails (e.g., Odoo connection timeout)
    ↓
Circuit breaker records failure
    ↓
If failures >= threshold → breaker opens
    ↓
Subsequent calls blocked immediately
    ↓
After recovery_timeout → breaker half-opens
    ↓
One test call allowed
    ↓
If success → breaker closes (recovered)
If failure → breaker opens again
    ↓
Meanwhile: graceful_degradation() queues action locally
```

---

## Security Model

### Secrets Management

```
.env                    ← API keys (NEVER committed)
vault/secrets/          ← OAuth tokens, banking creds
.gitignore              ← Excludes .env, secrets/, tokens
```

### Vault Sync Safety (Platinum Tier)

```
Cloud agent writes to: /Needs_Action/cloud/
Local agent writes to: /Needs_Action/local/
Shared via Git:        All .md files
NEVER synced:          .env, secrets/, tokens, WhatsApp sessions
```

### Human-in-the-Loop Guarantees

1. **No external actions without approval** (in DRY_RUN mode)
2. **All sensitive actions logged** (payment, email, social posts)
3. **Audit trail preserved** (Logs/ directory, never deleted)
4. **Quarantine for data corruption** (isolates bad items)

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Reasoning** | Qwen Code | AI analysis and planning |
| **Memory/GUI** | Obsidian | Local Markdown database |
| **Watchers** | Python 3.13+ | External source monitoring |
| **Action** | MCP Servers | External system integration |
| **Orchestration** | Python orchestrator | Coordination and workflow |
| **Process Mgmt** | PM2 | 24/7 service management |
| **Scheduling** | Cron | Periodic task execution |
| **Health** | HTTP server | Monitoring endpoints |
| **Testing** | pytest | 272 integration tests |

---

## Key Patterns

### Claim-by-Move

First agent to move an item from `Needs_Action/` to `In_Progress/` owns it. Other agents must ignore it.

### Single-Writer

Only the Local orchestrator writes to `Dashboard.md`. Cloud agents write to `Updates/` for Local to merge.

### Approval File

Sensitive actions create markdown files in `Pending_Approval/` requiring manual move to `Approved/` before execution.

### Ralph Wiggum Loop

Stop hook pattern that intercepts Qwen's exit and re-injects the prompt if the task is not marked complete.

---

*Architecture documented for Personal AI Employee Hackathon 2026*