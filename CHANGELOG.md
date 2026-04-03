# Changelog — Personal AI Employee

All notable changes to this project.

## [Unreleased] — Hackathon Implementation (Steps 1-6)

### Step 1: MCP Server Hardening (49 tools across 7 servers)

#### Added
- `oauthlib` and `requests-oauthlib` dependencies for Twitter OAuth 1.0a
- `send_email_from_vault` tool in Email MCP — parses YAML frontmatter, sends emails
- `post_with_image` tool in LinkedIn MCP — 3-step upload flow (register → upload → share)
- `post_invoice` tool in Odoo MCP — confirm and post draft invoices
- Unified `dry_run` mode across ALL MCP servers (Email, LinkedIn, Twitter, Facebook, Instagram, Odoo)
- Auto-adapt content to platform char limits (Twitter 280, LinkedIn 3000, Instagram 2200)

#### Fixed
- Odoo MCP authentication — switched from direct API key to proper session-based login (`common.login` → uid → `execute_kw`)
- Email MCP — skips Gmail auth in dry_run mode, returns dry_run success without blocking
- LinkedIn MCP — dry_run works even without token configured
- Twitter MCP — dry_run works for `post_tweet`, `post_thread`, `post_business_update`
- Social MCP — dry_run works for Facebook and Instagram without token configured
- pyproject.toml — added `[tool.hatch.build.targets.wheel]` with correct package dirs

### Step 2: Orchestrator Flow Completion

#### Added
- `process_approved_item()` — routes to 6 handlers covering all MCP servers:
  - `send_email` → Email MCP
  - `linkedin_post` → LinkedIn MCP
  - `twitter_post` → Twitter MCP
  - `social_post` → Social MCP (Facebook/Instagram)
  - `odoo_invoice` → Odoo MCP (create + post)
  - `odoo_payment` → Odoo MCP
- `_call_mcp_server()` — dynamically imports MCP modules and calls tool functions
- `_extract_frontmatter_field()` — regex-based YAML frontmatter parsing
- `_update_dashboard()` — auto-updates Dashboard.md every orchestration cycle
- `In_Progress/` directory — created in orchestrator init
- Action type inference from content when frontmatter missing

#### Fixed
- Item lifecycle: items now moved to In_Progress AFTER triggering AI (not before)
- `_handle_email_action` — extracts frontmatter fields, calls Email MCP
- `_handle_linkedin_action` — supports text and image posts
- `_handle_twitter_action` — respects 280 char limit
- `_handle_social_action` — auto-routes to Facebook or Instagram with char limits
- `_handle_odoo_invoice_action` — parses invoice lines from content
- `_handle_odoo_payment_action` — creates payment via Odoo MCP

### Step 3: Scheduled Operations

#### Added
- `ecosystem.config.js` — PM2 process manager for orchestrator + 3 watchers
- `scripts/cron/daily_briefing.sh` — calls orchestrator at 8:00 AM
- `scripts/cron/weekly_ceo_briefing.sh` — calls CEO briefing generator Monday 7:00 AM
- `scripts/cron/health_check.sh` — checks PM2, disk, vault, logs every hour
- `scripts/cron/process_needs_action.sh` — main automation loop every 5 minutes
- `scripts/silver_tier_demo.sh` — end-to-end demo: file → plan → approval → email → done
- `scripts/gold_tier_demo.sh` — full demo: social posts + odoo + CEO briefing

#### Fixed
- `setup_cron.sh` — rewritten to use orchestrator (not raw `qwen` CLI), added `--dry-run` and `--remove`
- `start_all.sh` — added `--dry-run`, `--no-pm2` flags, auto-creates `.env`, validates prerequisites
- `stop_all.sh` — added `--force` flag, graceful degradation without PM2 (direct process kill)

### Step 4: Integration Tests

#### Added
- `tests/test_integration.py` — 45 new integration tests:
  - Gmail Watcher (mocked API, action file creation, processed ID tracking)
  - Filesystem Watcher (drop directory, directory ignore)
  - Email MCP (dry_run send, vault frontmatter parsing)
  - Social MCP (7 tests: LinkedIn, Twitter, Facebook, Instagram, Cross-platform)
  - Odoo MCP (4 tests: create invoice, post invoice, create payment, create customer)
  - End-to-End Flow (5 tests: email, social, odoo lifecycles, dashboard, logging)
  - Ralph Wiggum Loop (6 tests: strategies, file movement, promise, empty folder, iterations, logging)
  - Orchestrator Error Handling (6 tests: fallback, unknown actions, missing files, MCP errors, signals)
  - Cron Script Validation (4 tests: existence, shebang, ecosystem config, demo scripts)

#### Fixed
- `test_approval_server.py` — assertion corrected from `list` to `dict` with proper keys

### Step 5: Startup/Shutdown Scripts

#### Added
- `scripts/status_all.sh` — service status + health + queue counts + recent activity
- `scripts/reset_all.sh` — clean state management (In_Progress → Needs_Action, old log cleanup)
- `scripts/logs_all.sh` — unified log viewing (PM2, cron, vault, health) with `--grep` search
- `scripts/health_check.sh` — comprehensive health validation (21 checks across 7 categories)
- `OPERATIONS_RUNBOOK.md` — complete operations reference (daily checks, troubleshooting, deployment)

#### Fixed
- All script paths corrected from `SCRIPT_DIR/../..` to `SCRIPT_DIR/..`

### Step 6: Error Recovery & Resilience

#### Added
- `tests/test_error_recovery_resilience.py` — 36 new tests:
  - ErrorRecoverySystem (13 tests): categorization, handling, logging, circuit breakers, stats
  - Graceful Degradation (6 tests): Odoo, Gmail, LinkedIn, Twitter, Qwen fallback strategies
  - Retry Handler (4 tests): exponential backoff, max attempts, non-transient no-retry
  - Orchestrator → Health Server (6 tests): state updates, HTTP endpoints
  - Error Recovery Chain (4 tests): transient retry, auth no-retry, system no-retry, quarantine
  - Health Check Script (2 tests): existence and execution validation

#### Fixed
- `scripts/error_recovery.py` — added `'segfault'` to system error keyword list
- Health server endpoint tests — ensure orchestrator is set running before HTTP check
- Transient error retry test — use proper `TransientError` exception class

### Test Suite Summary

| Step | Tests Before | Tests After | Status |
|------|-------------|-------------|--------|
| Step 1 | 195 | 195 | ✅ |
| Step 2 | 195 | 216 | ✅ (+21) |
| Step 3 | 216 | 216 | ✅ |
| Step 4 | 216 | 236 | ✅ (+20 + 1 fix) |
| Step 5 | 236 | 236 | ✅ |
| Step 6 | 236 | **272** | ✅ (+36) |

**Final: 272 passed, 0 failed, 1 warning**

---

## [0.1.0] — Initial Project Setup

- Obsidian vault structure with Dashboard, Handbook, Business Goals
- Base Watcher with Gmail, WhatsApp, FileSystem implementations
- 7 MCP server skeletons (Email, Filesystem, Approval, LinkedIn, Twitter, Social, Odoo)
- Orchestrator with multi-provider AI and multi-CLI routing
- Ralph Wiggum loop script
- CEO Briefing generator
- Error recovery and circuit breakers
- Health server
- Agent teams manager
- Quota management
- Config validator
