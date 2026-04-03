#!/bin/bash
# Status — Show AI Employee Service Status
#
# Displays:
# - PM2 service status (if PM2 is installed)
# - Health server status
# - Vault queue counts
# - Recent activity
#
# Usage: ./scripts/status_all.sh [--json]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VAULT_PATH="${PROJECT_ROOT}/vault"
HEALTH_PORT="${HEALTH_PORT:-8080}"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

JSON_MODE=false
if [[ "$1" == "--json" ]]; then JSON_MODE=true; fi

if [ "$JSON_MODE" = false ]; then
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Personal AI Employee — Status${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
fi

# ---- Section 1: PM2 Service Status ----
if [ "$JSON_MODE" = false ]; then
    echo -e "${BLUE}── Services (PM2) ──${NC}"
fi

if command -v pm2 &> /dev/null && [ -f "$PROJECT_ROOT/ecosystem.config.js" ]; then
    if [ "$JSON_MODE" = true ]; then
        echo '"pm2": ['
        pm2 jlist 2>/dev/null | python3 -c "
import json, sys
processes = json.load(sys.stdin)
for p in processes:
    name = p.get('name', '')
    status = p.get('pm2_env', {}).get('status', 'unknown')
    icon = '✅' if status == 'online' else '❌'
    print(f'  {icon} {name}: {status}')
"
        echo '],'
    else
        pm2 list 2>/dev/null || echo -e "  ${YELLOW}No PM2 processes found${NC}"
    fi
else
    if [ "$JSON_MODE" = false ]; then
        echo -e "  ${YELLOW}PM2 not installed or ecosystem.config.js missing${NC}"
    fi
fi

# ---- Section 2: Health Server ----
if [ "$JSON_MODE" = false ]; then
    echo ""
    echo -e "${BLUE}── Health Server ──${NC}"
fi

HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${HEALTH_PORT}/health/status" 2>/dev/null || echo "000")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    if [ "$JSON_MODE" = true ]; then
        echo '"health_server": "✅ online",'
    else
        echo -e "  ${GREEN}✅ Responding on port $HEALTH_PORT${NC}"
    fi
else
    if [ "$JSON_MODE" = true ]; then
        echo '"health_server": "❌ not responding",'
    else
        echo -e "  ${RED}❌ Not responding (HTTP $HEALTH_RESPONSE)${NC}"
    fi
fi

# ---- Section 3: Vault Queue Counts ----
if [ "$JSON_MODE" = false ]; then
    echo ""
    echo -e "${BLUE}── Vault Queues ──${NC}"
fi

for dir in Needs_Action In_Progress Pending_Approval Approved Done Plans Briefings; do
    if [ -d "$VAULT_PATH/$dir" ]; then
        count=$(find "$VAULT_PATH/$dir" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
        if [ "$count" -gt 0 ]; then
            if [ "$JSON_MODE" = true ]; then
                echo "\"$dir\": $count,"
            else
                printf "  %-20s %d file(s)\n" "$dir" "$count"
            fi
        fi
    fi
done

# ---- Section 4: Recent Activity ----
if [ "$JSON_MODE" = false ]; then
    echo ""
    echo -e "${BLUE}── Recent Activity ──${NC}"

    TODAY=$(date '+%Y-%m-%d')
    if [ -f "$VAULT_PATH/Logs/${TODAY}.json" ]; then
        log_count=$(python3 -c "import json; data=json.load(open('$VAULT_PATH/Logs/${TODAY}.json')); print(len(data))" 2>/dev/null || echo "0")
        echo -e "  Today's log entries: $log_count"

        # Show last 3 entries
        python3 -c "
import json
data = json.load(open('$VAULT_PATH/Logs/${TODAY}.json'))
for entry in data[-3:]:
    ts = entry.get('timestamp', '')[:19]
    t = entry.get('type', '')
    print(f'    [{ts}] {t}')
" 2>/dev/null || true
    else
        echo -e "  No log entries today"
    fi
fi

# ---- Section 5: Disk Usage ----
if [ "$JSON_MODE" = false ]; then
    echo ""
    echo -e "${BLUE}── System ──${NC}"

    DISK_USAGE=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $5}')
    echo -e "  Disk usage: $DISK_USAGE"

    # Python version
    if [ -f "$PYTHON" ]; then
        PY_VER=$("$PYTHON" --version 2>&1)
        echo -e "  Python: $PY_VER"
    fi

    # Node/PM2 version
    if command -v pm2 &> /dev/null; then
        PM2_VER=$(pm2 --version 2>/dev/null)
        echo -e "  PM2: v$PM2_VER"
    fi
fi

if [ "$JSON_MODE" = false ]; then
    echo ""
    echo -e "${BLUE}========================================${NC}"
fi
