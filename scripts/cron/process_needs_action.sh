#!/bin/bash
# Process Needs_Action — Runs every 5 minutes
#
# Triggers the orchestrator to process any items in the Needs_Action folder.
# This is the main automation loop: Watcher → Needs_Action → AI → Done.
#
# Cron: */5 * * * * /path/to/scripts/cron/process_needs_action.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VAULT_PATH="${PROJECT_ROOT}/vault"
LOG_FILE="${PROJECT_ROOT}/logs/cron.log"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [process-needs-action] Starting..." >> "$LOG_FILE" 2>/dev/null || true

cd "$PROJECT_ROOT"

# Source environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

export VAULT_PATH="${VAULT_PATH}"
export DRY_RUN="true"

# Count items before processing
NEEDS_ACTION_COUNT=$(find "$VAULT_PATH/Needs_Action" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)

if [ "$NEEDS_ACTION_COUNT" -eq 0 ]; then
    echo "[$(date '+%H:%M:%S')] No items in Needs_Action — skipping" >> "$LOG_FILE"
    exit 0
fi

echo "[$(date '+%H:%M:%S')] Found $NEEDS_ACTION_COUNT item(s) in Needs_Action — processing..." >> "$LOG_FILE"

# Run the orchestrator for one cycle (it processes all items then exits)
# Using --dry-run by default; set DRY_RUN=false in .env for production
timeout 300 "$PYTHON" -c "
import sys, os, time
sys.path.insert(0, '.')
from orchestrator import Orchestrator

orch = Orchestrator(vault_path='$VAULT_PATH', dry_run=True)

# Run one orchestration cycle
needs_action = orch.check_needs_action()
if needs_action:
    print(f'Processing {len(needs_action)} item(s)...')
    for item in needs_action:
        # Create plan
        plan_path = orch.create_plan(item)

        # Trigger AI processing (in dry_run, this just logs)
        prompt = f'Process item: {item.name}. Read Company_Handbook.md for rules. Determine actions.'
        orch.trigger_ai(prompt)

        # Move to In_Progress
        orch.move_to_in_progress(item)
        print(f'  ✅ Processed: {item.name}')
else:
    print('No items to process')

# Check and execute approved items
approved = orch.check_approved()
if approved:
    print(f'Executing {len(approved)} approved item(s)...')
    for item in approved:
        success = orch.process_approved_item(item)
        if success:
            orch.move_to_done(item)
            print(f'  ✅ Executed: {item.name}')
        else:
            print(f'  ❌ Failed: {item.name}')
else:
    print('No approved items to execute')

# Update dashboard
orch._update_dashboard(needs_action, orch.check_pending_approval(), orch.check_approved())
print('Dashboard updated')
" 2>&1 | tee -a "$LOG_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [process-needs-action] Complete" >> "$LOG_FILE" 2>/dev/null || true
