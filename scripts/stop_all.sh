#!/bin/bash
# Stop All AI Employee Services
#
# Stops all watchers and the orchestrator running under PM2.
# Gracefully handles missing PM2 by killing processes directly.
#
# Usage: ./scripts/stop_all.sh [--force]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Personal AI Employee - Stop All${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

FORCE=false
if [[ "$1" == "--force" ]]; then FORCE=true; fi

# ---- PM2 Mode ----
if command -v pm2 &> /dev/null; then
    if [ -f "ecosystem.config.js" ]; then
        echo "Stopping all services via PM2..."
        pm2 stop ecosystem.config.js 2>/dev/null || true

        if [ "$FORCE" = true ]; then
            echo "Force deleting PM2 processes..."
            pm2 delete ecosystem.config.js 2>/dev/null || true
        fi

        echo ""
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}  Service Status${NC}"
        echo -e "${BLUE}========================================${NC}"
        pm2 list
    else
        echo -e "${YELLOW}ecosystem.config.js not found — nothing to stop via PM2${NC}"
    fi
else
    echo -e "${YELLOW}PM2 not installed — attempting direct process kill...${NC}"

    # Kill orchestrator and watchers by process name
    for proc in "orchestrator.py" "gmail_watcher.py" "filesystem_watcher.py" "whatsapp_watcher.py"; do
        pids=$(pgrep -f "$proc" 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo "Killing $proc (PIDs: $pids)..."
            echo "$pids" | xargs kill -TERM 2>/dev/null || true
            sleep 1
            # Force kill if still running
            if pgrep -f "$proc" > /dev/null 2>&1; then
                echo "Force killing $proc..."
                pgrep -f "$proc" | xargs kill -9 2>/dev/null || true
            fi
        else
            echo "  $proc: not running"
        fi
    done
fi

echo ""
echo -e "${GREEN}✓ All services stopped.${NC}"
echo ""
echo "To restart:"
echo "  ./scripts/start_all.sh"
echo ""

