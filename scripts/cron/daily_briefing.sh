#!/bin/bash
# Daily Briefing Script — Runs at 8:00 AM
#
# Calls the orchestrator to generate a daily briefing by analyzing
# completed tasks, pending items, and business goals.
#
# Cron: 0 8 * * * /path/to/scripts/cron/daily_briefing.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VAULT_PATH="${PROJECT_ROOT}/vault"
LOG_FILE="${PROJECT_ROOT}/logs/cron.log"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"

# Log start
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [daily-briefing] Starting..." >> "$LOG_FILE" 2>/dev/null || true

cd "$PROJECT_ROOT"

# Source environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Export vault path for the Python script
export VAULT_PATH="${VAULT_PATH}"
export DRY_RUN="true"

# Generate daily briefing using the orchestrator's built-in capability
"$PYTHON" -c "
import sys, os
sys.path.insert(0, '.')
from orchestrator import Orchestrator
from datetime import datetime

orch = Orchestrator(vault_path='$VAULT_PATH', dry_run=True)
orch.generate_morning_briefing()
print(f'[{datetime.now().isoformat()}] Daily briefing complete')
" 2>&1 | tee -a "$LOG_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [daily-briefing] Complete" >> "$LOG_FILE" 2>/dev/null || true
