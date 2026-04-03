#!/bin/bash
# Weekly CEO Briefing Script — Runs Monday at 7:00 AM
#
# Uses the generate_ceo_briefing.py script to create a comprehensive
# Monday Morning CEO Briefing with revenue, bottlenecks, and suggestions.
#
# Cron: 0 7 * * 1 /path/to/scripts/cron/weekly_ceo_briefing.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VAULT_PATH="${PROJECT_ROOT}/vault"
LOG_FILE="${PROJECT_ROOT}/logs/cron.log"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [weekly-ceo-briefing] Starting..." >> "$LOG_FILE" 2>/dev/null || true

cd "$PROJECT_ROOT"

# Source environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

export VAULT_PATH="${VAULT_PATH}"
export DRY_RUN="true"

# Generate CEO briefing using the dedicated script
"$PYTHON" scripts/generate_ceo_briefing.py --vault "$VAULT_PATH" --period 7 2>&1 | tee -a "$LOG_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [weekly-ceo-briefing] Complete" >> "$LOG_FILE" 2>/dev/null || true
