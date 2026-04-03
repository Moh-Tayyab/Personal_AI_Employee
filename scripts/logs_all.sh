#!/bin/bash
# Logs — Unified Log Viewing
#
# Shows logs from all sources:
# - PM2 process logs
# - Cron logs
# - Vault daily logs
# - Health server logs
#
# Usage:
#   ./scripts/logs_all.sh              # Tail all logs live
#   ./scripts/logs_all.sh --pm2        # PM2 logs only
#   ./scripts/logs_all.sh --cron       # Cron logs only
#   ./scripts/logs_all.sh --vault      # Vault daily logs
#   ./scripts/logs_all.sh --last 100   # Last N lines
#   ./scripts/logs_all.sh --grep error # Search for keyword

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VAULT_PATH="${PROJECT_ROOT}/vault"
HEALTH_PORT="${HEALTH_PORT:-8080}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse flags
SHOW_PM2=false
SHOW_CRON=false
SHOW_VAULT=false
SHOW_HEALTH=false
GREP_KEYWORD=""
LAST_LINES=""

# If no args, show all logs live
if [ $# -eq 0 ]; then
    SHOW_PM2=true
    SHOW_CRON=true
    SHOW_VAULT=true
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --pm2)        SHOW_PM2=true; shift ;;
        --cron)       SHOW_CRON=true; shift ;;
        --vault)      SHOW_VAULT=true; shift ;;
        --health)     SHOW_HEALTH=true; shift ;;
        --last)       LAST_LINES="$2"; shift 2 ;;
        --grep)       GREP_KEYWORD="$2"; shift 2 ;;
        --tail)       LAST_LINES="$2"; shift 2 ;;
        *)            echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Default to last 50 lines if not specified
if [ -z "$LAST_LINES" ]; then
    LAST_LINES="50"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Personal AI Employee — Logs${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ---- PM2 Logs ----
if [ "$SHOW_PM2" = true ]; then
    echo -e "${BLUE}── PM2 Logs (last $LAST_LINES lines) ──${NC}"
    if command -v pm2 &> /dev/null; then
        if [ -n "$GREP_KEYWORD" ]; then
            pm2 logs --nostream --lines "$LAST_LINES" 2>/dev/null | grep -i "$GREP_KEYWORD" || echo "  No matches"
        else
            pm2 logs --nostream --lines "$LAST_LINES" 2>/dev/null || echo "  No PM2 logs"
        fi
    elif [ -d "$PROJECT_ROOT/logs/pm2" ]; then
        for logfile in "$PROJECT_ROOT/logs/pm2"/*.log; do
            if [ -f "$logfile" ]; then
                echo ""
                echo -e "  ${YELLOW}$(basename "$logfile"):${NC}"
                if [ -n "$GREP_KEYWORD" ]; then
                    tail -"$LAST_LINES" "$logfile" | grep -i "$GREP_KEYWORD" || echo "    No matches"
                else
                    tail -"$LAST_LINES" "$logfile"
                fi
            fi
        done
    else
        echo -e "  ${YELLOW}PM2 logs not found${NC}"
    fi
    echo ""
fi

# ---- Cron Logs ----
if [ "$SHOW_CRON" = true ]; then
    echo -e "${BLUE}── Cron Logs (last $LAST_LINES lines) ──${NC}"
    if [ -f "$PROJECT_ROOT/logs/cron.log" ]; then
        if [ -n "$GREP_KEYWORD" ]; then
            tail -"$LAST_LINES" "$PROJECT_ROOT/logs/cron.log" | grep -i "$GREP_KEYWORD" || echo "  No matches"
        else
            tail -"$LAST_LINES" "$PROJECT_ROOT/logs/cron.log"
        fi
    else
        echo -e "  ${YELLOW}No cron log found${NC}"
    fi
    echo ""
fi

# ---- Vault Daily Logs ----
if [ "$SHOW_VAULT" = true ]; then
    echo -e "${BLUE}── Vault Daily Logs ──${NC}"
    TODAY=$(date '+%Y-%m-%d')
    YESTERDAY=$(date -d 'yesterday' '+%Y-%m-%d' 2>/dev/null || date -v-1d '+%Y-%m-%d' 2>/dev/null || echo "")

    for logdate in "$TODAY" "$YESTERDAY"; do
        if [ -n "$logdate" ] && [ -f "$VAULT_PATH/Logs/${logdate}.json" ]; then
            echo -e "${YELLOW}${logdate}.json:${NC}"
            if [ -n "$GREP_KEYWORD" ]; then
                python3 -c "
import json
data = json.load(open('$VAULT_PATH/Logs/${logdate}.json'))
for entry in data[-$LAST_LINES:]:
    text = json.dumps(entry).lower()
    if '$GREP_KEYWORD'.lower() in text:
        print(f'  [{entry.get(\"timestamp\", \"\")[:19]}] {entry.get(\"type\", \"\")}')
" 2>/dev/null || echo "  No matches"
            else
                python3 -c "
import json
data = json.load(open('$VAULT_PATH/Logs/${logdate}.json'))
for entry in data[-$LAST_LINES:]:
    print(f'  [{entry.get(\"timestamp\", \"\")[:19]}] {entry.get(\"type\", \"\")}')
" 2>/dev/null || echo "  Empty"
            fi
        fi
    done
    echo ""
fi

# ---- Health Server Logs ----
if [ "$SHOW_HEALTH" = true ]; then
    echo -e "${BLUE}── Health Server ──${NC}"
    HEALTH_RESPONSE=$(curl -s "http://127.0.0.1:${HEALTH_PORT}/health/status" 2>/dev/null || echo "")
    if [ -n "$HEALTH_RESPONSE" ]; then
        echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
    else
        echo -e "  ${YELLOW}Health server not responding${NC}"
    fi
    echo ""
fi

echo -e "${BLUE}========================================${NC}"
echo "For live tailing:"
echo "  tail -f logs/cron.log"
echo "  pm2 logs"
echo ""
echo "For searching:"
echo "  ./scripts/logs_all.sh --grep error"
echo "  ./scripts/logs_all.sh --pm2 --grep warning"
echo ""
