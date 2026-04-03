#!/bin/bash
# Health Check Script — Runs every hour
#
# Checks:
# - PM2 process health (orchestrator + watchers)
# - Disk space usage
# - Vault directory integrity
# - Recent activity in logs
# - Health server endpoint
#
# Cron: 0 * * * * /path/to/scripts/cron/health_check.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VAULT_PATH="${PROJECT_ROOT}/vault"
LOG_FILE="${PROJECT_ROOT}/logs/cron.log"
HEALTH_PORT="${HEALTH_PORT:-8080}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [health-check] Starting..." >> "$LOG_FILE" 2>/dev/null || true

ISSUES=0

# ---- Check 1: PM2 process health ----
if command -v pm2 &> /dev/null; then
    echo "[$(date '+%H:%M:%S')] Checking PM2 processes..." >> "$LOG_FILE"

    for service in ai-orchestrator gmail-watcher filesystem-watcher; do
        if pm2 list | grep -q "$service.*online" 2>/dev/null; then
            echo "[$(date '+%H:%M:%S')] ✅ $service: online" >> "$LOG_FILE"
        else
            echo "[$(date '+%H:%M:%S')] ❌ $service: NOT RUNNING" >> "$LOG_FILE"
            ISSUES=$((ISSUES + 1))

            # Auto-restart if PM2 is available
            pm2 restart "$service" >> "$LOG_FILE" 2>&1 || true
            echo "[$(date '+%H:%M:%S')] Attempted restart of $service" >> "$LOG_FILE"
        fi
    done
else
    echo "[$(date '+%H:%M:%S')] ⚠️ PM2 not installed — skipping process checks" >> "$LOG_FILE"
fi

# ---- Check 2: Health server endpoint ----
if command -v curl &> /dev/null; then
    HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${HEALTH_PORT}/health/status" 2>/dev/null || echo "000")
    if [ "$HEALTH_RESPONSE" = "200" ]; then
        echo "[$(date '+%H:%M:%S')] ✅ Health server: responding (HTTP $HEALTH_RESPONSE)" >> "$LOG_FILE"
    else
        echo "[$(date '+%H:%M:%S')] ⚠️ Health server: not responding (HTTP $HEALTH_RESPONSE)" >> "$LOG_FILE"
        ISSUES=$((ISSUES + 1))
    fi
fi

# ---- Check 3: Disk space ----
DISK_USAGE=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "[$(date '+%H:%M:%S')] ❌ Disk usage: ${DISK_USAGE}% (CRITICAL)" >> "$LOG_FILE"
    ISSUES=$((ISSUES + 1))
elif [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$(date '+%H:%M:%S')] ⚠️ Disk usage: ${DISK_USAGE}% (WARNING)" >> "$LOG_FILE"
else
    echo "[$(date '+%H:%M:%S')] ✅ Disk usage: ${DISK_USAGE}%" >> "$LOG_FILE"
fi

# ---- Check 4: Vault integrity ----
REQUIRED_DIRS="Needs_Action Plans Done Pending_Approval Approved Rejected Logs"
for dir in $REQUIRED_DIRS; do
    if [ -d "$VAULT_PATH/$dir" ]; then
        count=$(find "$VAULT_PATH/$dir" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
        echo "[$(date '+%H:%M:%S')] ✅ $dir: exists ($count files)" >> "$LOG_FILE"
    else
        echo "[$(date '+%H:%M:%S')] ❌ $dir: MISSING" >> "$LOG_FILE"
        ISSUES=$((ISSUES + 1))
    fi
done

# ---- Check 5: Recent activity ----
TODAY=$(date '+%Y-%m-%d')
if [ -f "$VAULT_PATH/Logs/${TODAY}.json" ]; then
    log_entries=$(python3 -c "import json; data=json.load(open('$VAULT_PATH/Logs/${TODAY}.json')); print(len(data))" 2>/dev/null || echo "0")
    echo "[$(date '+%H:%M:%S')] ✅ Today's log: $log_entries entries" >> "$LOG_FILE"
else
    echo "[$(date '+%H:%M:%S')] ℹ️ No log entries today yet" >> "$LOG_FILE"
fi

# ---- Summary ----
if [ "$ISSUES" -gt 0 ]; then
    echo "[$(date '+%H:%M:%S')] ⚠️ Health check complete: $ISSUES issue(s) found" >> "$LOG_FILE"
else
    echo "[$(date '+%H:%M:%S')] ✅ Health check complete: All OK" >> "$LOG_FILE"
fi

exit $ISSUES
