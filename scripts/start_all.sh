#!/bin/bash
# Start all Personal AI Employee services
# Orchestrator + Watchers + Hook Server

set -e

# Configuration
VAULT_PATH="${VAULT_PATH:-./vault}"
DRY_RUN="${DRY_RUN:-true}"
HOOK_PORT="${HOOK_PORT:-8081}"
ENABLE_HOOKS="${ENABLE_HOOKS:-true}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Personal AI Employee - Starting Up   ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    exit 1
fi

if ! command -v claude &> /dev/null; then
    echo -e "${YELLOW}Warning: Claude Code CLI not found in PATH${NC}"
    echo "Some features may not work"
fi

# Create required directories
echo -e "${BLUE}Setting up vault directories...${NC}"
mkdir -p "$VAULT_PATH"/{Needs_Action,Plans,Done,Pending_Approval,Approved,Rejected,Logs,Drafts,Briefings,Triggers,secrets}

# Create PID directory
PID_DIR="./run"
mkdir -p "$PID_DIR"

# Function to start a service
start_service() {
    local name=$1
    local command=$2
    local pid_file="$PID_DIR/${name}.pid"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}$name already running (PID: $pid)${NC}"
            return 0
        fi
        rm -f "$pid_file"
    fi

    echo -e "${BLUE}Starting $name...${NC}"
    $command &
    local pid=$!
    echo $pid > "$pid_file"
    echo -e "${GREEN}✓ $name started (PID: $pid)${NC}"
}

# Function to stop all services
stop_all() {
    echo -e "${YELLOW}Stopping all services...${NC}"
    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            local name=$(basename "$pid_file" .pid)
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid"
                echo -e "${GREEN}✓ Stopped $name${NC}"
            fi
            rm -f "$pid_file"
        fi
    done
}

# Handle shutdown
trap stop_all EXIT

# Start services
echo ""
echo -e "${BLUE}Starting services...${NC}"
echo ""

# 1. Orchestrator (main coordination)
start_service "orchestrator" \
    "python3 orchestrator.py --vault $VAULT_PATH ${DRY_RUN:+--dry-run}"

# 2. Hook Server (HTTP endpoints)
if [ "$ENABLE_HOOKS" = "true" ]; then
    start_service "hooks" \
        "python3 -c \"from hooks import run_server; run_server(port=$HOOK_PORT, vault_path='$VAULT_PATH')\""
fi

# 3. Gmail Watcher (if configured)
if [ -f "$VAULT_PATH/secrets/gmail_credentials.json" ]; then
    echo -e "${BLUE}Starting Gmail watcher...${NC}"
    start_service "gmail_watcher" \
        "python3 watchers/gmail_watcher.py --vault $VAULT_PATH --credentials $VAULT_PATH/secrets/gmail_credentials.json"
fi

# 4. File Watcher
start_service "file_watcher" \
    "python3 watchers/filesystem_watcher.py --vault $VAULT_PATH --watch-path ./drop"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All services started!                 ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Services running:"
echo "  - Orchestrator: Processing items from Needs_Action"
echo "  - Hook Server:  http://localhost:$HOOK_PORT"
if [ -f "$VAULT_PATH/secrets/gmail_credentials.json" ]; then
    echo "  - Gmail Watcher: Monitoring inbox"
fi
echo "  - File Watcher:  Watching ./drop"
echo ""
echo "To stop all services: kill \$(cat $PID_DIR/*.pid)"
echo "To view logs: tail -f $VAULT_PATH/Logs/*.log"
echo ""

# Keep script running to maintain services
echo -e "${BLUE}Press Ctrl+C to stop all services...${NC}"
wait