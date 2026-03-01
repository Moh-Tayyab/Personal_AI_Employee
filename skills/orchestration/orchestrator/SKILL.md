---
name: orchestrator
description: |
  Central coordination process that manages watchers, triggers skills,
  handles the Ralph loop, and maintains overall system health. Acts as
  the master controller for the AI Employee's autonomous operation.
allowed-tools: [Read, Write, Glob, Grep, Edit, Bash]
---

# Orchestrator - Professional Skill

Master coordination process that manages all AI Employee components, triggers processing cycles, and ensures system reliability.

## When to Use

- System startup: Initialize all watchers and processes
- Scheduled intervals: Check for work and trigger processing
- User command: `/orchestrator start|stop|status`
- Automatic: Run as a daemon process

## Before Implementation

| Source | Gather |
|--------|--------|
| **mcp_config.json** | Available MCP servers |
| **Company_Handbook.md** | Operating rules, schedules |
| **Dashboard.md** | Current system state |
| **.orchestrator_state.json** | Previous state, recovery info |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Watcher    │  │   Watcher    │  │   Watcher    │       │
│  │   Manager    │  │   Manager    │  │   Manager    │       │
│  │  (Gmail)     │  │ (WhatsApp)   │  │ (Filesystem) │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
│         └─────────────────┼─────────────────┘                │
│                           │                                  │
│                           ▼                                  │
│                   ┌───────────────┐                          │
│                   │  Needs_Action │                          │
│                   │    Folder     │                          │
│                   └───────┬───────┘                          │
│                           │                                  │
│                           ▼                                  │
│                  ┌────────────────┐                          │
│                  │  Ralph Loop    │                          │
│                  │  Processing    │                          │
│                  └────────┬───────┘                          │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐                │
│         │                 │                 │                │
│         ▼                 ▼                 ▼                │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐           │
│  │  Process   │   │  Process   │   │  Process   │           │
│  │   Email    │   │  WhatsApp  │   │   Other    │           │
│  └─────┬──────┘   └─────┬──────┘   └─────┬──────┘           │
│        │                │                │                   │
│        └────────────────┼────────────────┘                   │
│                         │                                    │
│                         ▼                                    │
│               ┌─────────────────┐                            │
│               │  Execute Action │                            │
│               │   (via MCP)     │                            │
│               └────────┬────────┘                            │
│                        │                                     │
│                        ▼                                     │
│                ┌──────────────┐                              │
│                │    Done      │                              │
│                │   Folder     │                              │
│                └──────────────┘                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Health Monitor                      │   │
│  │  - Watcher status   - Error recovery                 │   │
│  │  - Process health   - Alert system                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Workflow

### Phase 1: Initialization

```yaml
startup_sequence:
  1. Load configuration
     - Read mcp_config.json
     - Read Company_Handbook.md
     - Read schedule configuration

  2. Initialize watchers
     - Start Gmail watcher
     - Start WhatsApp watcher
     - Start filesystem watcher

  3. Initialize MCP connections
     - Connect to email MCP
     - Connect to browser MCP
     - Test connections

  4. Restore state
     - Load .orchestrator_state.json
     - Check for incomplete tasks
     - Resume interrupted operations

  5. Start health monitor
     - Begin process monitoring
     - Start alert system
```

### Phase 2: Main Loop

```python
def main_loop():
    while running:
        # 1. Check for new items
        items = scan_needs_action()

        # 2. If items exist, start Ralph loop
        if items:
            start_ralph_loop("Process items in Needs_Action")

        # 3. Check scheduled tasks
        check_scheduled_tasks()

        # 4. Health check
        check_watcher_health()
        check_mcp_connections()

        # 5. Update dashboard
        update_dashboard()

        # 6. Wait for next cycle
        sleep(config['poll_interval'])
```

### Phase 3: Processing Cycle

```yaml
processing_cycle:
  trigger:
    - new_items_detected
    - scheduled_time
    - manual_request

  steps:
    - scan_needs_action
    - prioritize_items
    - start_ralph_loop
    - monitor_progress
    - handle_completion
```

## Configuration

```yaml
# vault/.config/orchestrator.yaml

orchestrator:
  # Main loop settings
  poll_interval: 60  # seconds
  max_concurrent_tasks: 5

  # Watcher management
  watchers:
    gmail:
      enabled: true
      script: scripts/gmail_watcher.py
      restart_on_failure: true
      max_restarts: 3

    whatsapp:
      enabled: true
      script: scripts/whatsapp_watcher.py
      restart_on_failure: true

    filesystem:
      enabled: true
      script: scripts/filesystem_watcher.py
      watch_paths:
        - drop/
        - inbox/

  # Ralph loop settings
  ralph_loop:
    max_iterations: 10
    iteration_timeout: 300
    completion_check: "folder_empty:Needs_Action"

  # Health monitoring
  health:
    check_interval: 60
    alert_on_failure: true
    auto_restart: true
    max_restart_attempts: 3

  # Scheduling
  schedule:
    ceo_briefing:
      time: "07:00"
      days: [monday]

    subscription_audit:
      time: "09:00"
      days: [1]  # First of month

    cleanup:
      time: "02:00"
      days: [sunday]

  # MCP configuration
  mcp_servers:
    email:
      enabled: true
      command: "node mcp/email/server.js"
      env:
        GMAIL_CREDENTIALS: ".credentials/gmail_credentials.json"

    browser:
      enabled: true
      command: "npx @anthropic/browser-mcp"

  # Logging
  logging:
    level: INFO
    file: Logs/orchestrator.log
    max_size: 10MB
    backup_count: 5
```

