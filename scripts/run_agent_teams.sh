#!/bin/bash
#
# Run Agent Teams for Silver and Gold Tier Completion
#
# This script launches all specialized agents to complete Silver and Gold tier requirements.
# Each agent works on their domain of expertise while coordinating through the vault structure.
#

set -e

# Configuration
VAULT_PATH="${VAULT_PATH:-./vault}"
DRY_RUN="${DRY_RUN:-true}"
LOG_DIR="$VAULT_PATH/Logs"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log function
log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}"
}

# Print header
print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}  Personal AI Employee - Agent Teams${NC}"
    echo -e "${BLUE}  Silver & Gold Tier Completion${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

# Print usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --vault PATH       Path to vault directory (default: ./vault)"
    echo "  --live             Run in live mode (not dry run)"
    echo "  --email            Run Email Specialist agent"
    echo "  --social           Run Social Media Manager agent"
    echo "  --accounting       Run Accounting Specialist agent"
    echo "  --all              Run all agents (default)"
    echo "  --list-tasks       List tasks without processing"
    echo "  --report           Generate completion report"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --all                    # Run all agents in dry-run mode"
    echo "  $0 --all --live             # Run all agents in live mode"
    echo "  $0 --email --report         # Process emails and generate report"
    echo "  $0 --list-tasks             # List all available tasks"
    echo ""
}

# Parse arguments
RUN_EMAIL=false
RUN_SOCIAL=false
RUN_ACCOUNTING=false
RUN_ALL=false
LIST_TASKS=false
GENERATE_REPORT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --vault)
            VAULT_PATH="$2"
            shift 2
            ;;
        --live)
            DRY_RUN=false
            shift
            ;;
        --email)
            RUN_EMAIL=true
            shift
            ;;
        --social)
            RUN_SOCIAL=true
            shift
            ;;
        --accounting)
            RUN_ACCOUNTING=true
            shift
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        --list-tasks)
            LIST_TASKS=true
            shift
            ;;
        --report)
            GENERATE_REPORT=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Default to running all if nothing specified
if ! $RUN_EMAIL && ! $RUN_SOCIAL && ! $RUN_ACCOUNTING && ! $RUN_ALL && ! $LIST_TASKS; then
    RUN_ALL=true
fi

# Set dry-run flag for Python scripts
DRY_RUN_FLAG=""
if $DRY_RUN; then
    DRY_RUN_FLAG="--dry-run"
    log "INFO" "${YELLOW}Running in DRY-RUN mode (no actual actions)${NC}"
else
    DRY_RUN_FLAG="--no-dry-run"
    log "INFO" "${GREEN}Running in LIVE mode (actual actions will be taken)${NC}"
fi

# Print configuration
print_header
log "INFO" "Vault Path: $VAULT_PATH"
log "INFO" "Log Directory: $LOG_DIR"
log "INFO" "Dry Run: $DRY_RUN"
echo ""

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    log "INFO" "Activating virtual environment..."
    source .venv/bin/activate
fi

# List tasks mode
if $LIST_TASKS; then
    log "INFO" "Listing available tasks..."
    echo ""
    
    echo -e "${BLUE}=== Silver Tier Tasks ===${NC}"
    echo ""
    
    echo -e "${YELLOW}Email Tasks:${NC}"
    find "$VAULT_PATH/Needs_Action" -name "EMAIL_*.md" 2>/dev/null | while read file; do
        echo "  - $(basename "$file")"
    done
    
    echo ""
    echo -e "${YELLOW}Social Media Tasks:${NC}"
    find "$VAULT_PATH/Needs_Action" -name "SOCIAL_*.md" -o -name "*linkedin*.md" -o -name "*twitter*.md" 2>/dev/null | while read file; do
        echo "  - $(basename "$file")"
    done
    
    echo ""
    echo -e "${BLUE}=== Gold Tier Tasks ===${NC}"
    echo ""
    
    echo -e "${YELLOW}Accounting Tasks:${NC}"
    find "$VAULT_PATH/Needs_Action" -name "INVOICE_*.md" 2>/dev/null | while read file; do
        echo "  - $(basename "$file")"
    done
    
    echo ""
    echo -e "${YELLOW}Research Tasks:${NC}"
    find "$VAULT_PATH/Needs_Action" -name "RESEARCH_*.md" 2>/dev/null | while read file; do
        echo "  - $(basename "$file")"
    done
    
    echo ""
    exit 0
fi

# Run Email Specialist
if $RUN_ALL || $RUN_EMAIL; then
    log "INFO" "${BLUE}Starting Email Specialist Agent...${NC}"
    echo ""
    
    python3 "$SCRIPT_DIR/agents/email_specialist.py" \
        --vault "$VAULT_PATH" \
        $DRY_RUN_FLAG \
        ${GENERATE_REPORT:+--report}
    
    echo ""
    log "INFO" "${GREEN}Email Specialist completed${NC}"
    echo ""
fi

# Run Social Media Manager
if $RUN_ALL || $RUN_SOCIAL; then
    log "INFO" "${BLUE}Starting Social Media Manager Agent...${NC}"
    echo ""
    
    python3 "$SCRIPT_DIR/agents/social_media_manager.py" \
        --vault "$VAULT_PATH" \
        $DRY_RUN_FLAG \
        ${GENERATE_REPORT:+--report}
    
    echo ""
    log "INFO" "${GREEN}Social Media Manager completed${NC}"
    echo ""
fi

# Run Accounting Specialist
if $RUN_ALL || $RUN_ACCOUNTING; then
    log "INFO" "${BLUE}Starting Accounting Specialist Agent...${NC}"
    echo ""
    
    python3 "$SCRIPT_DIR/agents/accounting_specialist.py" \
        --vault "$VAULT_PATH" \
        $DRY_RUN_FLAG \
        ${GENERATE_REPORT:+--report}
    
    echo ""
    log "INFO" "${GREEN}Accounting Specialist completed${NC}"
    echo ""
fi

# Generate summary report
if $GENERATE_REPORT; then
    log "INFO" "${BLUE}Generating completion report...${NC}"
    
    python3 "$SCRIPT_DIR/complete_silver_gold_tiers.py" \
        --vault "$VAULT_PATH" \
        $DRY_RUN_FLAG \
        --report
    
    echo ""
    log "INFO" "${GREEN}Completion report generated${NC}"
fi

# Print summary
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}  Agent Teams Execution Complete!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

if $DRY_RUN; then
    echo -e "${YELLOW}⚠️  This was a DRY RUN - no actual actions were taken${NC}"
    echo ""
    echo "To run in LIVE mode (actual actions):"
    echo "  $0 --all --live"
else
    echo -e "${GREEN}✅ Live mode - all actions were executed${NC}"
fi

echo ""
echo "Check the logs for details:"
echo "  - Email: $LOG_DIR/email_specialist.log"
echo "  - Social: $LOG_DIR/social_media_manager.log"
echo "  - Accounting: $LOG_DIR/accounting_specialist.log"
echo ""

# Show recent reports
echo "Generated Reports:"
find "$LOG_DIR" -name "*report_*.md" -type f -mmin -60 2>/dev/null | while read file; do
    echo "  - $file"
done
echo ""
