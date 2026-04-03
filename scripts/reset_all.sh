#!/bin/bash
# Reset — Clean State Management
#
# Resets the AI Employee to a clean state:
# - Moves In_Progress items back to Needs_Action
# - Clears old logs (older than 7 days)
# - Optionally clears Done, Rejected, Plans, Briefings
# - Does NOT touch Approved or Pending_Approval (requires manual action)
#
# Usage: ./scripts/reset_all.sh [--all] [--dry-run]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VAULT_PATH="${PROJECT_ROOT}/vault"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Personal AI Employee — Reset${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Parse flags
RESET_ALL=false
DRY_RUN=false
if [[ "$1" == "--all" ]]; then RESET_ALL=true; fi
if [[ "$1" == "--dry-run" ]] || [[ "$2" == "--dry-run" ]]; then DRY_RUN=true; fi

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}DRY RUN — showing what would be reset${NC}"
    echo ""
fi

ACTIONS=0

# ---- 1. In_Progress → Needs_Action ----
echo -e "${BLUE}── 1. In_Progress → Needs_Action ──${NC}"
in_progress_count=$(find "$VAULT_PATH/In_Progress" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
if [ "$in_progress_count" -gt 0 ]; then
    echo "  $in_progress_count item(s) in In_Progress"
    if [ "$DRY_RUN" = false ]; then
        for f in "$VAULT_PATH/In_Progress"/*.md; do
            mv "$f" "$VAULT_PATH/Needs_Action/"
            echo "    Moved: $(basename "$f")"
        done
    fi
    ACTIONS=$((ACTIONS + in_progress_count))
else
    echo "  Empty — nothing to move"
fi

# ---- 2. Clear old logs (older than 7 days) ----
echo ""
echo -e "${BLUE}── 2. Old Logs (>7 days) ──${NC}"
old_logs=$(find "$VAULT_PATH/Logs" -maxdepth 1 -name "*.json" -mtime +7 2>/dev/null | wc -l)
if [ "$old_logs" -gt 0 ]; then
    echo "  $old_logs old log file(s)"
    if [ "$DRY_RUN" = false ]; then
        find "$VAULT_PATH/Logs" -maxdepth 1 -name "*.json" -mtime +7 -delete
        echo "    Deleted $old_logs file(s)"
    fi
else
    echo "  No old logs to clean"
fi

# ---- 3. Clear Ralph loop logs (older than 3 days) ----
echo ""
echo -e "${BLUE}── 3. Ralph Loop Logs (>3 days) ──${NC}"
ralph_logs=$(find "$VAULT_PATH/Logs/ralph_loop" -maxdepth 1 -name "*.json" -mtime +3 2>/dev/null | wc -l)
if [ "$ralph_logs" -gt 0 ]; then
    echo "  $ralph_logs old Ralph loop log(s)"
    if [ "$DRY_RUN" = false ]; then
        find "$VAULT_PATH/Logs/ralph_loop" -maxdepth 1 -name "*.json" -mtime +3 -delete
        echo "    Deleted $ralph_logs file(s)"
    fi
else
    echo "  No old Ralph loop logs"
fi

# ---- 4. Clear PM2 logs (older than 3 days, >50MB files) ----
echo ""
echo -e "${BLUE}── 4. PM2 Log Rotation ──${NC}"
if [ -d "$PROJECT_ROOT/logs/pm2" ]; then
    large_logs=$(find "$PROJECT_ROOT/logs/pm2" -name "*.log" -size +50M 2>/dev/null | wc -l)
    if [ "$large_logs" -gt 0 ]; then
        echo "  $large_logs large PM2 log file(s) (>50MB)"
        if [ "$DRY_RUN" = false ]; then
            find "$PROJECT_ROOT/logs/pm2" -name "*.log" -size +50M -delete
            echo "    Truncated $large_logs file(s)"
        fi
    else
        echo "  No oversized PM2 logs"
    fi
fi

# ---- 5. Optional: Clear Done/Rejected/Plans/Briefings ----
if [ "$RESET_ALL" = true ]; then
    echo ""
    echo -e "${YELLOW}── 5. Full Reset (--all) ──${NC}"

    for dir in Done Rejected Plans Briefings; do
        count=$(find "$VAULT_PATH/$dir" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
        if [ "$count" -gt 0 ]; then
            echo "  Clearing $dir: $count file(s)"
            if [ "$DRY_RUN" = false ]; then
                find "$VAULT_PATH/$dir" -maxdepth 1 -name "*.md" -delete
                echo "    Deleted $count file(s)"
            fi
            ACTIONS=$((ACTIONS + count))
        else
            echo "  $dir: empty"
        fi
    done
fi

# ---- Summary ----
echo ""
echo "========================================"
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}  DRY RUN — $ACTIONS action(s) would be taken${NC}"
    echo ""
    echo "To execute:"
    echo "  ./scripts/reset_all.sh"
    echo ""
    echo "To full reset (clears Done/Plans/etc):"
    echo "  ./scripts/reset_all.sh --all"
else
    echo -e "${GREEN}  Reset complete — $ACTIONS action(s) taken${NC}"
    echo ""
    echo "Current state:"
    for dir in Needs_Action In_Progress Pending_Approval Approved Done Plans; do
        count=$(find "$VAULT_PATH/$dir" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
        printf "  %-20s %d file(s)\n" "$dir" "$count"
    done
fi
echo ""
echo -e "${BLUE}========================================${NC}"