## Process Management

### Watcher Management

```python
class WatcherManager:
    def __init__(self, config):
        self.watchers = {}
        self.config = config

    def start_all(self):
        for name, watcher_config in self.config['watchers'].items():
            if watcher_config['enabled']:
                self.start_watcher(name, watcher_config)

    def start_watcher(self, name, config):
        process = subprocess.Popen(
            ['python', config['script']],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.watchers[name] = {
            'process': process,
            'config': config,
            'restarts': 0,
            'started_at': datetime.now()
        }

    def check_health(self):
        for name, watcher in self.watchers.items():
            if watcher['process'].poll() is not None:
                # Process has exited
                self.handle_watcher_failure(name, watcher)

    def handle_watcher_failure(self, name, watcher):
        if watcher['restarts'] < watcher['config'].get('max_restarts', 3):
            self.restart_watcher(name)
        else:
            self.alert(f"Watcher {name} failed after max restarts")
```

### Ralph Loop Integration

```python
class Orchestrator:
    def start_ralph_loop(self, task):
        state = {
            'loop_id': f"RALPH_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'task': task,
            'max_iterations': self.config['ralph_loop']['max_iterations'],
            'current_iteration': 0,
            'status': 'starting'
        }

        self.save_state(state)

        # Start Claude Code with Ralph loop
        result = self.run_claude_with_ralph_loop(task)

        return result

    def run_claude_with_ralph_loop(self, task):
        # This would integrate with Claude Code's stop hook
        # The actual implementation depends on how Claude Code is invoked
        pass
```

### Scheduled Tasks

```python
class Scheduler:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.scheduled_tasks = []

    def check_scheduled_tasks(self):
        now = datetime.now()

        for task in self.scheduled_tasks:
            if task.should_run(now):
                self.run_scheduled_task(task)

    def run_scheduled_task(self, task):
        if task.name == 'ceo_briefing':
            self.orchestrator.generate_briefing()
        elif task.name == 'subscription_audit':
            self.orchestrator.run_subscription_audit()
        elif task.name == 'cleanup':
            self.orchestrator.run_cleanup()
```

## Health Monitoring

### Health Checks

```python
class HealthMonitor:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.health_status = {}

    def check_all(self):
        return {
            'watchers': self.check_watchers(),
            'mcp_servers': self.check_mcp_servers(),
            'vault': self.check_vault(),
            'processes': self.check_processes(),
            'memory': self.check_memory(),
            'disk': self.check_disk()
        }

    def check_watchers(self):
        status = {}
        for name, watcher in self.orchestrator.watchers.items():
            status[name] = {
                'running': watcher['process'].poll() is None,
                'uptime': datetime.now() - watcher['started_at'],
                'restarts': watcher['restarts']
            }
        return status

    def check_mcp_servers(self):
        status = {}
        for name, server in self.orchestrator.mcp_servers.items():
            try:
                # Test MCP connection
                server.ping()
                status[name] = {'status': 'healthy'}
            except Exception as e:
                status[name] = {'status': 'error', 'message': str(e)}
        return status
```

### Alerting

```python
class AlertSystem:
    def __init__(self, config):
        self.config = config

    def send_alert(self, level, message, details=None):
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level,  # info, warning, error, critical
            'message': message,
            'details': details
        }

        # Log alert
        self.log_alert(alert)

        # Update dashboard
        self.update_dashboard_alert(alert)

        # Notify human (if critical)
        if level in ['error', 'critical']:
            self.notify_human(alert)

    def notify_human(self, alert):
        # Create urgent item in Needs_Action
        self.create_alert_file(alert)

        # Update dashboard with alert banner
        self.update_dashboard_alert(alert)
```

## State Management

### State File Format

```json
{
  "orchestrator_id": "ORCH_20260301_100000",
  "started_at": "2026-03-01T10:00:00Z",
  "status": "running",
  "current_cycle": {
    "started_at": "2026-03-01T10:05:00Z",
    "items_processed": 5,
    "current_task": "Processing EMAIL_client.md"
  },
  "watchers": {
    "gmail": {
      "status": "running",
      "last_check": "2026-03-01T10:04:30Z",
      "messages_processed": 12
    },
    "whatsapp": {
      "status": "running",
      "last_check": "2026-03-01T10:04:30Z",
      "messages_processed": 3
    }
  },
  "ralph_loop": {
    "active": false,
    "last_completed": "2026-03-01T09:45:00Z",
    "total_iterations": 3
  },
  "health": {
    "last_check": "2026-03-01T10:04:00Z",
    "status": "healthy"
  }
}
```

## CLI Commands

```bash
# Start orchestrator
python orchestrator.py start

# Stop orchestrator
python orchestrator.py stop

# Check status
python orchestrator.py status

# Process once (single cycle)
python orchestrator.py --once

# Dry run (no actual execution)
python orchestrator.py --dry-run

# Start specific watcher
python orchestrator.py start-watcher gmail

# Check health
python orchestrator.py health

# Generate briefing
python orchestrator.py briefing
```

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| State File | `.orchestrator_state.json` | Recovery and status |
| Orchestrator Log | `Logs/orchestrator.log` | Debugging and audit |
| Health Report | `Logs/health.json` | System health |
| Dashboard | `Dashboard.md` | User-facing status |

## References

| File | Purpose |
|------|---------|
| `references/process-management.md` | Process lifecycle details |
| `references/scheduling.md` | Task scheduling configuration |
| `references/recovery.md` | State recovery procedures |