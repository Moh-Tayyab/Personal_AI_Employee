#!/bin/bash
# Start All AI Employee Services
#
# Starts the orchestrator and all watchers using PM2 for 24/7 operation
# with automatic restart on failure.
#
# Usage: ./scripts/start_all.sh [--dry-run] [--no-pm2]

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
echo -e "${BLUE}  Personal AI Employee - Start All${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Parse flags
DRY_RUN=false
NO_PM2=false
if [[ "$1" == "--dry-run" ]]; then DRY_RUN=true; fi
if [[ "$1" == "--no-pm2" ]] || [[ "$2" == "--no-pm2" ]]; then NO_PM2=true; fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit .env with your API credentials before starting.${NC}"
    else
        echo -e "${RED}Error: .env.example not found. Create a .env file first.${NC}"
        exit 1
    fi
fi

# Check Python
if [ ! -f ".venv/bin/python" ]; then
    echo -e "${RED}Error: .venv/bin/python not found. Run: uv venv && uv pip install -e .${NC}"
    exit 1
fi
PYTHON_VERSION=$(.venv/bin/python --version 2>&1)
echo -e "${GREEN}✓ Python: $PYTHON_VERSION${NC}"

# Check vault
if [ ! -d "vault" ]; then
    echo -e "${RED}Error: vault/ directory not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Vault directory found${NC}"

# Ensure directories exist
mkdir -p logs/pm2 drop vault/Needs_Action vault/Plans vault/Done vault/Pending_Approval vault/Approved vault/Rejected vault/Logs vault/In_Progress

# ---- PM2 Mode ----
if [ "$NO_PM2" = false ]; then
    if ! command -v pm2 &> /dev/null; then
        echo -e "${YELLOW}PM2 not installed. Install with: npm install -g pm2${NC}"
        echo -e "${YELLOW}Falling back to --no-pm2 mode (direct process mode)...${NC}"
        NO_PM2=true
    fi
fi

# ---- Dry Run Check ----
if [ "$DRY_RUN" = true ]; then
    echo ""
    echo -e "${YELLOW}DRY RUN — showing what would be started${NC}"
    echo ""
    echo "Services that would start:"
    echo "  - ai-orchestrator  (orchestrator.py --vault ./vault)"
    echo "  - gmail-watcher    (watchers/gmail_watcher.py --vault ./vault)"
    echo "  - filesystem-watcher (watchers/filesystem_watcher.py --vault ./vault --drop-dir ./drop)"
    echo ""
    echo "Configuration:"
    echo "  - PM2 ecosystem: ecosystem.config.js"
    echo "  - Environment: .env"
    echo "  - Log directory: logs/pm2/"
    echo ""
    echo "To actually start services:"
    echo "  ./scripts/start_all.sh"
    exit 0
fi

if [ "$NO_PM2" = false ]; then
    echo ""
    echo "Starting services via PM2..."

    # Check ecosystem config
    if [ ! -f "ecosystem.config.js" ]; then
        echo -e "${RED}Error: ecosystem.config.js not found${NC}"
        exit 1
    fi

    # Stop existing instances
    pm2 stop ecosystem.config.js 2>/dev/null || true
    pm2 delete ecosystem.config.js 2>/dev/null || true
    sleep 2

    # Start all services
    pm2 start ecosystem.config.js
    sleep 3

    # Show status
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Service Status${NC}"
    echo -e "${BLUE}========================================${NC}"
    pm2 list

    echo ""
    echo "========================================"
    echo "  Next Steps"
    echo "========================================"
    echo ""
    echo -e "${GREEN}✓ All services started via PM2${NC}"
    echo ""
    echo "Monitor:    pm2 monit"
    echo "Logs:       pm2 logs"
    echo "Status:     pm2 list"
    echo "Restart:    pm2 restart ai-orchestrator"
    echo "Stop:       ./scripts/stop_all.sh"
    echo ""
    echo "Save for boot:"
    echo "  pm2 save && pm2 startup"
    echo ""
else
    echo ""
    echo -e "${YELLOW}Direct process mode (no PM2)${NC}"
    echo ""
    echo "To run the orchestrator in the foreground:"
    echo "  .venv/bin/python orchestrator.py --vault ./vault --dry-run"
    echo ""
    echo "To run watchers in the background:"
    echo "  nohup .venv/bin/python watchers/filesystem_watcher.py --vault ./vault --drop-dir ./drop &"
    echo "  nohup .venv/bin/python watchers/gmail_watcher.py --vault ./vault &"
    echo ""
    echo "To set up cron-based scheduling:"
    echo "  ./scripts/setup_cron.sh"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  AI Employee Ready${NC}"
echo -e "${GREEN}========================================${NC}"
